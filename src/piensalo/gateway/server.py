"""Observe-mode HTTP server for the Cortex Gateway.

Contract (brief §9, Mode 1): accept client traffic, forward it **unchanged**,
preserve streaming and tool calls, run the Cortex Router in **shadow**, and
record local event metadata. It never alters the request or the response, and
never calls an additional model.

Fidelity model — the reason observe mode is safe by construction:

- The request body is forwarded to the upstream **verbatim** (the original
  bytes). We parse a *copy* only to feed the shadow router.
- The response body is streamed back to the client as it arrives from the
  upstream. For non-streaming responses the body bytes are identical. For SSE
  streams the application payload (the ``data:`` events) is forwarded byte for
  byte; only the HTTP transfer framing is re-managed (chunked), which is a
  transport detail, not application data.

Security defaults are fail-closed: loopback bind, optional bearer auth (401 on
mismatch), body-size cap (413), recursive-proxy-loop guard (508), and no body
retention unless explicitly enabled.

Stdlib only — no provider SDK, no third-party server.
"""
from __future__ import annotations

import time
import urllib.error
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from . import wire_openai
from .config import GatewayConfig
from .ledger import EventLedger, GatewayEvent, content_hash, redact_headers
from .router import CortexRouter

# Hop-by-hop headers must not be forwarded (RFC 7230 §6.1).
_HOP_BY_HOP = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}

_LOOP_HEADER = "X-Piensalo-Gateway"
_STREAM_CHUNK = 4096


class GatewayServer(ThreadingHTTPServer):
    """Threaded loopback server holding gateway state."""

    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, config: GatewayConfig):
        self.gwconfig = config
        self.router = CortexRouter(config.router_policy)
        self.ledger = EventLedger(config.ledger_dir)
        self._upstream = urlparse(config.upstream_base_url)
        super().__init__((config.bind_host, config.bind_port), ObserveHandler)

    @property
    def upstream_hostport(self) -> str:
        p = self._upstream
        return f"{p.hostname}:{p.port or ''}"


class ObserveHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    # Quiet by default; the ledger is the record of truth.
    def log_message(self, fmt, *args):  # noqa: D401
        return

    # ---- entry points ----

    def do_POST(self):  # noqa: N802
        self._proxy()

    def do_GET(self):  # noqa: N802
        self._proxy()

    # ---- core ----

    def _proxy(self):
        cfg: GatewayConfig = self.server.gwconfig
        router: CortexRouter = self.server.router
        ledger: EventLedger = self.server.ledger
        started = time.perf_counter()
        request_id = uuid.uuid4().hex

        # Recursive-proxy-loop guard: if a request already carries our marker,
        # something is pointing the gateway at itself. Fail closed.
        if self.headers.get(_LOOP_HEADER):
            self._error(508, "recursive gateway loop detected", request_id, ledger, cfg, started)
            return

        # Auth (fail closed when a token is configured).
        if cfg.auth_token is not None and not self._auth_ok(cfg.auth_token):
            self._error(401, "unauthorized", request_id, ledger, cfg, started, status="blocked")
            return

        # Bounded body read.
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length > cfg.max_body_bytes:
            self._error(413, "request body too large", request_id, ledger, cfg, started,
                        status="blocked")
            return
        body = self.rfile.read(length) if length else b""

        is_chat = self.command == "POST" and self.path.rstrip("/").endswith("/chat/completions")

        # Shadow router — recorded, never acted on.
        decision = None
        norm_req = None
        if is_chat:
            norm_req = wire_openai.parse_request(body, request_id=request_id)
            decision = router.decide(norm_req, shadow=True)

        # Build the upstream request. Forward bytes verbatim.
        upstream_url = _join_upstream(cfg.upstream_base_url, self.path)
        fwd_headers = self._forward_headers(cfg)
        up_req = urllib.request.Request(
            upstream_url, data=body if body else None, headers=fwd_headers, method=self.command
        )

        up_started = time.perf_counter()
        try:
            resp = urllib.request.urlopen(up_req, timeout=cfg.upstream_timeout_s)
        except urllib.error.HTTPError as e:
            # Upstream returned a non-2xx: forward it faithfully (observe mode
            # owns nothing about the upstream's decision).
            self._relay_error_response(e, request_id, ledger, cfg, started, up_started,
                                       norm_req, decision, body)
            return
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            self._error(502, f"upstream unreachable: {e}", request_id, ledger, cfg, started,
                        status="upstream_error", norm_req=norm_req, decision=decision,
                        req_body=body)
            return

        wants_stream = bool(norm_req and norm_req.stream) or _looks_like_sse(resp)
        with resp:
            if wants_stream:
                self._relay_stream(resp, request_id, ledger, cfg, started, up_started,
                                   norm_req, decision, body)
            else:
                self._relay_full(resp, request_id, ledger, cfg, started, up_started,
                                 norm_req, decision, body)

    # ---- relay helpers ----

    def _relay_full(self, resp, request_id, ledger, cfg, started, up_started,
                    norm_req, decision, req_body):
        payload = resp.read()
        up_latency = (time.perf_counter() - up_started) * 1000.0
        status = resp.status
        parsed = wire_openai.parse_response(
            payload, requested_model=(norm_req.model if norm_req else "")
        )
        self.send_response(status)
        for k, v in self._response_headers(resp, streaming=False, body_len=len(payload)):
            self.send_header(k, v)
        self.end_headers()
        # Record BEFORE the client-visible body so the ledger is durable by the
        # time the client's read returns (no observer race).
        self._record(ledger, cfg, request_id, started, up_latency, norm_req, decision,
                     parsed, req_body, payload, status=_status_word(status), http_status=status,
                     streamed=False)
        self.wfile.write(payload)
        self.wfile.flush()

    def _relay_stream(self, resp, request_id, ledger, cfg, started, up_started,
                      norm_req, decision, req_body):
        status = resp.status
        self.send_response(status)
        for k, v in self._response_headers(resp, streaming=True, body_len=None):
            self.send_header(k, v)
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()

        captured: list[bytes] = []
        while True:
            chunk = resp.read(_STREAM_CHUNK)
            if not chunk:
                break
            captured.append(chunk)
            # chunked transfer framing (transport detail; payload unchanged).
            self.wfile.write(f"{len(chunk):X}\r\n".encode("ascii"))
            self.wfile.write(chunk)
            self.wfile.write(b"\r\n")
            self.wfile.flush()

        up_latency = (time.perf_counter() - up_started) * 1000.0
        parsed = wire_openai.parse_stream_metadata(
            captured, requested_model=(norm_req.model if norm_req else "")
        )
        # Record BEFORE the terminating chunk, which is what signals end-of-
        # stream to the client — so the ledger is durable when the client returns.
        self._record(ledger, cfg, request_id, started, up_latency, norm_req, decision,
                     parsed, req_body, b"".join(captured), status=_status_word(status),
                     http_status=status, streamed=True)
        self.wfile.write(b"0\r\n\r\n")
        self.wfile.flush()

    def _relay_error_response(self, http_error, request_id, ledger, cfg, started, up_started,
                              norm_req, decision, req_body):
        payload = http_error.read()
        up_latency = (time.perf_counter() - up_started) * 1000.0
        parsed = wire_openai.parse_response(payload, requested_model=(norm_req.model if norm_req else ""))
        self.send_response(http_error.code)
        for k, v in self._response_headers(http_error, streaming=False, body_len=len(payload)):
            self.send_header(k, v)
        self.end_headers()
        self._record(ledger, cfg, request_id, started, up_latency, norm_req, decision,
                     parsed, req_body, payload, status="upstream_error",
                     http_status=http_error.code, streamed=False)
        self.wfile.write(payload)
        self.wfile.flush()

    # ---- header handling ----

    def _forward_headers(self, cfg: GatewayConfig) -> dict:
        out: dict = {}
        for k in self.headers.keys():
            lk = k.lower()
            if lk in _HOP_BY_HOP or lk in ("host", "content-length"):
                continue
            out[k] = self.headers[k]
        # Upstream host + our loop marker.
        up = urlparse(cfg.upstream_base_url)
        out["Host"] = up.netloc
        out[_LOOP_HEADER] = "observe"
        # Upstream auth override: if an explicit upstream key is configured,
        # replace the client's Authorization with it; otherwise pass through.
        if getattr(cfg, "upstream_api_key", None):
            out["Authorization"] = f"Bearer {cfg.upstream_api_key}"
        return out

    def _response_headers(self, resp, *, streaming: bool, body_len):
        pairs = []
        headers = resp.headers
        for k in headers.keys():
            lk = k.lower()
            if lk in _HOP_BY_HOP:
                continue
            if lk == "content-length":
                continue  # we set our own framing
            pairs.append((k, headers[k]))
        if not streaming and body_len is not None:
            pairs.append(("Content-Length", str(body_len)))
        return pairs

    def _auth_ok(self, token: str) -> bool:
        header = self.headers.get("Authorization", "")
        expected = f"Bearer {token}"
        # Constant-time-ish compare.
        if len(header) != len(expected):
            return False
        return _consteq(header, expected)

    # ---- recording ----

    def _record(self, ledger, cfg, request_id, started, up_latency, norm_req, decision,
                parsed, req_body, resp_bytes, *, status, http_status, streamed):
        latency = (time.perf_counter() - started) * 1000.0
        src_tokens = norm_req.input_tokens_est() if norm_req else 0
        ev = GatewayEvent(
            request_id=request_id,
            client=self.headers.get("User-Agent", "unknown"),
            protocol=wire_openai.PROTOCOL,
            mode=cfg.mode,
            requested_model=(norm_req.model if norm_req else ""),
            resolved_model=parsed.resolved_model if parsed else "",
            router_decision=(decision.decision if decision else "PASS_THROUGH"),
            router_reasons=(decision.reasons if decision else ["non-chat path: forwarded as-is"]),
            router_confidence=(decision.confidence if decision else 0.0),
            router_features=(decision.features if decision else {}),
            cortex_operations_activated=[],  # observe: never activates cortex ops
            source_context_tokens_est=src_tokens,
            selected_context_tokens_est=src_tokens,  # observe: no selection
            model_tokens_in=(parsed.usage.tokens_in if parsed else 0),
            model_tokens_out=(parsed.usage.tokens_out if parsed else 0),
            model_tokens_measured=(parsed.usage.measured if parsed else False),
            additional_cortex_tokens=0,
            latency_ms=round(latency, 2),
            upstream_latency_ms=round(up_latency, 2),
            verification_level="NOT_RUN",
            streamed=streamed,
            tool_calls=(len(parsed.tool_calls) if parsed else 0),
            status=status,
            http_status=http_status,
            retention=cfg.retention,
            request_hash=content_hash(req_body) if req_body else "",
            response_hash=content_hash(resp_bytes) if resp_bytes else "",
            request_headers=redact_headers(dict(self.headers), redact=cfg.redact),
        )
        if cfg.retention == "full" and not cfg.no_store:
            ev.request_body = norm_req.raw if norm_req else None
            try:
                ev.response_body = resp_bytes.decode("utf-8", errors="replace")
            except Exception:  # pragma: no cover - defensive
                ev.response_body = None
        ledger.append(ev)

    def _error(self, code, message, request_id, ledger, cfg, started, *, status="gateway_error",
               norm_req=None, decision=None, req_body=b""):
        body = f'{{"error":{{"message":{message!r},"type":"piensalo_gateway"}}}}'.encode()
        latency = (time.perf_counter() - started) * 1000.0
        # Record BEFORE any response byte: a client can raise on the status/
        # headers alone (never reading the body), so the ledger must be durable
        # first for error responses.
        ledger.append(
            GatewayEvent(
                request_id=request_id,
                client=self.headers.get("User-Agent", "unknown"),
                mode=cfg.mode,
                requested_model=(norm_req.model if norm_req else ""),
                router_decision=(decision.decision if decision else "PASS_THROUGH"),
                router_reasons=(decision.reasons if decision else [message]),
                latency_ms=round(latency, 2),
                status=status,
                http_status=code,
                error=message,
                retention=cfg.retention,
                request_hash=content_hash(req_body) if req_body else "",
                request_headers=redact_headers(dict(self.headers), redact=cfg.redact),
            )
        )
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()


def _join_upstream(base_url: str, client_path: str) -> str:
    """Join the configured upstream base URL with the incoming request path
    without duplicating a shared path prefix.

    An OpenAI client configured against the gateway's ``…/v1`` sends the HTTP
    path ``/v1/chat/completions``. If the operator also configured the upstream
    as ``http://host/v1`` (the documented, natural form), a naive concatenation
    would produce ``…/v1/v1/chat/completions`` — a 404 on a real provider.

    Rule: if the client path already begins with the base URL's path segment,
    forward to ``scheme://host`` + client path (the prefix is already present);
    otherwise append the client path to the full base. Handles base URLs with
    no path (``http://host``) and deeper prefixes (``…/api/v1``). Query strings
    on the client path are preserved.
    """
    p = urlparse(base_url)
    host_root = f"{p.scheme}://{p.netloc}"
    base_path = p.path.rstrip("/")  # "" or "/v1" or "/api/v1"
    if base_path and (client_path == base_path or client_path.startswith(base_path + "/")):
        return host_root + client_path
    return host_root + base_path + client_path


def _status_word(http_status: int) -> str:
    """Map an HTTP status to the ledger's coarse status word."""
    if 200 <= http_status < 400:
        return "ok"
    return "upstream_error"


def _looks_like_sse(resp) -> bool:
    ctype = resp.headers.get("Content-Type", "") if hasattr(resp, "headers") else ""
    return "text/event-stream" in ctype.lower()


def _consteq(a: str, b: str) -> bool:
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    return result == 0


def serve(config: GatewayConfig) -> GatewayServer:
    """Construct (but do not block on) a gateway server. Caller runs
    ``server.serve_forever()`` or drives it in a thread/tests."""
    # Recursion guard at construction: refuse to point the gateway at itself.
    up = urlparse(config.upstream_base_url) if config.upstream_base_url else None
    if up and up.hostname in ("127.0.0.1", "::1", "localhost") and (up.port == config.bind_port):
        raise ValueError(
            "refusing to configure a recursive proxy loop: upstream "
            f"{up.hostname}:{up.port} equals the gateway bind port"
        )
    return GatewayServer(config)
