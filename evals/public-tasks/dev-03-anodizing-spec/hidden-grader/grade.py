#!/usr/bin/env python3
"""Hidden layered grader — dev-03-anodizing-spec. Usage: grade.py <answer-file>.

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

    spec = re.search(r"^SPEC:\s*(.+)$", text, re.M | re.I)
    t1 = re.search(r"^TYPE_I:\s*(.+)$", text, re.M | re.I)
    t2 = re.search(r"^TYPE_II:\s*(.+)$", text, re.M | re.I)
    t3 = re.search(r"^TYPE_III:\s*(.+)$", text, re.M | re.I)
    conf = re.search(r"^CONFIDENCE:\s*(high|medium|low)\s*$", text, re.M | re.I)

    # cognition judged format-independently. For each type we require the
    # process to be correctly ASSOCIATED with its type (either on the exact
    # line, or in prose as "type i ... chromic"), so a swapped answer still
    # fails cognition.
    def line_or_prose(line_m, roman, keyword):
        if line_m and keyword in line_m.group(1).lower():
            return True
        for mm in re.finditer(r"type[ _-]*" + roman + r"\b", low):
            window = low[mm.start(): mm.start() + 60]
            if keyword in window:
                return True
        return False

    cognition = {
        "spec_8625": "8625" in low,
        "type_i_chromic": line_or_prose(t1, "i", "chromic"),
        "type_ii_sulfuric": line_or_prose(t2, "ii", "sulfuric"),
        "type_iii_hardcoat": line_or_prose(t3, "iii", "hard"),
    }
    contract = {
        "spec_line": bool(spec),
        "type_i_line": bool(t1),
        "type_ii_line": bool(t2),
        "type_iii_line": bool(t3),
        "confidence_line": bool(conf),
    }
    deterministic = {"all_facts_correct": all(cognition.values())}
    return emit_layered_verdict(cognition, contract, deterministic,
                                absent_output=absent)

if __name__ == "__main__":
    sys.exit(main())
