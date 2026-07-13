"""Deterministic, provider-independent token estimation.

No tokenizer library and no provider SDK: estimates use the widely-cited
~4-characters-per-token heuristic, which is deterministic and neutral
across model families. Every reported number is an ESTIMATE and is always
labeled as such downstream — never a billed or provider-exact count.
"""
from __future__ import annotations

ESTIMATOR = "chars/4 heuristic (provider-independent estimate)"


def estimate_tokens(text: str) -> int:
    """Deterministic token estimate for any text (>= 1 for non-empty)."""
    if not text:
        return 0
    return max(1, (len(text) + 3) // 4)
