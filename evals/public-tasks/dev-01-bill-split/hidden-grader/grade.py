#!/usr/bin/env python3
"""Hidden layered grader — dev-01-bill-split. Usage: grade.py <answer-file>.

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

    tip = re.search(r"^TIP:\s*\$?([0-9]+\.[0-9]{2})\s*$", text, re.M)
    total = re.search(r"^TOTAL:\s*\$?([0-9]+\.[0-9]{2})\s*$", text, re.M)
    per = re.search(r"^PER_PERSON:\s*\$?([0-9]+\.[0-9]{2})\s*$", text, re.M)

    # cognition judged format-independently: the correct values present anywhere.
    cognition = {
        "tip_15_12": bool(re.search(r"\b15\.12\b", text)),
        "total_99_12": bool(re.search(r"\b99\.12\b", text)),
        "per_person_24_78": bool(re.search(r"\b24\.78\b", text)),
    }
    contract = {
        "tip_line": bool(tip),
        "total_line": bool(total),
        "per_person_line": bool(per),
    }
    deterministic = {"all_values_correct": all(cognition.values())}
    return emit_layered_verdict(cognition, contract, deterministic,
                                absent_output=absent)

if __name__ == "__main__":
    sys.exit(main())
