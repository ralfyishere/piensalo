#!/usr/bin/env python3
"""Hidden layered grader — dev-05-greywater-recovery. Usage: grade.py <answer-file>.

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

    # --- task contract: exact field names present and parseable at column 0 ---
    lpd = re.search(r"^RECOVERED_LPD:\s*([0-9][0-9,]*)\s*$", text, re.M)
    m3 = re.search(r"^RECOVERED_M3_MONTH:\s*([0-9]+(?:\.[0-9]+)?)\s*$", text, re.M)
    eur = re.search(r"^SAVINGS_EUR_MONTH:\s*(?:EUR\s*)?([0-9]+(?:\.[0-9]+)?)\s*$", text, re.M)

    # --- cognition: correct compounded values present ANYWHERE (format-
    # independent), so a prose-only correct answer still passes cognition and
    # fails only contract.
    flat = text.replace(",", "")
    cognition = {
        "recovered_lpd_918": bool(re.search(r"\b918\b", flat)),
        "recovered_m3_month_27_54": bool(re.search(r"\b27\.54\b", flat)),
        "savings_eur_88_13": bool(re.search(r"\b88\.13\b", flat)),
    }

    contract = {
        "recovered_lpd_line": bool(lpd),
        "recovered_m3_month_line": bool(m3),
        "savings_eur_month_line": bool(eur),
        "m3_two_decimals": bool(re.search(r"^RECOVERED_M3_MONTH:\s*[0-9]+\.[0-9]{2}\s*$", text, re.M)),
        "eur_two_decimals": bool(re.search(r"^SAVINGS_EUR_MONTH:\s*(?:EUR\s*)?[0-9]+\.[0-9]{2}\s*$", text, re.M)),
    }

    deterministic = {"all_three_values_correct": all(cognition.values())}
    return emit_layered_verdict(cognition, contract, deterministic,
                                absent_output=absent)

if __name__ == "__main__":
    sys.exit(main())
