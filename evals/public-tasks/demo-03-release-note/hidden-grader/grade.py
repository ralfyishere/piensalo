#!/usr/bin/env python3
"""Hidden layered grader — demo-03-release-note. Usage: grade.py <answer-file>.

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

def main():
    text, absent = read_answer(sys.argv)
    low = text.lower()

    cognition = {
        "offline_sync_mentioned": ("offline" in low) and ("sync" in low),
        "search_40_pct_faster": bool(re.search(r"\b40\s*(%|percent)", low))
            and ("search" in low),
        "android8_eol_sept30": ("android 8" in low)
            and bool(re.search(r"september\s*30|sept\.?\s*30\b|09-30|9/30", low)),
    }
    contract = {
        "headline_line": bool(re.search(r"^HEADLINE: .{1,80}$", text, re.M)),
        "audience_line": bool(re.search(r"^AUDIENCE: existing-users\s*$", text, re.M)),
        "cta_line_exact": bool(re.search(
            r"^CTA: Update Lumen Notes in your app store\s*$", text, re.M)),
        "no_bold_or_fences": not re.search(r"\*\*|```", text),
    }
    deterministic = {"all_facts_present": all(cognition.values())}
    return emit_layered_verdict(cognition, contract, deterministic,
                                absent_output=absent)

if __name__ == "__main__":
    sys.exit(main())
