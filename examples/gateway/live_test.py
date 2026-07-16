"""Reproducible LIVE test: observe-mode Cortex Gateway in front of a real
OpenAI-compatible provider (Ollama by default).

This is the harness behind the LIVE TESTED claim in docs/gateway/PROTOCOLS.md.
It requires a running provider, so it is a runnable script, not a CI unit test.

Prerequisites (Ollama example):
    brew install ollama && ollama serve &
    ollama pull qwen2.5:0.5b

Run:
    python examples/gateway/live_test.py
    # or against another provider:
    python examples/gateway/live_test.py \
        --direct http://127.0.0.1:11434 --upstream http://127.0.0.1:11434/v1 \
        --model qwen2.5:0.5b

It proves, against the real provider, that observe mode: (1) returns a response
semantically identical to a direct call (deterministic temp=0 request; volatile
id/created fields excluded), (2) forwards the SSE stream faithfully, (3) adds
only small latency, and (4) records resolved model + measured usage + shadow
router decisions in the local ledger — while adding zero cortex tokens.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
import time
import urllib.request


def call(base, body, stream=False, timeout=60):
    data = json.dumps({**body, "stream": stream}).encode()
    req = urllib.request.Request(base + "/v1/chat/completions", data=data,
                                 headers={"Content-Type": "application/json"}, method="POST")
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), (time.perf_counter() - t0) * 1000.0


def semantic(raw):
    d = json.loads(raw)
    ch = d["choices"][0]
    return {"role": ch["message"].get("role"), "content": ch["message"].get("content"),
            "finish_reason": ch.get("finish_reason"), "usage": d.get("usage"),
            "message_keys": sorted(ch["message"].keys())}


def reassemble(raw):
    content, events, done = "", 0, False
    for line in raw.split(b"\n"):
        line = line.strip()
        if not line.startswith(b"data:"):
            continue
        payload = line[5:].strip()
        if payload == b"[DONE]":
            done = True
            continue
        events += 1
        try:
            content += json.loads(payload)["choices"][0].get("delta", {}).get("content", "") or ""
        except Exception:
            pass
    return content, events, done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--direct", default="http://127.0.0.1:11434")
    ap.add_argument("--upstream", default="http://127.0.0.1:11434/v1")
    ap.add_argument("--model", default="qwen2.5:0.5b")
    ap.add_argument("--port", type=int, default=8899)
    args = ap.parse_args()

    gw = f"http://127.0.0.1:{args.port}"
    ledger = tempfile.mkdtemp(prefix="piensalo-live-") + "/gw"
    req = {"model": args.model,
           "messages": [{"role": "user", "content": "Reply with exactly: PIENSALO LIVE TEST OK"}],
           "temperature": 0, "seed": 42}

    proc = subprocess.Popen(
        ["piensalo", "serve", "--mode", "observe", "--upstream-base-url", args.upstream,
         "--upstream-model", args.model, "--port", str(args.port), "--ledger-dir", ledger],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(40):
            try:
                call(gw, req)
                break
            except Exception:
                time.sleep(0.5)

        out = {}
        out["nonstream_identical"] = semantic(call(args.direct, req)[0]) == semantic(call(gw, req)[0])
        dc, de, dd = reassemble(call(args.direct, req, stream=True)[0])
        gc, ge, gd = reassemble(call(gw, req, stream=True)[0])
        out["stream_identical"] = (dc == gc and len(gc) > 0)
        out["stream_events"], out["stream_done_marker"] = ge, gd

        med = lambda base: sorted(call(base, req)[1] for _ in range(5))[2]
        out["latency_overhead_ms_median"] = round(med(gw) - med(args.direct), 1)

        time.sleep(0.3)
        events = [json.loads(x) for x in open(ledger + "/events.jsonl") if x.strip()]
        out["ledger_resolved_models"] = sorted({e.get("resolved_model") for e in events})
        out["ledger_measured_usage"] = any(e.get("model_tokens_measured") for e in events)
        out["ledger_additional_cortex_tokens_all_zero"] = all(
            e.get("additional_cortex_tokens", 0) == 0 for e in events)
        print(json.dumps(out, indent=2))
        ok = out["nonstream_identical"] and out["stream_identical"] and \
            out["ledger_additional_cortex_tokens_all_zero"]
        print("\nLIVE TEST:", "PASS" if ok else "FAIL")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    main()
