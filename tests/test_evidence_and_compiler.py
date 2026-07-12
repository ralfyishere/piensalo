"""Evidence-record loader and compiler tests."""
from __future__ import annotations

import json

import pytest

from piensalo.compiler import compile_program, select_operations
from piensalo.core import load_operations, operation_names
from piensalo.evidence import MechanismRecord, load_evidence_file

RECORD = {
    "mechanism": "post-draft-scanner",
    "version": "2.0",
    "intended_effect": "select a repair only for demonstrated defects",
    "trigger": "a draft exists",
    "counterindications": ["no draft yet"],
    "models_tested": ["example-model"],
    "task_classes": ["procedural"],
    "trials": 24,
    "result": "abstained correctly on clean drafts",
    "negative_transfer": "none observed",
    "cost": "negligible",
    "known_confounds": ["dev-split validation only"],
    "evidence_level": "DEV_VALIDATED",
    "verdict": "keep",
    "next_kill_test": "held-out rerun with frozen constants",
}


def test_mechanism_record_roundtrip():
    rec = MechanismRecord.from_dict(RECORD)
    assert rec.to_dict() == RECORD


def test_mechanism_record_rejects_bad_level():
    with pytest.raises(ValueError):
        MechanismRecord.from_dict(dict(RECORD, evidence_level="PROVEN"))


def test_load_evidence_file(tmp_path):
    md = tmp_path / "EVIDENCE.md"
    md.write_text(
        "# Evidence\n\n```json\n" + json.dumps(RECORD) + "\n```\n\nProse follows.\n",
        encoding="utf-8",
    )
    records = load_evidence_file(md)
    assert len(records) == 1
    assert records[0].mechanism == "post-draft-scanner"


def test_core_has_eleven_operations_with_correct_evidence_status():
    ops = load_operations()
    assert len(ops) == 11
    tested = {"inspect_result", "classify_failure", "apply_targeted_repair", "verify"}
    for op in ops:
        expected = "EXPERIMENTALLY_TESTED" if op["name"] in tested else "DESIGNED"
        assert op["evidence_status"] == expected, op["name"]
        assert 3 <= len(op["procedure"]) <= 6, op["name"]


def test_compile_program_modes():
    task = "Compute 5% compounded per month over 12 months. You must not use estimates."
    packet = compile_program(task, mode="packet")
    assert packet["schema"] == "piensalo/program/v1"
    assert packet["task_analysis"]["has_numeric_work"] is True
    assert packet["task_analysis"]["constraints"]

    prompt = compile_program(task, mode="prompt")
    assert "## Task" in prompt
    assert "Stop condition:" in prompt

    prose = compile_program(task, mode="prose")
    assert "Cognitive program" in prose

    with pytest.raises(ValueError):
        compile_program(task, mode="haiku")


def test_select_operations_explicit_and_heuristic():
    explicit = select_operations("anything", names=["verify", "deliver"])
    assert [op["name"] for op in explicit] == ["verify", "deliver"]
    with pytest.raises(KeyError):
        select_operations("anything", names=["not-an-op"])
    # Heuristic selection preserves canonical order.
    names = [op["name"] for op in select_operations("Short task.")]
    canonical = operation_names()
    assert names == [n for n in canonical if n in set(names)]
