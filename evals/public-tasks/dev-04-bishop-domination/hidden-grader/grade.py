#!/usr/bin/env python3
"""Hidden layered grader — dev-04-bishop-domination. Usage: grade.py <answer-file>.

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

    # Primary parse on decoration-stripped lines; contract judged on raw text.
    val, _ = parse_anchored(text, "MIN_BISHOPS", int)
    if val is not None:
        cog = (val == 8)
    else:
        cog = fallback_explicit_value(text, ["bishops", "bishop"], 8,
                                      traps=(6, 10, 14)) is True

    cognition = {"min_bishops_8": cog}
    contract = {"min_bishops_line_present": bool(
        re.search(r"^MIN_BISHOPS:\s*[0-9]+\s*$", text, re.M))}
    deterministic = {"value_is_8": cog}
    return emit_layered_verdict(cognition, contract, deterministic,
                                absent_output=absent)

if __name__ == "__main__":
    sys.exit(main())
