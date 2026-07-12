"""Layered verdicts: separate cognition from delivery before scoring.

Grading rules (each learned from a witnessed grading failure class):

1. STRIP DECORATION before any anchored parse (bold, backticks, bullets,
   leading indentation) — a bolded correct answer must not fail the
   cognition layer.
2. A prose FALLBACK may only LOWER credit relative to the primary parse —
   never rescue credit the primary parse could not see. If the anchored
   value exists, it is authoritative; if it does not, the fallback may only
   confirm an EXPLICIT statement of the answer, and any explicit statement
   of a known-wrong trap value vetoes credit.
3. ABSENT OUTPUT is not a cognition failure: if the answer text is empty,
   an infrastructure stub, or a permission-stall shell with no substantive
   content, cognition = UNMEASURED (None) and the failure layer is
   ``delivery-incomplete``.
4. Contract compliance is judged on the RAW text (decoration violates an
   exact-format contract even when cognition passes).

Verdict schema::

    {"cognitive_correctness":    {"pass": true|false|null, "checks": {...}},
     "task_contract_compliance": {"pass": bool, "checks": {...}},
     "deterministic_result":     {"pass": true|false|null, "checks": {...}},
     "critical_failure":         bool,
     "final_score":              0-100,
     "failure_layer":            "cognition"|"delivery"|"rendering"|"routing"|
                                 "verification"|"delivery-incomplete"|"grader"|"none"}

``pass: null`` always means UNMEASURED, never "soft fail".
"""
from __future__ import annotations

import re

STUB_SIGNATURES = (
    "API Error",
    "hit your session limit",
    "Connection closed",
    "rate limit",
    "overloaded_error",
)

STALL_PATTERNS = (
    r"permission to (write|create|save)",
    r"please approve",
    r"approve the file write",
    r"awaiting (your )?(approval|permission|confirmation)",
)


def strip_decoration(line: str) -> str:
    """Remove bold/italics/backticks/bullets/heading markers/indentation.

    Content is untouched — this only removes rendering.
    """
    s = line.strip()
    s = re.sub(r"^[-*+]\s+", "", s)  # bullet
    s = re.sub(r"^#{1,6}\s+", "", s)  # heading
    s = s.strip("`")  # code-span wrap
    s = re.sub(r"^\*{1,3}(.*?)\*{1,3}$", r"\1", s)  # full-line bold/italic
    s = s.replace("**", "")  # inline bold remnants
    return s.strip()


def is_absent(text: str) -> bool:
    """True when the output is empty, an infra stub, or a stall shell with
    no substantive content — i.e. cognition cannot be measured from it."""
    t = text.strip()
    if len(t) < 5:
        return True
    if len(t) < 400 and any(sig.lower() in t.lower() for sig in STUB_SIGNATURES):
        return True
    if len(t) < 400 and any(re.search(p, t, re.I) for p in STALL_PATTERNS):
        return True
    return False


def parse_anchored(text: str, field: str, cast=str):
    """Primary parse: an exact ``FIELD: value`` line, judged on
    DECORATION-STRIPPED lines (rule 1).

    Returns ``(value_or_None, raw_line_hit)`` where ``raw_line_hit``
    reflects the RAW text, for contract judging (rule 4).
    """
    pat = re.compile(r"^%s:\s*(.+?)\s*$" % re.escape(field))
    raw_hit = any(pat.match(line) for line in text.splitlines())
    val = None
    for line in text.splitlines():
        m = pat.match(strip_decoration(line))
        if m:
            try:
                val = cast(m.group(1).strip().strip("`").strip("*"))
            except (ValueError, TypeError):
                val = None
            break
    return val, raw_hit


def fallback_explicit_value(text: str, field_words, correct, traps=()):
    """Prose fallback under rule 2: may only confirm an EXPLICIT
    'answer is X'-class statement; any explicit statement of a trap value
    vetoes credit. Returns True/False/None (None = fallback cannot judge).
    """
    joined = "|".join(re.escape(w) for w in field_words)

    def says(v) -> bool:
        v = re.escape(str(v))
        return bool(
            re.search(r"(answer|result|total|final)\D{0,25}\b%s\b" % v, text, re.I)
            or re.search(r"\b%s\b\s*(?:%s)" % (v, joined), text, re.I)
        )

    for t in traps:
        if says(t):
            return False
    if says(correct):
        return True
    return None


def _layer_pass(checks: dict):
    """True if all checks pass, False if any fails, None if any check is
    unmeasured OR there are no checks at all (no checks is not a pass)."""
    vals = list(checks.values())
    if not vals or any(v is None for v in vals):
        return None
    return all(bool(v) for v in vals)


def build_layered_verdict(
    cognition_checks: dict,
    contract_checks: dict,
    deterministic_checks: dict,
    critical_failure: bool = False,
    rendering_fault: bool = False,
    absent_output: bool = False,
) -> dict:
    """Build the layered verdict dict. Check values may be True/False/None
    (None = unmeasured). Returns the verdict; callers print/serialize it.
    """
    cog = _layer_pass(cognition_checks)
    con = all(bool(v) for v in contract_checks.values()) if contract_checks else True
    det = _layer_pass(deterministic_checks)

    if absent_output:
        cog, det = None, None
        layer = "delivery-incomplete"
        score = 0
    elif critical_failure:
        layer = "delivery-incomplete"
        score = 0
    elif cog is False:
        layer = "cognition"
        score = 0
    elif cog is True and not con:
        layer = "rendering" if rendering_fault else "delivery"
        score = 60
    elif cog is True and con:
        layer = "none"
        score = 100
    else:  # cog is None without absent_output: no oracle could measure it
        layer = "grader"
        score = 0

    return {
        "cognitive_correctness": {"pass": cog, "checks": cognition_checks},
        "task_contract_compliance": {"pass": con, "checks": contract_checks},
        "deterministic_result": {"pass": det, "checks": deterministic_checks},
        "critical_failure": bool(critical_failure or absent_output),
        "final_score": score,
        "failure_layer": layer,
    }
