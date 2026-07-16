"""Cortex Gateway — the delivery layer that makes the PIÉNSALO cortex
(THINK · CHECK · CONTEXT) reachable from the AI tools people already use.

This package is a *delivery surface*, not a fourth brand. Stage 2 ships the
``observe`` mode only: byte-faithful pass-through that preserves streaming and
tool calls, runs the Cortex Router in shadow, and records an inspectable local
event ledger. It never alters traffic and never calls an extra model.

Layering (kept strict on purpose):

- ``protocol``  — SDK-free normalized request/response/decision/event types.
- ``router``    — deterministic Cortex Router; explains every decision.
- ``ledger``    — local JSONL event ledger; redacts by default.
- ``config``    — gateway configuration + security validation (SSRF, binds).
- ``wire_openai`` — the OpenAI Chat Completions protocol adapter (edge only).
- ``server``    — the observe-mode HTTP server.
- ``report``    — status / inspect / report / replay / doctor over the ledger.

Nothing in ``protocol``/``router``/``ledger`` imports a provider SDK or a wire
format. One wire protocol's assumptions must never reach the cognitive core.
"""
from __future__ import annotations

__all__ = [
    "protocol",
    "router",
    "ledger",
    "config",
]
