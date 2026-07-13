"""Context MVP: schema validation, canonical serialization, parsers."""
from __future__ import annotations

import json

import pytest

from piensalo.context import parser, schema
from piensalo.context.compiler import compile_capsule


def _compile(text: str, fmt: str = "text", budget: int = 5000, **kw):
    return compile_capsule(text, fmt=fmt, goal="continue", token_budget=budget, **kw)


BASIC = """\
OBJECTIVE: Ship the widget.
DECISION: Use sqlite for storage.
CONSTRAINT: Never push directly to main.
STOP CONDITION: Stop after two consecutive CI failures.
NEXT ACTION: Run `uv run pytest -q` and fix the first failure.
"""


# --------------------------------------------------------------- schema
def test_compiled_capsule_validates():
    capsule = _compile(BASIC).capsule
    assert schema.validate_capsule(capsule) == []


def test_missing_key_is_reported_not_defaulted():
    capsule = _compile(BASIC).capsule
    broken = {k: v for k, v in capsule.items() if k != "invariants"}
    errors = schema.validate_capsule(broken)
    assert any("invariants" in e for e in errors)


def test_unknown_status_and_exactness_rejected():
    capsule = _compile(BASIC).capsule
    capsule["decisions"][0]["status"] = "MAYBE"
    errors = schema.validate_capsule(capsule)
    assert any("unknown status 'MAYBE'" in e for e in errors)
    capsule["decisions"][0]["status"] = "ACTIVE"
    capsule["decisions"][0]["exactness"] = "FUZZY"
    errors = schema.validate_capsule(capsule)
    assert any("unknown exactness 'FUZZY'" in e for e in errors)


def test_superseded_requires_backlink():
    capsule = _compile(BASIC).capsule
    capsule["decisions"][0]["status"] = "SUPERSEDED"
    errors = schema.validate_capsule(capsule)
    assert any("SUPERSEDED without superseded_by" in e for e in errors)


def test_behavioral_equivalence_field_cannot_claim_a_pass():
    capsule = _compile(BASIC).capsule
    capsule["risk"]["behavioral_equivalence"] = "SAFE TO RESUME"
    errors = schema.validate_capsule(capsule)
    assert any("must be 'UNMEASURED'" in e for e in errors)


def test_canonical_json_is_stable_and_platform_neutral():
    capsule = _compile(BASIC).capsule
    a = schema.canonical_json(capsule)
    b = schema.canonical_json(json.loads(a))
    assert a == b
    assert a.endswith("\n")


def test_load_capsule_rejects_invalid_json(tmp_path):
    bad = tmp_path / "capsule.json"
    bad.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError, match="not valid JSON"):
        schema.load_capsule(str(bad))


def test_load_capsule_missing_file_is_specific(tmp_path):
    with pytest.raises(ValueError, match="capsule not found"):
        schema.load_capsule(str(tmp_path / "nope.json"))


# ---------------------------------------------------------- text parser
def test_text_parser_recognizes_all_markers():
    text = """\
OBJECTIVE: O.
SUCCESS CONDITION: S.
DECISION: D.
CONSTRAINT: C.
INVARIANT: I.
STOP CONDITION: St.
COMPLETED: Co.
FAILED APPROACH: F.
OPEN QUESTION: Q.
OPEN ACTION: A.
NEXT ACTION: N.
ARTIFACT: src/x.py
"""
    result = parser.parse_text(text)
    types = [i.record_type for i in result.items]
    assert types == ["objective", "success_condition", "decision",
                     "constraint", "invariant", "stop_condition",
                     "completed", "failed_approach", "open_question",
                     "open_action", "next_action", "artifact"]
    assert result.omissions == []


def test_text_parser_continuation_lines_and_spans():
    text = "DECISION: first line\n  second line\n  third line\n"
    result = parser.parse_text(text)
    item = result.items[0]
    assert item.content == "first line\nsecond line\nthird line"
    assert (item.line_start, item.line_end) == (1, 3)


def test_text_parser_unstructured_becomes_omission_never_a_record():
    text = "Some chat about lunch.\nMore chatter.\n\nDECISION: Real one.\n"
    result = parser.parse_text(text)
    assert [i.record_type for i in result.items] == ["decision"]
    assert len(result.omissions) == 1
    assert result.omissions[0]["lines"] == "1-2"
    assert "not deterministically classifiable" in result.omissions[0]["detail"]


def test_text_parser_status_and_exactness_tags():
    result = parser.parse_text(
        "DECISION [CONTESTED]: Weekly releases.\n"
        "CONSTRAINT [EXACT]: Keep p95 latency under 250 ms.\n")
    assert result.items[0].status == "CONTESTED"
    assert result.items[1].exactness == "EXACT"


def test_text_parser_unknown_tag_is_an_error():
    with pytest.raises(parser.ParseError, match=r"unknown tag \[URGENT\]"):
        parser.parse_text("DECISION [URGENT]: x.\n")


def test_text_parser_empty_marker_content_is_an_error():
    with pytest.raises(parser.ParseError, match="has no content"):
        parser.parse_text("DECISION:\n")


def test_supersedes_before_any_decision_is_an_error():
    with pytest.raises(parser.ParseError, match="before any DECISION"):
        parser.parse_text("SUPERSEDES: something\n")


def test_expires_attaches_to_previous_record():
    result = parser.parse_text(
        "DECISION [TEMPORARY]: Freeze deploys.\nEXPIRES: 2026-08-01\n")
    assert result.items[0].expiry == "2026-08-01"
    assert result.items[0].status == "TEMPORARY"


# --------------------------------------------------------- jsonl parser
def test_jsonl_typed_records():
    text = json.dumps({"type": "decision", "content": "Use sqlite.",
                       "status": "ACTIVE"}) + "\n" + \
        json.dumps({"type": "stop_condition", "content": "Stop at 3 fails."})
    result = parser.parse_jsonl(text)
    assert [i.record_type for i in result.items] == ["decision", "stop_condition"]


def test_jsonl_message_content_is_scanned_for_markers():
    msg = {"role": "assistant",
           "content": "DECISION: Use sqlite.\nnothing structured here\n"}
    result = parser.parse_jsonl(json.dumps(msg))
    assert [i.record_type for i in result.items] == ["decision"]
    assert len(result.omissions) == 1


def test_jsonl_unknown_object_becomes_unverified_record():
    text = json.dumps({"tool": "bash", "exit": 0})
    result = parser.parse_jsonl(text)
    assert result.items[0].record_type == "unstructured"
    assert result.items[0].status == "UNVERIFIED"
    assert result.warnings  # surfaced, not silent


def test_jsonl_invalid_json_line_is_a_hard_error():
    with pytest.raises(parser.ParseError, match="line 2: invalid JSON"):
        parser.parse_jsonl('{"type": "decision", "content": "x"}\n{oops\n')


def test_jsonl_unknown_type_is_a_hard_error():
    with pytest.raises(parser.ParseError, match="unknown record type 'vibe'"):
        parser.parse_jsonl(json.dumps({"type": "vibe", "content": "x"}))


def test_jsonl_non_object_line_is_a_hard_error():
    with pytest.raises(parser.ParseError, match="must be an object"):
        parser.parse_jsonl('["a", "b"]')


def test_jsonl_bad_status_is_a_hard_error():
    with pytest.raises(parser.ParseError, match="unknown status 'SORTA'"):
        parser.parse_jsonl(
            json.dumps({"type": "decision", "content": "x", "status": "SORTA"}))
