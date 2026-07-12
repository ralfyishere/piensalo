#!/usr/bin/env python3
"""Hidden layered grader — dev-07-calibration-windows. Usage: grade.py <answer-file>.

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

    # Primary parse on decoration-stripped lines (a bolded correct line is a
    # contract fault, not a cognition failure); authoritative when present.
    val, _ = parse_anchored(text, "CALIBRATIONS", int)
    if val is not None:
        cog = (val == 7)
    else:
        cog = fallback_explicit_value(text, ["calibrations", "calibration"], 7,
                                      traps=(6,)) is True

    cognition = {"calibrations_7": cog}
    contract = {"calibrations_line_present": bool(
        re.search(r"^CALIBRATIONS:\s*[0-9]+\s*$", text, re.M))}
    deterministic = {"value_is_7": cog}
    return emit_layered_verdict(cognition, contract, deterministic,
                                absent_output=absent)

if __name__ == "__main__":
    sys.exit(main())
