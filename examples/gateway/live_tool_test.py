"""Reproducible LIVE test: STREAMED tool-call fidelity through the observe gateway.

Proves the gateway preserves tool-call names/arguments both non-stream and —
crucially — reassembled from an SSE stream, matching a direct call, against a
real tool-capable provider. This is the harness behind the "tool-call fidelity:
LIVE TESTED" claim in docs/gateway/PROTOCOLS.md.

Prerequisites (Ollama example, a tool-capable model):
    ollama pull qwen2.5:7b

Run:
    python examples/gateway/live_tool_test.py
    python examples/gateway/live_tool_test.py --model llama3.1:8b
"""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
import time
import urllib.request

TOOLS = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a city",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "City name"}},
            "required": ["city"],
        },
    },
}]


def call(base, body, stream=False, timeout=120):
    data = json.dumps({**body, "stream": stream}).encode()
    req = urllib.request.Request(base + "/v1/chat/completions", data=data,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def toolcalls_nonstream(raw):
    msg = json.loads(raw)["choices"][0]["message"]
    return [{"name": tc.get("function", {}).get("name"),
             "arguments": tc.get("function", {}).get("arguments")}
            for tc in (msg.get("tool_calls") or [])]


def toolcalls_from_stream(raw):
    slots = {}
    for line in raw.split(b"\n"):
        line = line.strip()
        if not line.startswith(b"data:"):
            continue
        payload = line[5:].strip()
        if payload in (b"[DONE]", b""):
            continue
        try:
            evt = json.loads(payload)
        except Exception:
            continue
        for choice in evt.get("choices", []) or []:
            for tc in (choice.get("delta", {}) or {}).get("tool_calls", []) or []:
                s = slots.setdefault(tc.get("index", 0), {"name": "", "arguments": ""})
                fn = tc.get("function", {}) or {}
                s["name"] += fn.get("name", "") or ""
                s["arguments"] += fn.get("arguments", "") or ""
    return [{"name": slots[i]["name"], "arguments": slots[i]["arguments"]} for i in sorted(slots)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--direct", default="http://127.0.0.1:11434")
    ap.add_argument("--upstream", default="http://127.0.0.1:11434/v1")
    ap.add_argument("--model", default="qwen2.5:7b")
    ap.add_argument("--port", type=int, default=8905)
    args = ap.parse_args()

    gw = f"http://127.0.0.1:{args.port}"
    ledger = tempfile.mkdtemp(prefix="piensalo-tool-") + "/gw"
    req = {"model": args.model,
           "messages": [{"role": "user",
                         "content": "What is the current weather in Paris? Use the get_weather tool."}],
           "tools": TOOLS, "temperature": 0, "seed": 42}

    proc = subprocess.Popen(
        ["piensalo", "serve", "--mode", "observe", "--upstream-base-url", args.upstream,
         "--upstream-model", args.model, "--port", str(args.port), "--ledger-dir", ledger],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            try:
                call(gw, {**req, "tools": [], "messages": [{"role": "user", "content": "hi"}]})
                break
            except Exception:
                time.sleep(0.5)

        out = {}
        d_ns, g_ns = toolcalls_nonstream(call(args.direct, req)), toolcalls_nonstream(call(gw, req))
        out["nonstream_direct"] = d_ns
        out["nonstream_gateway"] = g_ns
        out["nonstream_identical"] = (d_ns == g_ns and len(g_ns) > 0)

        d_s = toolcalls_from_stream(call(args.direct, req, stream=True))
        g_s = toolcalls_from_stream(call(gw, req, stream=True))
        out["stream_direct"] = d_s
        out["stream_gateway"] = g_s
        out["provider_emits_stream_toolcall_deltas"] = len(d_s) > 0
        out["stream_identical"] = (d_s == g_s and len(g_s) > 0)

        time.sleep(0.3)
        events = [json.loads(x) for x in open(ledger + "/events.jsonl") if x.strip()]
        out["ledger_max_toolcalls_recorded"] = max((e.get("tool_calls", 0) for e in events), default=0)
        out["ledger_additional_cortex_tokens_all_zero"] = all(
            e.get("additional_cortex_tokens", 0) == 0 for e in events)

        print(json.dumps(out, indent=2))
        ok = out["nonstream_identical"] and out["ledger_additional_cortex_tokens_all_zero"]
        if out["provider_emits_stream_toolcall_deltas"]:
            ok = ok and out["stream_identical"]
            print("\nLIVE TOOL-CALL TEST:", "PASS" if ok else "FAIL",
                  "(non-stream + streamed tool-calls faithful)")
        else:
            print("\nLIVE TOOL-CALL TEST:", "PASS (non-stream)" if ok else "FAIL",
                  "— provider did not emit streamed tool-call deltas; "
                  "streamed tool-call fidelity remains mock-tested for this provider")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    main()
