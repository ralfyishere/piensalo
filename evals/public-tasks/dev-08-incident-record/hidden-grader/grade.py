#!/usr/bin/env python3
"""Hidden layered grader — dev-08-incident-record. Usage: grade.py <answer-file>.

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

FIELDS = [
    "INCIDENT_DATE",
    "REGION",
    "SERVICE",
    "DURATION_MINUTES",
    "ROOT_CAUSE",
    "FAILED_TRANSACTIONS",
    "ONCALL",
]

EXPECT = {
    "INCIDENT_DATE": "2026-03-03",
    "REGION": "eu-west",
    "SERVICE": "checkout",
    "DURATION_MINUTES": "45",
    "ROOT_CAUSE": "expired tls certificate",
    "FAILED_TRANSACTIONS": "12400",
    "ONCALL": "priya nandakumar",
}


def main():
    text, absent = read_answer(sys.argv)
    low = text.lower()

    # --- cognition: are the correct facts present at all (any formatting)? ---
    cognition = {
        "date_correct": ("2026-03-03" in text) or ("3 march 2026" in low) or ("march 3" in low),
        "region_correct": "eu-west" in low,
        "service_correct": "checkout" in low,
        "duration_45": bool(re.search(r"\b45\b", text)),
        "root_cause_correct": "expired tls certificate" in low
            or ("tls" in low and "cert" in low and "expir" in low),
        "failed_txn_12400": bool(re.search(r"12,?400", text)),
        "oncall_correct": "priya nandakumar" in low,
    }

    # --- task contract: EXACT seven-line record ---
    lines = [l.rstrip("\n") for l in text.splitlines()]
    nonblank = [l for l in lines if l.strip() != ""]

    field_line = {}
    for l in nonblank:
        mm = re.match(r"^([A-Z_]+):\s+(.*)$", l)
        if mm and mm.group(1) in FIELDS and mm.group(1) not in field_line:
            field_line[mm.group(1)] = mm.group(2).strip()

    all_fields_col0 = all(f in field_line for f in FIELDS)
    values_exact = all(field_line.get(f, "").lower() == EXPECT[f] for f in FIELDS)
    no_thousands_sep = bool(field_line.get("FAILED_TRANSACTIONS")) and \
        re.fullmatch(r"12400", field_line.get("FAILED_TRANSACTIONS", ""))
    no_markdown = not re.search(r"\*\*|```|^\s*[-*]\s|^#", text, re.M)
    exactly_seven = len(nonblank) == 7 and all(
        re.match(r"^[A-Z_]+:\s", l) for l in nonblank)

    contract = {
        "all_seven_fields_at_col0": all_fields_col0,
        "field_values_exact": values_exact,
        "failed_txn_no_thousands_separator": bool(no_thousands_sep),
        "no_markdown_or_bold_or_fences": bool(no_markdown),
        "exactly_seven_field_lines_no_prose": exactly_seven,
    }

    deterministic = {"record_parses_and_matches":
                     all(contract.values()) and all(cognition.values())}

    # Delivery-contract task: a contract miss on right cognition is a
    # rendering-grade fault (correct field, wrong surface form).
    rendering = all(cognition.values()) and not all(contract.values())

    return emit_layered_verdict(cognition, contract, deterministic,
                                rendering_fault=rendering,
                                absent_output=absent)

if __name__ == "__main__":
    sys.exit(main())
