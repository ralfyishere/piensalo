#!/usr/bin/env python3
"""Hidden layered grader — demo-02-pilot-review. Usage: grade.py <answer-file>.

Hardened during public port:
- decoration is stripped before any anchored parse (a bolded correct answer is
  a contract fault, never a cognition failure);
- the prose fallback may only confirm an explicit answer statement, and any
  explicit trap value vetoes credit;
- stubs/stalls grade as delivery-incomplete with cognition UNMEASURED (null).
"""
import os
import re
import sys

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "graders")))
from layered_common import (emit_layered_verdict, read_answer, parse_anchored,
                            fallback_explicit_value, strip_decoration)

def pct_cast(s):
    return int(s.rstrip("%").strip())


def main():
    text, absent = read_answer(sys.argv)
    low = text.lower()

    pct, _ = parse_anchored(text, "VERIFIED_REDUCTION_PCT", pct_cast)
    contra, _ = parse_anchored(text, "CONTRADICTION_FOUND")
    source, _ = parse_anchored(text, "CONTROLLING_SOURCE")

    if pct is not None:
        pct_ok = (pct == 11)
    else:
        pct_ok = fallback_explicit_value(text, ["percent", "%", "reduction"],
                                         11, traps=(18,)) is True

    if contra is not None:
        contra_ok = contra.lower().startswith("yes")
    else:
        contra_ok = bool(re.search(r"contradict|conflict\b|disagree", low)) \
            and not re.search(r"no (contradiction|conflict)", low)

    if source is not None:
        source_ok = "appendix" in source.lower()
    else:
        source_ok = bool(
            re.search(r"appendix\b[^.\n]{0,60}(supersedes|controls|governs|is authoritative)", low)
            or re.search(r"(defer to|controlling|authoritative)[^.\n]{0,40}appendix", low))

    cognition = {
        "verified_pct_11": pct_ok,
        "contradiction_found_yes": contra_ok,
        "controlling_source_appendix": source_ok,
    }
    contract = {
        "pct_line": bool(re.search(r"^VERIFIED_REDUCTION_PCT:\s*[0-9]+%?\s*$", text, re.M)),
        "contradiction_line": bool(re.search(r"^CONTRADICTION_FOUND:\s*(yes|no)\s*$", text, re.M | re.I)),
        "source_line": bool(re.search(r"^CONTROLLING_SOURCE:\s*\S+", text, re.M)),
    }
    deterministic = {"all_three_correct": all(cognition.values())}
    return emit_layered_verdict(cognition, contract, deterministic,
                                absent_output=absent)

if __name__ == "__main__":
    sys.exit(main())
