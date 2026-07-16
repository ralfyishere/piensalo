"""Local, inspectable event ledger for the Cortex Gateway.

Every request that passes through the gateway appends one JSON line to
``<ledger_dir>/events.jsonl``. The ledger is the observability surface —
`gateway status/inspect/report/replay` read it — and it is privacy-preserving
by default: bodies are stored as content **hashes**, not content, unless the
operator explicitly raises retention.

No telemetry, no network. This module only writes local files.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "gateway-event/1"

# Header names that must never be written to the ledger, even at full retention.
_SECRET_HEADERS = {"authorization", "x-api-key", "api-key", "cookie", "set-cookie", "proxy-authorization"}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def content_hash(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return "sha256:" + hashlib.sha256(data).hexdigest()


def redact_headers(headers: dict, *, redact: bool) -> dict:
    """Drop secret headers always; when ``redact`` is on, keep only a safe
    allow-list of non-sensitive header *names* (values dropped)."""
    out: dict = {}
    for k, v in headers.items():
        lk = k.lower()
        if lk in _SECRET_HEADERS:
            out[lk] = "<redacted>"
            continue
        if redact:
            # Record presence, not value, for everything else.
            out[lk] = "<present>"
        else:
            out[lk] = v
    return out


@dataclass
class GatewayEvent:
    """One request/response cycle. Fields mirror the brief's §19 report."""

    schema: str = SCHEMA_VERSION
    ts: str = ""
    request_id: str = ""
    client: str = ""  # user-agent or "unknown"
    protocol: str = "openai.chat"
    mode: str = "observe"
    requested_model: str = ""
    resolved_model: str = ""
    router_decision: str = "PASS_THROUGH"
    router_reasons: list[str] = field(default_factory=list)
    router_confidence: float = 0.0
    router_features: dict = field(default_factory=dict)
    cortex_operations_activated: list[str] = field(default_factory=list)  # observe: always []
    source_context_tokens_est: int = 0
    selected_context_tokens_est: int = 0  # observe: == source (no selection)
    model_tokens_in: int = 0
    model_tokens_out: int = 0
    model_tokens_measured: bool = False
    additional_cortex_tokens: int = 0  # observe: always 0
    latency_ms: float = 0.0
    upstream_latency_ms: float = 0.0
    verification_level: str = "NOT_RUN"  # observe: no CHECK
    expansion_count: int = 0
    fallback: bool = False
    streamed: bool = False
    tool_calls: int = 0
    status: str = "ok"  # ok | upstream_error | gateway_error | blocked
    http_status: int = 0
    error: str = ""
    retention: str = "hashes"
    request_hash: str = ""
    response_hash: str = ""
    request_headers: dict = field(default_factory=dict)
    # Only populated when retention == "full".
    request_body: dict | None = None
    response_body: str | None = None

    def to_dict(self) -> dict:
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None}


class EventLedger:
    """Append-only JSONL ledger under a directory. Loopback, local, no I/O to
    the network."""

    def __init__(self, ledger_dir: str | Path):
        self.dir = Path(ledger_dir)
        self.path = self.dir / "events.jsonl"

    def _ensure_dir(self) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)

    def append(self, event: GatewayEvent) -> None:
        self._ensure_dir()
        if not event.ts:
            event.ts = now_iso()
        line = json.dumps(event.to_dict(), sort_keys=True, default=str)
        # Append atomically-enough for a single-process loopback server.
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def read_all(self) -> list[dict]:
        if not self.path.exists():
            return []
        events: list[dict] = []
        for raw in self.path.read_text(encoding="utf-8").splitlines():
            raw = raw.strip()
            if not raw:
                continue
            events.append(json.loads(raw))
        return events

    def read_last(self, n: int) -> list[dict]:
        return self.read_all()[-n:]

    def find(self, request_id: str) -> dict | None:
        for ev in self.read_all():
            if ev.get("request_id") == request_id:
                return ev
        return None
