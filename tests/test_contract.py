"""Contract adapter tests: conversion, check, emit, normalize."""
from __future__ import annotations

import json

from piensalo.verify.contract import (
    check,
    convert_task_contract,
    emit,
    load_task_contract,
    normalize,
)


def test_convert_required_output_fields():
    contract = convert_task_contract(
        {
            "required_output_fields": [
                {"name": "ANSWER", "format": "number"},
                {"name": "NOTES", "format": "text"},
            ],
            "order_required": True,
        }
    )
    assert [f["name"] for f in contract["fields"]] == ["ANSWER", "NOTES"]
    assert contract["fields"][0]["pattern"] == r"^ANSWER:"
    assert contract["exact_format"] is True
    assert contract["final_line"] == "NOTES"


def test_load_task_contract_from_file(tmp_path):
    p = tmp_path / "contract.json"
    p.write_text(
        json.dumps({"required_output_fields": [{"name": "TOTAL", "format": "number"}]}),
        encoding="utf-8",
    )
    contract = load_task_contract(str(p))
    assert contract["fields"][0]["name"] == "TOTAL"
    assert contract["exact_format"] is False


def test_internal_form_passthrough():
    internal = {"fields": [{"name": "X", "pattern": r"^X:", "required": True}]}
    assert convert_task_contract(internal) is internal


def test_check_detects_missing_and_decorated_fields():
    contract = convert_task_contract(
        {"required_output_fields": [{"name": "ANSWER", "format": "n"}]}
    )
    missing = check(contract, "some prose without the field")
    assert missing["all_present"] is False
    assert missing["missing"][0]["field"] == "ANSWER"

    decorated = check(contract, "**ANSWER: 42**")
    assert decorated["all_present"] is True
    assert decorated["present"][0]["recoverable_by_normalize"] is True


def test_exact_format_rejects_decoration():
    contract = convert_task_contract(
        {
            "required_output_fields": [{"name": "ANSWER", "format": "n"}],
            "no_extra_lines": True,
        }
    )
    result = check(contract, "**ANSWER: 42**")
    assert result["all_present"] is False  # exact contracts judge raw text only


def test_normalize_only_when_not_exact():
    non_exact = {"fields": [{"name": "A", "pattern": r"^A:", "required": True}]}
    assert normalize(non_exact, "**A: 1**") == "A: 1"
    exact = dict(non_exact, exact_format=True)
    assert normalize(exact, "**A: 1**") == "**A: 1**"  # untouched


def test_emit_mentions_fields_and_exactness():
    contract = {
        "fields": [{"name": "A", "pattern": r"^A:", "required": True}],
        "exact_format": True,
        "final_line": "A",
    }
    block = emit(contract)
    assert "'A'" in block
    assert "VERBATIM" in block
    assert "LAST line" in block
