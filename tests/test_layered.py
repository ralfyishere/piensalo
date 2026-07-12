"""Layered-verdict tests: UNMEASURED absent output, decoration, fallback."""
from __future__ import annotations

from piensalo.verify.layered import (
    build_layered_verdict,
    fallback_explicit_value,
    is_absent,
    parse_anchored,
    strip_decoration,
)


def test_absent_output_is_unmeasured_not_failed():
    verdict = build_layered_verdict(
        cognition_checks={"answer": None},
        contract_checks={},
        deterministic_checks={},
        absent_output=True,
    )
    assert verdict["cognitive_correctness"]["pass"] is None  # UNMEASURED
    assert verdict["deterministic_result"]["pass"] is None
    assert verdict["failure_layer"] == "delivery-incomplete"
    assert verdict["critical_failure"] is True
    assert verdict["final_score"] == 0


def test_is_absent_on_stub_and_stall():
    assert is_absent("") is True
    assert is_absent("API Error: something broke") is True
    assert is_absent("I need permission to write the file. Please approve.") is True
    assert is_absent("ANSWER: 42\n" + "substantive analysis " * 50) is False


def test_decorated_correct_answer_passes_cognition():
    text = "**ANSWER: 42**"
    val, raw_hit = parse_anchored(text, "ANSWER", int)
    assert val == 42  # decoration stripped for cognition
    assert raw_hit is False  # raw text still fails an exact contract
    verdict = build_layered_verdict(
        cognition_checks={"answer": val == 42},
        contract_checks={"raw_line": raw_hit},
        deterministic_checks={"answer": val == 42},
        rendering_fault=True,
    )
    assert verdict["cognitive_correctness"]["pass"] is True
    assert verdict["failure_layer"] == "rendering"
    assert verdict["final_score"] == 60


def test_cognition_failure_scores_zero():
    verdict = build_layered_verdict(
        cognition_checks={"answer": False},
        contract_checks={"raw_line": True},
        deterministic_checks={"answer": False},
    )
    assert verdict["failure_layer"] == "cognition"
    assert verdict["final_score"] == 0


def test_full_pass():
    verdict = build_layered_verdict(
        cognition_checks={"answer": True},
        contract_checks={"raw_line": True},
        deterministic_checks={"answer": True},
    )
    assert verdict["failure_layer"] == "none"
    assert verdict["final_score"] == 100


def test_fallback_only_lowers_never_rescues():
    # Explicit trap statement vetoes credit even if correct value appears.
    text = "The total is 64 squares... so the answer is 8."
    assert fallback_explicit_value(text, ["squares"], correct=8, traps=(64,)) is False
    # Explicit correct statement confirms.
    assert fallback_explicit_value("The answer is 8.", ["squares"], correct=8) is True
    # No explicit statement: fallback cannot judge.
    assert fallback_explicit_value("Lots of prose.", ["squares"], correct=8) is None


def test_strip_decoration_variants():
    assert strip_decoration("**ANSWER: 42**") == "ANSWER: 42"
    assert strip_decoration("- ANSWER: 42") == "ANSWER: 42"
    assert strip_decoration("`ANSWER: 42`") == "ANSWER: 42"
    assert strip_decoration("## ANSWER: 42") == "ANSWER: 42"
