#!/usr/bin/env python3
"""Piénsalo evaluation lab — shared layered-grading library.

Every hidden grader in evals/public-tasks/*/hidden-grader/ imports this module
and emits one layered verdict as the last line of stdout. The layering exists
to keep FAILURE ATTRIBUTION honest: "the model reasoned wrong" (cognition),
"the model reasoned right but violated the output contract" (delivery /
rendering), and "no substantive output ever arrived" (delivery-incomplete)
are different findings and must never be collapsed into one pass/fail bit.

Grading rules (hardened during public port):
  1. STRIP DECORATION before any anchored parse (bold, backticks, bullets,
     leading indentation). A bolded correct answer must not be scored as a
     cognition failure; it is a contract/rendering fault only.
  2. A prose FALLBACK may only LOWER credit relative to the primary parse —
     never rescue credit the primary parse could not see. If the anchored
     value exists, it is authoritative. If it does not, the fallback may only
     confirm an EXPLICIT statement of the answer, and any explicit statement
     of a known-wrong trap value vetoes credit. Mentioning the task's numbers
     or scale is NOT stating the answer.
  3. ABSENT OUTPUT is not a cognition failure: if the answer text is empty,
     an infrastructure stub, or a permission-stall shell with no substantive
     content, cognition = UNMEASURED (None) and failure_layer =
     "delivery-incomplete". Never grade a stub as a wrong answer.
  4. Contract compliance is judged on the RAW text (decoration violates an
     exact-format contract even when cognition passes).

Verdict JSON (last line of grader stdout):
{
  "cognitive_correctness":    {"pass": true|false|null, "checks": {...}},  # null = UNMEASURED
  "task_contract_compliance": {"pass": bool, "checks": {...}},
  "deterministic_result":     {"pass": true|false|null, "checks": {...}},
  "critical_failure":         bool,
  "final_score":              0-100,
  "failure_layer":            "cognition"|"delivery"|"rendering"|"routing"|
                              "verification"|"delivery-incomplete"|"grader"|"none"
}
"""
import json
import re

STUB_SIGNATURES = (
    "API Error", "hit your session limit", "Connection closed",
    "rate limit", "overloaded_error",
)

STALL_PATTERNS = (
    r"permission to (write|create|save)",
    r"please approve",
    r"approve the file write",
    r"awaiting (your )?(approval|permission|confirmation)",
)


def strip_decoration(line):
    """Bold/italics/backticks/bullets/indentation removed; content untouched."""
    s = line.strip()
    s = re.sub(r"^[-*+]\s+", "", s)           # bullet
    s = re.sub(r"^#{1,6}\s+", "", s)          # heading
    s = s.strip("`")                           # code span wrap
    s = re.sub(r"^\*{1,3}(.*?)\*{1,3}$", r"\1", s)  # full-line bold/italic
    s = s.replace("**", "")                    # inline bold remnants
    return s.strip()


def is_absent(text):
    """Empty, infrastructure stub, or a stall shell with no substantive content."""
    t = text.strip()
    if len(t) < 5:
        return True
    if len(t) < 400 and any(sig.lower() in t.lower() for sig in STUB_SIGNATURES):
        return True
    if len(t) < 400 and any(re.search(p, t, re.I) for p in STALL_PATTERNS):
        return True
    return False


def parse_anchored(text, field, cast=str):
    """Primary parse: exact `FIELD: value` line, judged on DECORATION-STRIPPED
    lines (rule 1). Returns (value|None, raw_line_hit: bool) where raw_line_hit
    reflects the RAW text for contract judging (rule 4)."""
    pat = re.compile(r"^%s:\s*(.+?)\s*$" % re.escape(field))
    raw_hit = any(pat.match(l) for l in text.splitlines())
    val = None
    for l in text.splitlines():
        m = pat.match(strip_decoration(l))
        if m:
            try:
                val = cast(m.group(1).strip().strip("`").strip("*"))
            except (ValueError, TypeError):
                val = None
            break
    return val, raw_hit


def fallback_explicit_value(text, field_words, correct, traps=()):
    """Fallback (rule 2): may only confirm an EXPLICIT 'answer is X'-class
    statement; any explicit trap-value statement vetoes. Returns True/False/None
    (None = fallback cannot judge; callers treat None as no credit)."""
    joined = "|".join(re.escape(w) for w in field_words)
    say = lambda v: bool(
        re.search(r"(answer|result|total|final)\D{0,25}\b%s\b" % re.escape(str(v)), text, re.I)
        or re.search(r"\b%s\b\s*(?:%s)" % (re.escape(str(v)), joined), text, re.I))
    for t in traps:
        if say(t):
            return False
    if say(correct):
        return True
    return None


def emit_layered_verdict(cognition_checks, contract_checks, deterministic_checks,
                         critical_failure=False, rendering_fault=False,
                         absent_output=False):
    """cognition_checks values may be True/False/None (None = unmeasured)."""
    def layer_pass(checks):
        vals = list(checks.values())
        if any(v is None for v in vals):
            return None
        return all(bool(v) for v in vals)

    cog = layer_pass(cognition_checks)
    con = all(bool(v) for v in contract_checks.values()) if contract_checks else True
    det = layer_pass(deterministic_checks)

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
    else:  # cog is None without absent_output: grader could not measure
        layer = "grader"
        score = 0

    verdict = {
        "cognitive_correctness": {"pass": cog, "checks": cognition_checks},
        "task_contract_compliance": {"pass": con, "checks": contract_checks},
        "deterministic_result": {"pass": det, "checks": deterministic_checks},
        "critical_failure": bool(critical_failure or absent_output),
        "final_score": score,
        "failure_layer": layer,
    }
    print(json.dumps(verdict))
    return 0


def read_answer(argv):
    """Read the answer file named as argv[1]. Returns (text, absent: bool)."""
    if len(argv) < 2:
        return "", True
    try:
        text = open(argv[1], encoding="utf-8", errors="replace").read()
    except OSError:
        return "", True
    return text, is_absent(text)
