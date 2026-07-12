#!/usr/bin/env python3
"""Hidden layered grader — dev-06-field-laptop. Usage: grade.py <answer-file>.

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

    # Contract: raw column-0 PICK line. Cognition: judged on the decoration-
    # stripped PICK line when one exists (a bolded PICK is a contract fault,
    # not a cognition failure); else on the full text.
    raw_pick = ""
    for l in text.splitlines():
        if l.startswith("PICK:"):
            raw_pick = l
            break
    stripped_pick = ""
    for l in text.splitlines():
        s = strip_decoration(l)
        if s.startswith("PICK:"):
            stripped_pick = s
            break

    scope = (stripped_pick or text).lower()
    picks_basalt = ("basalt" in scope) or ("ranger" in scope)
    names_disqualified = any(v in scope for v in
                             ("peregrine", "x17", "sable", "timberline"))
    cognition = {
        "picks_basalt_ranger": picks_basalt,
        "does_not_pick_disqualified": not names_disqualified,
    }
    contract = {
        "pick_line_present": bool(raw_pick),
        "single_model_named": bool(raw_pick)
            and len(raw_pick.split("PICK:", 1)[1].strip()) > 0,
    }
    deterministic = {"pick_is_basalt_only": picks_basalt and not names_disqualified}
    return emit_layered_verdict(cognition, contract, deterministic,
                                absent_output=absent)

if __name__ == "__main__":
    sys.exit(main())
