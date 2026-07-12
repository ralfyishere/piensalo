"""fable_think.loop — a bounded improvement loop with provenance.

The loop controller is a bookkeeper and gatekeeper: it never calls a
model. A driving session (human or agent) produces the evidence; the
controller enforces bounds (cycles per session, token/wall budgets),
gate-checks each action before opening a cycle, records model provenance,
archives candidates, and regenerates the next-session prompt from
canonical state. See ``controller`` for commands and ``state`` for the
on-disk layout under ``./.fable-think/``.
"""
from fable_think.loop.controller import main
from fable_think.loop.state import LoopPaths

__all__ = ["main", "LoopPaths"]
