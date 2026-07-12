"""Scanner tests: defect detection, selection, and abstention."""
from __future__ import annotations

from piensalo.inspect.scanner import ACTIVATE, pretask_triggers, scan
from piensalo.verify.contract import check, convert_task_contract

TASK_CONTRACT = {
    "required_output_fields": [
        {"name": "ANSWER", "format": "number"},
        {"name": "CONFIDENCE", "format": "0-1"},
    ],
    "no_extra_lines": True,
}


def test_stalled_draft_missing_deliverable_detected():
    """A stalled draft (analysis but no required fields) with a
    task-contract-style contract must fire missing-deliverable."""
    task = "Compute the answer. Output ANSWER: and CONFIDENCE: lines exactly."
    draft = "I started analyzing the problem and found several considerations..."
    result = scan(task, draft, contract=TASK_CONTRACT, max_repairs=1)
    assert "missing-deliverable" in result["defects_detected"]
    assert result["selected_repairs"] == ["final-answer-completeness"]
    assert result["no_repair_needed"] is False
    assert any("ANSWER" in e for e in result["evidence_from_draft"])
    # Candidate scores carry the evidence and clear the threshold.
    top = result["candidate_scores"][0]
    assert top["selected"] is True
    assert top["value"] >= ACTIVATE


def test_contract_check_result_also_accepted():
    """scan() accepts a pre-computed check result too."""
    draft = "no fields here"
    pre = check(convert_task_contract(TASK_CONTRACT), draft)
    result = scan("task", draft, contract=pre)
    assert "missing-deliverable" in result["defects_detected"]


def test_clean_draft_abstains():
    task = "Write a short greeting."
    draft = "Hello! Here is the greeting you asked for."
    result = scan(task, draft, contract=None)
    assert result["no_repair_needed"] is True
    assert result["selected_repairs"] == []
    assert result["verification_target"] is None


def test_mid_confidence_defect_fires_after_recalibration():
    """A genuine procedural defect (conf ~0.55) must clear the recalibrated
    threshold instead of being swallowed by flat penalties."""
    task = "Two reports conflict about the outage window. Reconcile and answer."
    draft = "The outage lasted two hours. That is the answer."
    result = scan(task, draft)
    assert "unresolved-contradiction" in result["defects_detected"]
    assert "contradiction-resolution" in result["selected_repairs"]


def test_pretask_triggers_are_structural():
    hits = pretask_triggers("Interest is compounded at 2% per month over 12 months.")
    assert any(h["skill"] == "rederive-the-numbers" for h in hits)
    assert pretask_triggers("Write a poem about autumn.") == []
