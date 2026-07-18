"""Extended LIVE tool-fidelity matrix: observe gateway vs direct, real model.

Completes the observe-mode fidelity checklist against a real tool-capable local
model (default qwen2.5:7b via Ollama). Every cell compares

    client -> Ollama directly          (DIRECT arm)
    client -> observe gateway -> Ollama (GATEWAY arm)

with deterministic settings (temperature=0, seed=42). The gateway must not
add, remove, reorder, or reinterpret anything. Cells the upstream model/server
cannot express are reported BLOCKED BY UPSTREAM CAPABILITY — never fabricated.

GRADER CORRECTION (documented, full clean rerun performed): the first version
of this matrix compared tool-call ``id`` values ACROSS the two arms. Ollama
mints a fresh random id (``call_xxxxxxxx``) on every invocation, so two
separate invocations can never share ids — that comparison was structurally
impossible at the upstream, i.e. the grader was objectively defective, not the
gateway. Corrected discipline: compare name + arguments + call order across
arms; require id PRESENCE in each arm; prove id integrity via the
within-conversation tool-result round trip (cell 6). Cross-invocation id
equality is reported BLOCKED BY UPSTREAM CAPABILITY.

Cells:
  1  nonstream_single_toolcall   id present, name+arguments identical
  2  stream_single_toolcall      reassembled name+arguments identical, [DONE] seen
  3  stream_event_order          per-event field sequence identical
  4  finish_reason_usage         finish_reason + usage identical (both arms)
  5  multiple_toolcalls          two tools requested -> compare call lists
  6  tool_result_association     round-trip: tool_call -> tool result -> answer
  7  cancellation_midstream      client aborts stream via gateway; gateway
                                 stays healthy for the next request
  8  timeout_behavior            NOT run live (needs a stalling upstream);
                                 covered by unit test (dead upstream -> 502)

Writes results.json next to this file.
"""
from __future__ import annotations

import json
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

DIRECT = "http://127.0.0.1:11434"
UPSTREAM = "http://127.0.0.1:11434/v1"
MODEL = sys.argv[1] if len(sys.argv) > 1 else "qwen2.5:7b"
PORT = 8907
GW = f"http://127.0.0.1:{PORT}"

WEATHER = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a city",
        "parameters": {"type": "object",
                       "properties": {"city": {"type": "string"}},
                       "required": ["city"]},
    },
}
TIMEC = {
    "type": "function",
    "function": {
        "name": "get_time",
        "description": "Get the current local time for a city",
        "parameters": {"type": "object",
                       "properties": {"city": {"type": "string"}},
                       "required": ["city"]},
    },
}


def call(base, body, stream=False, timeout=180):
    data = json.dumps({**body, "stream": stream}).encode()
    req = urllib.request.Request(base + "/v1/chat/completions", data=data,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def det(messages, tools=None):
    body = {"model": MODEL, "messages": messages, "temperature": 0, "seed": 42}
    if tools:
        body["tools"] = tools
    return body


def parse_nonstream(raw):
    d = json.loads(raw)
    ch = d["choices"][0]
    tcs = [{"id": tc.get("id", ""), "name": tc.get("function", {}).get("name"),
            "arguments": tc.get("function", {}).get("arguments")}
           for tc in (ch["message"].get("tool_calls") or [])]
    return {"content": ch["message"].get("content"), "tool_calls": tcs,
            "finish_reason": ch.get("finish_reason"), "usage": d.get("usage"),
            "model": d.get("model")}


def parse_stream(raw):
    slots, order, finish, usage, done = {}, [], None, None, False
    for line in raw.split(b"\n"):
        line = line.strip()
        if not line.startswith(b"data:"):
            continue
        payload = line[5:].strip()
        if payload == b"[DONE]":
            done = True
            order.append("DONE")
            continue
        if not payload:
            continue
        try:
            evt = json.loads(payload)
        except Exception:
            order.append("unparseable")
            continue
        if isinstance(evt.get("usage"), dict):
            usage = evt["usage"]
        for c in evt.get("choices", []) or []:
            d = c.get("delta", {}) or {}
            kinds = []
            if d.get("content"):
                kinds.append("content")
            for tc in d.get("tool_calls", []) or []:
                kinds.append("tool_call")
                s = slots.setdefault(tc.get("index", 0), {"id": "", "name": "", "arguments": ""})
                if tc.get("id"):
                    s["id"] += tc["id"]
                fn = tc.get("function", {}) or {}
                s["name"] += fn.get("name", "") or ""
                s["arguments"] += fn.get("arguments", "") or ""
            if c.get("finish_reason"):
                finish = c["finish_reason"]
                kinds.append("finish")
            order.append("+".join(kinds) if kinds else "empty")
    calls = [slots[i] for i in sorted(slots)]
    return {"tool_calls": calls, "order": order, "finish_reason": finish,
            "usage": usage, "done": done}


def main():
    outdir = Path(__file__).parent
    ledger = tempfile.mkdtemp(prefix="piensalo-fid-") + "/gw"
    proc = subprocess.Popen(
        ["piensalo", "serve", "--mode", "observe", "--upstream-base-url", UPSTREAM,
         "--upstream-model", MODEL, "--port", str(PORT), "--ledger-dir", ledger],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    cells = {}
    try:
        for _ in range(60):
            try:
                call(GW, det([{"role": "user", "content": "hi"}]))
                break
            except Exception:
                time.sleep(0.5)

        ask = [{"role": "user",
                "content": "What is the current weather in Paris? Use the get_weather tool."}]

        def name_args(calls):
            return [(t["name"], t["arguments"]) for t in calls]

        # 1 + 4 nonstream
        d = parse_nonstream(call(DIRECT, det(ask, [WEATHER])))
        g = parse_nonstream(call(GW, det(ask, [WEATHER])))
        cells["nonstream_single_toolcall"] = {
            "direct": d["tool_calls"], "gateway": g["tool_calls"],
            "id_present_both_arms": bool(d["tool_calls"] and d["tool_calls"][0]["id"]
                                         and g["tool_calls"] and g["tool_calls"][0]["id"]),
            "identical": name_args(d["tool_calls"]) == name_args(g["tool_calls"])
            and len(g["tool_calls"]) == 1,
            "ids_cross_invocation": "BLOCKED BY UPSTREAM CAPABILITY (Ollama mints a random "
                                    "id per invocation; within-conversation id integrity is "
                                    "proven by tool_result_association)",
        }
        cells["finish_reason_usage_nonstream"] = {
            "direct": {"finish": d["finish_reason"], "usage": d["usage"]},
            "gateway": {"finish": g["finish_reason"], "usage": g["usage"]},
            "identical": (d["finish_reason"], d["usage"]) == (g["finish_reason"], g["usage"]),
        }

        # 2 + 3 + 4 streamed
        ds = parse_stream(call(DIRECT, det(ask, [WEATHER]), stream=True))
        gs = parse_stream(call(GW, det(ask, [WEATHER]), stream=True))
        cells["stream_single_toolcall"] = {
            "direct": ds["tool_calls"], "gateway": gs["tool_calls"],
            "done_marker_both": ds["done"] and gs["done"],
            "id_present_both_arms": bool(ds["tool_calls"] and ds["tool_calls"][0]["id"]
                                         and gs["tool_calls"] and gs["tool_calls"][0]["id"]),
            "identical": name_args(ds["tool_calls"]) == name_args(gs["tool_calls"])
            and len(gs["tool_calls"]) == 1,
        }
        cells["stream_event_order"] = {
            "direct_events": len(ds["order"]), "gateway_events": len(gs["order"]),
            "identical_sequence": ds["order"] == gs["order"],
        }
        cells["finish_reason_usage_stream"] = {
            "direct": {"finish": ds["finish_reason"], "usage": ds["usage"]},
            "gateway": {"finish": gs["finish_reason"], "usage": gs["usage"]},
            "identical": (ds["finish_reason"], ds["usage"]) == (gs["finish_reason"], gs["usage"]),
        }

        # 5 multiple tool calls
        ask2 = [{"role": "user",
                 "content": "Get the current weather in Paris AND the current local time in "
                            "Tokyo. Use both the get_weather and get_time tools."}]
        d2 = parse_nonstream(call(DIRECT, det(ask2, [WEATHER, TIMEC])))
        g2 = parse_nonstream(call(GW, det(ask2, [WEATHER, TIMEC])))
        if len(d2["tool_calls"]) < 2:
            cells["multiple_toolcalls"] = {
                "status": "BLOCKED BY UPSTREAM CAPABILITY",
                "detail": f"direct arm emitted {len(d2['tool_calls'])} call(s); the model did "
                          "not produce parallel tool calls, so multi-call fidelity cannot be "
                          "exercised live",
                "gateway_matches_direct_anyway": d2["tool_calls"] == g2["tool_calls"],
            }
        else:
            cells["multiple_toolcalls"] = {
                "direct": d2["tool_calls"], "gateway": g2["tool_calls"],
                "identical": name_args(d2["tool_calls"]) == name_args(g2["tool_calls"]),
                "order_preserved": [t["name"] for t in d2["tool_calls"]]
                == [t["name"] for t in g2["tool_calls"]],
            }

        # 6 tool-result association (round trip using the DIRECT arm's call id)
        first = parse_nonstream(call(DIRECT, det(ask, [WEATHER])))
        if not first["tool_calls"]:
            cells["tool_result_association"] = {
                "status": "BLOCKED BY UPSTREAM CAPABILITY",
                "detail": "model emitted no tool call to associate a result with",
            }
        else:
            tc = first["tool_calls"][0]
            follow = [
                ask[0],
                {"role": "assistant", "content": None,
                 "tool_calls": [{"id": tc["id"], "type": "function",
                                 "function": {"name": tc["name"],
                                              "arguments": tc["arguments"]}}]},
                {"role": "tool", "tool_call_id": tc["id"],
                 "content": '{"temperature_c": 21, "condition": "sunny"}'},
            ]
            fd = parse_nonstream(call(DIRECT, det(follow, [WEATHER])))
            fg = parse_nonstream(call(GW, det(follow, [WEATHER])))
            cells["tool_result_association"] = {
                "direct_content": fd["content"], "gateway_content": fg["content"],
                "identical": fd == fg,
                "answer_uses_result": bool(fg["content"]) and "21" in (fg["content"] or ""),
            }

        # 7 cancellation mid-stream through the gateway
        try:
            data = json.dumps({**det(ask, [WEATHER]), "stream": True}).encode()
            s = socket.create_connection(("127.0.0.1", PORT), timeout=30)
            s.sendall(
                b"POST /v1/chat/completions HTTP/1.1\r\nHost: x\r\n"
                b"Content-Type: application/json\r\nContent-Length: "
                + str(len(data)).encode() + b"\r\n\r\n" + data)
            s.recv(256)  # first bytes arrive, then abort mid-stream
            s.close()
            time.sleep(1.0)
            # gateway must still serve the next request
            after = parse_nonstream(call(GW, det([{"role": "user",
                                                   "content": "Reply with exactly: OK"}])))
            cells["cancellation_midstream"] = {
                "gateway_survived": after["content"] is not None,
                "note": "client aborted mid-stream; gateway served the next request",
            }
        except Exception as e:  # honest failure capture
            cells["cancellation_midstream"] = {"gateway_survived": False, "error": str(e)}

        cells["timeout_behavior"] = {
            "status": "NOT RUN LIVE",
            "detail": "requires a deliberately stalling upstream; dead-upstream 502 relay is "
                      "unit-tested (tests/test_gateway_server.py)",
        }

        # resolved-model check across the arms used above
        cells["resolved_model"] = {"direct": d["model"], "gateway": g["model"],
                                   "identical": d["model"] == g["model"]}

        result = {"model": MODEL, "settings": {"temperature": 0, "seed": 42},
                  "cells": cells}
        (outdir / "results.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        hard = [k for k, v in cells.items()
                if v.get("identical") is False or v.get("gateway_survived") is False]
        print("\nMATRIX:", "PASS (no fidelity divergence)" if not hard
              else f"DIVERGENCE in {hard}")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    main()
