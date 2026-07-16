"""Read-side of the gateway: status, inspect, report, replay, doctor.

These render the local event ledger — the observability surface — without any
network access or web dashboard. Output is JSON/JSONL-friendly and terminal
readable, matching PIÉNSALO's offline, inspectable conventions.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .config import ConfigError, GatewayConfig
from .ledger import EventLedger


def _ledger(ledger_dir: str) -> EventLedger:
    return EventLedger(ledger_dir)


def status(ledger_dir: str, config: GatewayConfig | None = None) -> dict:
    """A snapshot: config summary (if given) + ledger location + event count."""
    led = _ledger(ledger_dir)
    events = led.read_all()
    out: dict = {
        "ledger_path": str(led.path),
        "ledger_exists": led.path.exists(),
        "event_count": len(events),
    }
    if config is not None:
        out["config"] = config.public_summary()
    if events:
        out["last_event_ts"] = events[-1].get("ts", "")
    return out


def inspect(ledger_dir: str, last: int = 20) -> list[dict]:
    """The last N events, each trimmed to a human-scannable projection."""
    led = _ledger(ledger_dir)
    rows = led.read_last(last)
    trimmed = []
    for ev in rows:
        trimmed.append(
            {
                "ts": ev.get("ts", ""),
                "request_id": ev.get("request_id", ""),
                "client": ev.get("client", ""),
                "requested_model": ev.get("requested_model", ""),
                "resolved_model": ev.get("resolved_model", ""),
                "router_decision": ev.get("router_decision", ""),
                "router_confidence": ev.get("router_confidence", 0.0),
                "streamed": ev.get("streamed", False),
                "tool_calls": ev.get("tool_calls", 0),
                "source_context_tokens_est": ev.get("source_context_tokens_est", 0),
                "model_tokens_in": ev.get("model_tokens_in", 0),
                "model_tokens_out": ev.get("model_tokens_out", 0),
                "latency_ms": ev.get("latency_ms", 0.0),
                "status": ev.get("status", ""),
                "http_status": ev.get("http_status", 0),
            }
        )
    return trimmed


def report(ledger_dir: str) -> dict:
    """Aggregate stats across all recorded events. Honest about what observe
    mode does NOT measure (no interventions, no verification)."""
    led = _ledger(ledger_dir)
    events = led.read_all()
    n = len(events)
    decisions = Counter(ev.get("router_decision", "") for ev in events)
    statuses = Counter(ev.get("status", "") for ev in events)
    streamed = sum(1 for ev in events if ev.get("streamed"))
    with_tools = sum(1 for ev in events if ev.get("tool_calls", 0))
    # In observe mode the router is shadow-only: "would-intervene" = any
    # non-PASS_THROUGH decision. This is reported as a shadow rate, not an
    # intervention rate (nothing was actually intervened on).
    would_intervene = sum(
        1 for ev in events if ev.get("router_decision", "PASS_THROUGH") != "PASS_THROUGH"
    )
    return {
        "event_count": n,
        "mode_note": "observe: router decisions are shadow-only; nothing was intervened on",
        "router_decisions": dict(decisions),
        "shadow_would_intervene_rate": round(would_intervene / n, 3) if n else 0.0,
        "shadow_pass_through_rate": round((n - would_intervene) / n, 3) if n else 0.0,
        "statuses": dict(statuses),
        "streamed_count": streamed,
        "responses_with_tool_calls": with_tools,
        "total_model_tokens_in": sum(ev.get("model_tokens_in", 0) for ev in events),
        "total_model_tokens_out": sum(ev.get("model_tokens_out", 0) for ev in events),
        "additional_cortex_tokens": 0,  # observe mode never adds any
        "verification": "NOT_RUN (observe mode does not verify)",
    }


def replay(ledger_dir: str, request_id: str) -> dict | None:
    """Return the full recorded event for a request id (bodies only present if
    retention was 'full')."""
    return _ledger(ledger_dir).find(request_id)


def doctor(config: GatewayConfig | None, ledger_dir: str) -> dict:
    """Preflight checks for a gateway configuration. Never touches the network
    beyond the DNS resolution already done by config validation."""
    checks: list[dict] = []

    def add(name: str, ok: bool, detail: str):
        checks.append({"check": name, "ok": ok, "detail": detail})

    if config is None:
        add("config", False, "no configuration provided")
    else:
        try:
            config.validate()
            add("config_valid", True, "configuration passed validation")
        except ConfigError as e:
            add("config_valid", False, str(e))
        add(
            "loopback_bind",
            config.bind_host in ("127.0.0.1", "::1", "localhost"),
            f"bind host is {config.bind_host}",
        )
        add(
            "no_store_default",
            config.no_store,
            "bodies are not retained" if config.no_store else "WARNING: body retention enabled",
        )
        add(
            "upstream_configured",
            bool(config.upstream_base_url),
            config.upstream_base_url or "no upstream set (required to serve)",
        )
        add(
            "mode_implemented",
            config.mode == "observe",
            f"mode={config.mode} (only observe is implemented)",
        )

    ldir = Path(ledger_dir)
    add(
        "ledger_writable",
        _dir_writable(ldir),
        f"ledger dir {ldir} is writable" if _dir_writable(ldir) else f"cannot write {ldir}",
    )

    ok = all(c["ok"] for c in checks)
    return {"ok": ok, "checks": checks}


def _dir_writable(d: Path) -> bool:
    try:
        d.mkdir(parents=True, exist_ok=True)
        probe = d / ".piensalo_write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False


def render_terminal(obj) -> str:
    """Pretty JSON for terminal display."""
    return json.dumps(obj, indent=2, sort_keys=False, default=str)
