#!/usr/bin/env python3
"""Hidden layered grader — dev-02-log-error-filter. Usage: grade.py <answer-file>.

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

EXPECTED = ["payments", "search", "auth"]  # ERROR lines in file order


def main():
    text, absent = read_answer(sys.argv)
    low = text.lower()

    # --- cognition: correct services, correct order, no false positives ---
    seq = [w for w in re.findall(r"[a-z]+", low) if w in EXPECTED]
    first_order = []
    for w in seq:
        if w not in first_order:
            first_order.append(w)

    non_error_services = ["cache", "scheduler"]  # appear only on non-ERROR lines
    cognition = {
        "all_three_error_services_present": all(s in low for s in EXPECTED),
        "correct_order": first_order == EXPECTED,
        "no_non_error_services": not any(s in low for s in non_error_services),
    }

    contract = {
        "header_line_present": bool(re.search(r"^ERROR_SERVICES:\s*$", text, re.M)),
    }

    deterministic = {"list_matches_exactly": all(cognition.values())}
    return emit_layered_verdict(cognition, contract, deterministic,
                                absent_output=absent)

if __name__ == "__main__":
    sys.exit(main())
