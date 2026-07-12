#!/usr/bin/env python3
"""Hidden layered grader — demo-01-discount-stack. Usage: grade.py <answer-file>.

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

def money(s):
    return float(s.replace("$", "").replace(",", "").strip())


def main():
    text, absent = read_answer(sys.argv)

    val, _ = parse_anchored(text, "FINAL_PRICE", money)
    if val is not None:
        cog = abs(val - 126.00) < 0.005
    else:
        cog = fallback_explicit_value(text, ["final price", "price", "jacket"],
                                      126, traps=(100,)) is True

    cognition = {"final_price_126_00": cog}
    contract = {"final_price_line": bool(re.search(
        r"^FINAL_PRICE:\s*\$?[0-9]+\.[0-9]{2}\s*$", text, re.M))}
    deterministic = {"value_is_126_00": cog}
    return emit_layered_verdict(cognition, contract, deterministic,
                                absent_output=absent)

if __name__ == "__main__":
    sys.exit(main())
