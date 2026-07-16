"""Stage 2 — observe-mode gateway server tests.

An in-process mock upstream stands in for an OpenAI-compatible provider. We
prove the observe invariants offline: byte-faithful request pass-through,
identical non-streaming response bytes, ordered/faithful SSE streaming, tool-call
fidelity, shadow-router recording, and the security guards (auth, size cap,
recursive-loop, secret redaction).
"""
from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from piensalo.gateway.config import GatewayConfig
from piensalo.gateway.ledger import EventLedger
from piensalo.gateway.server import GatewayServer

# --- mock upstream ----------------------------------------------------------

# A canned non-streaming completion, with a tool call, to test tool fidelity.
_JSON_RESPONSE = {
    "id": "chatcmpl-mock",
    "object": "chat.completion",
    "model": "mock/model-1",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "hello from upstream",
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {"name": "get_weather", "arguments": '{"city":"SF"}'},
                    }
                ],
            },
            "finish_reason": "tool_calls",
        }
    ],
    "usage": {"prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18},
}

# An SSE stream with two content deltas then a tool-call delta then DONE.
_SSE_EVENTS = [
    'data: {"id":"c","model":"mock/model-1","choices":[{"index":0,"delta":{"role":"assistant","content":"Hel"}}]}\n\n',
    'data: {"id":"c","model":"mock/model-1","choices":[{"index":0,"delta":{"content":"lo"}}]}\n\n',
    'data: {"id":"c","model":"mock/model-1","choices":[{"index":0,"delta":{"tool_calls":[{"index":0,"id":"call_9","function":{"name":"do","arguments":"{}"}}]}}]}\n\n',
    'data: {"id":"c","model":"mock/model-1","choices":[{"index":0,"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":5,"completion_tokens":3}}\n\n',
    "data: [DONE]\n\n",
]
_SSE_BYTES = "".join(_SSE_EVENTS).encode("utf-8")

_UPSTREAM_STATE: dict = {}


class MockUpstream(BaseHTTPRequestHandler):
    def log_message(self, *a):
        return

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", 0) or 0)
        body = self.rfile.read(length) if length else b""
        _UPSTREAM_STATE["last_body"] = body
        _UPSTREAM_STATE["last_headers"] = {k: v for k, v in self.headers.items()}
        try:
            data = json.loads(body.decode("utf-8"))
        except ValueError:
            data = {}
        if data.get("stream"):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Connection", "close")
            self.end_headers()
            for evt in _SSE_EVENTS:
                self.wfile.write(evt.encode("utf-8"))
                self.wfile.flush()
            return
        payload = json.dumps(_JSON_RESPONSE).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture
def stack(tmp_path):
    """Start a mock upstream + a gateway pointed at it. Yields (base_url, cfg)."""
    up_port = _free_port()
    upstream = ThreadingHTTPServer(("127.0.0.1", up_port), MockUpstream)
    up_thread = threading.Thread(target=upstream.serve_forever, daemon=True)
    up_thread.start()

    gw_port = _free_port()
    cfg = GatewayConfig.build(
        bind_port=gw_port,
        upstream_base_url=f"http://127.0.0.1:{up_port}/v1",
        upstream_model="mock/model-1",
        ledger_dir=str(tmp_path / "gw"),
    )
    gw = GatewayServer(cfg)
    gw_thread = threading.Thread(target=gw.serve_forever, daemon=True)
    gw_thread.start()

    yield f"http://127.0.0.1:{gw_port}", cfg

    gw.shutdown()
    gw.server_close()
    upstream.shutdown()
    upstream.server_close()


def _post(base_url, body: dict, headers=None, path="/v1/chat/completions"):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        base_url + path, data=data, headers=headers or {"Content-Type": "application/json"},
        method="POST",
    )
    resp = urllib.request.urlopen(req, timeout=10)
    return resp.status, resp.read(), dict(resp.headers)


# --- tests ------------------------------------------------------------------


def test_non_stream_response_is_byte_identical(stack):
    base, cfg = stack
    status, body, _ = _post(base, {"model": "mock/model-1", "messages": [{"role": "user", "content": "hi"}]})
    assert status == 200
    # The client receives exactly the upstream's bytes.
    assert body == json.dumps(_JSON_RESPONSE).encode("utf-8")


def test_request_body_reaches_upstream_verbatim(stack):
    base, cfg = stack
    sent = {"model": "mock/model-1", "messages": [{"role": "user", "content": "exact bytes 123"}],
            "temperature": 0.3}
    _post(base, sent)
    # Upstream saw the identical body bytes the client sent (no re-serialization).
    assert _UPSTREAM_STATE["last_body"] == json.dumps(sent).encode("utf-8")


def test_ledger_records_metadata_and_shadow_router(stack):
    base, cfg = stack
    _post(base, {"model": "mock/model-1", "messages": [{"role": "user", "content": "hi"}]})
    events = EventLedger(cfg.ledger_dir).read_all()
    assert len(events) == 1
    ev = events[0]
    assert ev["requested_model"] == "mock/model-1"
    assert ev["resolved_model"] == "mock/model-1"
    assert ev["model_tokens_in"] == 11 and ev["model_tokens_out"] == 7
    assert ev["model_tokens_measured"] is True
    assert ev["router_decision"] == "PASS_THROUGH"  # trivial request
    assert ev["cortex_operations_activated"] == []  # observe never activates cortex
    assert ev["additional_cortex_tokens"] == 0
    assert ev["verification_level"] == "NOT_RUN"
    # Cortex Vault seams exist but observe mode is read-only w.r.t. durable
    # memory: it never reads or proposes memory writes.
    assert ev["memory_refs_read"] == []
    assert ev["memory_updates_proposed"] == []


def test_tool_call_fidelity_non_stream(stack):
    base, cfg = stack
    _post(base, {"model": "mock/model-1", "messages": [{"role": "user", "content": "weather?"}]})
    ev = EventLedger(cfg.ledger_dir).read_all()[0]
    assert ev["tool_calls"] == 1  # the upstream tool call was observed


def test_streaming_is_ordered_and_faithful(stack):
    base, cfg = stack
    status, body, headers = _post(
        base, {"model": "mock/model-1", "stream": True, "messages": [{"role": "user", "content": "hi"}]}
    )
    assert status == 200
    # Aggregate SSE payload is byte-identical and events are in order.
    assert body == _SSE_BYTES
    assert body.index(b"Hel") < body.index(b"lo") < body.index(b"[DONE]")
    ev = EventLedger(cfg.ledger_dir).read_all()[0]
    assert ev["streamed"] is True
    assert ev["tool_calls"] == 1  # streamed tool-call delta reassembled
    assert ev["resolved_model"] == "mock/model-1"


def test_shadow_router_decides_check_without_intervening(stack):
    base, cfg = stack
    # A request with several deterministic requirements should be shadow-flagged.
    content = "Return JSON. It must include name. Output exactly this format. Only return the table."
    status, body, _ = _post(
        base, {"model": "mock/model-1", "messages": [{"role": "user", "content": content}]}
    )
    # Response is still the untouched upstream body (shadow = no intervention).
    assert body == json.dumps(_JSON_RESPONSE).encode("utf-8")
    ev = EventLedger(cfg.ledger_dir).read_all()[0]
    assert "CHECK" in ev["router_decision"]
    assert ev["router_reasons"]


def test_auth_required_when_configured(tmp_path):
    up_port = _free_port()
    upstream = ThreadingHTTPServer(("127.0.0.1", up_port), MockUpstream)
    threading.Thread(target=upstream.serve_forever, daemon=True).start()
    gw_port = _free_port()
    cfg = GatewayConfig.build(
        bind_port=gw_port,
        upstream_base_url=f"http://127.0.0.1:{up_port}/v1",
        auth_token="s3cret",
        ledger_dir=str(tmp_path / "gw"),
    )
    gw = GatewayServer(cfg)
    threading.Thread(target=gw.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{gw_port}"
    try:
        # No token -> 401.
        with pytest.raises(urllib.error.HTTPError) as e:
            _post(base, {"model": "m", "messages": []})
        assert e.value.code == 401
        # Correct token -> 200.
        status, body, _ = _post(
            base, {"model": "mock/model-1", "messages": [{"role": "user", "content": "hi"}]},
            headers={"Content-Type": "application/json", "Authorization": "Bearer s3cret"},
        )
        assert status == 200
    finally:
        gw.shutdown(); gw.server_close(); upstream.shutdown(); upstream.server_close()


def test_body_size_cap(stack):
    base, cfg = stack
    cfg.max_body_bytes = 50  # tighten at runtime for the test
    big = {"model": "m", "messages": [{"role": "user", "content": "x" * 500}]}
    with pytest.raises(urllib.error.HTTPError) as e:
        _post(base, big)
    assert e.value.code == 413


def test_recursive_loop_guard(stack):
    base, cfg = stack
    with pytest.raises(urllib.error.HTTPError) as e:
        _post(base, {"model": "m", "messages": []},
              headers={"Content-Type": "application/json", "X-Piensalo-Gateway": "observe"})
    assert e.value.code == 508


def test_secrets_never_written_to_ledger(stack):
    base, cfg = stack
    _post(
        base, {"model": "mock/model-1", "messages": [{"role": "user", "content": "hi"}]},
        headers={"Content-Type": "application/json", "Authorization": "Bearer sk-super-secret-value"},
    )
    ledger_text = EventLedger(cfg.ledger_dir).path.read_text()
    assert "sk-super-secret-value" not in ledger_text
    assert "<redacted>" in ledger_text


def test_upstream_error_is_relayed_and_recorded(tmp_path):
    # Point the gateway at a resolvable-but-dead port to force a 502.
    dead_port = _free_port()  # nothing listening here
    gw_port = _free_port()
    cfg = GatewayConfig.build(
        bind_port=gw_port,
        upstream_base_url=f"http://127.0.0.1:{dead_port}/v1",
        ledger_dir=str(tmp_path / "gw"),
    )
    gw = GatewayServer(cfg)
    threading.Thread(target=gw.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{gw_port}"
    try:
        with pytest.raises(urllib.error.HTTPError) as e:
            _post(base, {"model": "m", "messages": [{"role": "user", "content": "hi"}]})
        assert e.value.code == 502
        ev = EventLedger(cfg.ledger_dir).read_all()[0]
        assert ev["status"] == "upstream_error"
    finally:
        gw.shutdown(); gw.server_close()
