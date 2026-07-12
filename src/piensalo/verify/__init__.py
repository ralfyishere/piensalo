"""piensalo.verify — output-contract validation and layered verdicts.

Two complementary checks live here. ``contract`` validates the required
SURFACE form of an answer (field presence, exact-format rules) without ever
touching substantive content. ``layered`` separates cognition (is the
underlying answer right?) from delivery (is it in the demanded form?) so a
bolded correct answer is never scored as a wrong answer, and absent output
is never scored as a cognition failure.
"""
from piensalo.verify.contract import check, emit, load_task_contract, normalize
from piensalo.verify.layered import (
    build_layered_verdict,
    fallback_explicit_value,
    is_absent,
    parse_anchored,
    strip_decoration,
)

__all__ = [
    "load_task_contract",
    "check",
    "emit",
    "normalize",
    "build_layered_verdict",
    "strip_decoration",
    "is_absent",
    "parse_anchored",
    "fallback_explicit_value",
]
