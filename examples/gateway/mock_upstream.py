"""A tiny OpenAI-compatible mock upstream, so you can try the Cortex Gateway
with zero credentials and zero network access.

    python examples/gateway/mock_upstream.py 8991

It answers POST /v1/chat/completions with a canned completion (and a canned SSE
stream when the request sets "stream": true). It exists only for the offline
demo in this directory's README — it is not part of the shipped package.
"""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

_RESPONSE = {
    "id": "chatcmpl-demo",
    "object": "chat.completion",
    "model": "demo/model-1",
    "choices": [
        {"index": 0, "message": {"role": "assistant", "content": "Hello from the mock upstream."},
         "finish_reason": "stop"}
    ],
    "usage": {"prompt_tokens": 12, "completion_tokens": 6, "total_tokens": 18},
}

_STREAM = [
    'data: {"model":"demo/model-1","choices":[{"index":0,"delta":{"role":"assistant","content":"Hello "}}]}\n\n',
    'data: {"model":"demo/model-1","choices":[{"index":0,"delta":{"content":"streamed."}}]}\n\n',
    'data: {"model":"demo/model-1","choices":[{"index":0,"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":12,"completion_tokens":2}}\n\n',
    "data: [DONE]\n\n",
]


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        return

    def do_POST(self):  # noqa: N802
        n = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(n) if n else b""
        try:
            stream = bool(json.loads(raw.decode("utf-8")).get("stream"))
        except ValueError:
            stream = False
        if stream:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Connection", "close")
            self.end_headers()
            for evt in _STREAM:
                self.wfile.write(evt.encode("utf-8"))
                self.wfile.flush()
            return
        body = json.dumps(_RESPONSE).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8991
    print(f"mock upstream on http://127.0.0.1:{port}/v1")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
