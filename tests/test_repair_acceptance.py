"""Contract-gated repair acceptance (NR-10 guard).

Regression source: cortex-value task 11 — a compliant draft was 'repaired'
into a fenced, instruction-echoing block and the scanner's own defect count
accepted it. The contract is the judge now; the detector never is.
"""
from __future__ import annotations

from piensalo.verify import contract as contract_mod
from piensalo.verify.acceptance import evaluate_repair


def _contract():
    c = contract_mod.convert_task_contract(
        {"required_output_fields": [{"name": n} for n in
                                    ("STATUS", "OWNER", "DEADLINE", "TICKET")],
         "no_extra_lines": True})
    return c


_GOOD = ("STATUS: APPROVED\nOWNER: platform-security\n"
         "DEADLINE: 2026-08-01\nTICKET: SEC-4211")

# The exact task-11 failure artifact: values intact, fenced + echoed text.
_FENCED_ECHO = ("```\n" + _GOOD + "\n\n# disqualifier-scan\n\n"
                "**Trigger (observable):** The task defines pass/fail "
                "conditions...\n```")


def test_task11_regression_compliant_draft_preserved_byte_for_byte():
    res = evaluate_repair(_contract(), _GOOD, _FENCED_ECHO)
    assert res["accept"] is False
    assert res["verdict"] == "CORRECT_ABSTENTION"
    assert res["output"] == _GOOD  # byte-for-byte original


def test_repair_rejected_when_format_regresses():
    broken = _GOOD.replace("TICKET: SEC-4211", "")  # a demonstrated failure
    repaired_but_fenced = "```\n" + _GOOD + "\n```"
    res = evaluate_repair(_contract(), broken, repaired_but_fenced)
    assert res["accept"] is False
    assert res["verdict"] == "REJECTED_DELIVERY_DAMAGE"
    assert res["output"] == broken


def test_repair_rejected_when_passing_field_regresses():
    broken = _GOOD.replace("TICKET: SEC-4211", "")
    repaired_lost_owner = ("STATUS: APPROVED\nDEADLINE: 2026-08-01\n"
                           "TICKET: SEC-4211")
    res = evaluate_repair(_contract(), broken, repaired_lost_owner)
    assert res["accept"] is False
    assert res["verdict"] == "REJECTED_REGRESSION"
    assert res["output"] == broken


def test_repair_accepted_only_on_strict_contract_improvement():
    broken = _GOOD.replace("TICKET: SEC-4211", "")
    res = evaluate_repair(_contract(), broken, _GOOD)
    assert res["accept"] is True
    assert res["verdict"] == "ACCEPTED"
    assert res["output"] == _GOOD
    assert res["before"]["violations"] > res["after"]["violations"]


def test_no_improvement_is_rejected():
    broken = _GOOD.replace("TICKET: SEC-4211", "")
    res = evaluate_repair(_contract(), broken, broken + "\nstill no ticket")
    assert res["accept"] is False
    assert res["verdict"] in ("REJECTED_NO_IMPROVEMENT",
                              "REJECTED_DELIVERY_DAMAGE")
    assert res["output"] == broken


def test_no_contract_means_no_sole_judge_detector():
    res = evaluate_repair(None, "original", "repaired")
    assert res["accept"] is False
    assert res["verdict"] == "UNMEASURED"
    assert res["output"] == "original"
