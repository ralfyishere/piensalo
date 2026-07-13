"""Optimizer: grading, verdict comparison, blind judging, extraction."""
from __future__ import annotations

import json

from piensalo.adapters.base import ModelResponse
from piensalo.context import quality
from piensalo.context.extraction import validate_proposals
from piensalo.context.ingest import load_context_text
from piensalo.context.select import chunk_items
from piensalo.verify.contract import convert_task_contract


def _grade_pair(full_reqs, opt_reqs, accepted=True):
    full = {"passed": all(p for _, p in full_reqs),
            "requirements": [{"id": i, "kind": "oracle", "passed": p}
                             for i, p in full_reqs]}
    opt = {"passed": all(p for _, p in opt_reqs),
           "requirements": [{"id": i, "kind": "oracle", "passed": p}
                            for i, p in opt_reqs]}
    return quality.compare_verdict(full, opt, optimized_accepted=accepted)


def test_grade_deterministic_contract_and_oracle():
    contract = convert_task_contract(
        {"required_output_fields": [{"name": "TOTAL", "format": "number"}]})
    g = quality.grade("TOTAL: 12\n", contract=contract,
                      expectations={"must_contain": ["12"],
                                    "must_not_contain": ["oops"],
                                    "field_values": {"TOTAL": "12"}})
    assert g["passed"] is True
    assert g["status"] == "DETERMINISTIC TASK VERIFIED"
    assert len(g["requirements"]) == 4


def test_grade_unmeasured_without_requirements():
    g = quality.grade("anything")
    assert g["passed"] is None
    assert g["status"] == "UNMEASURED"


def test_verdict_maintained_improved_regression_fallback():
    both_pass = [("a", True), ("b", True)]
    assert _grade_pair(both_pass, both_pass) == "MAINTAINED"
    # full failed b, optimized fixed it -> IMPROVED
    assert _grade_pair([("a", True), ("b", False)], both_pass) == "IMPROVED"
    # full passed b, accepted optimized failed it -> REGRESSION, never averaged
    assert _grade_pair(both_pass, [("a", True), ("b", False)]) == "REGRESSION"
    assert _grade_pair(both_pass, both_pass, accepted=False) == "SAFE FALLBACK"


def test_one_regression_is_not_averaged_away():
    full = [("a", True), ("b", True), ("c", False)]
    opt = [("a", True), ("b", False), ("c", True)]  # 1 fix, 1 regression
    assert _grade_pair(full, opt) == "REGRESSION"


class ScriptedJudge:
    provider = "fake-judge"

    def __init__(self, verdicts, model="judge-model-9"):
        self.verdicts = list(verdicts)
        self.requested_model = model
        self.prompts = []

    def complete(self, prompt):
        self.prompts.append(prompt)
        v = self.verdicts.pop(0)
        return ModelResponse(text=f"VERDICT: {v}", requested_model=self.requested_model,
                             resolved_model=self.requested_model,
                             provider=self.provider, tokens_in=10,
                             tokens_out=3)


def test_blind_compare_swaps_order_and_detects_agreement():
    judge = ScriptedJudge(["1", "2"])  # full wins in both orderings
    result = quality.blind_compare(judge, task="t", full_response="FULL",
                                   optimized_response="OPT")
    assert result["orderings_run"] == 2
    assert result["agreed"] is True and result["winner"] == "full"
    assert result["judge_resolved_model"] == "judge-model-9"
    assert "weak evidence" in result["note"]
    # Order actually swapped between calls.
    assert judge.prompts[0].index("FULL") < judge.prompts[0].index("OPT")
    assert judge.prompts[1].index("OPT") < judge.prompts[1].index("FULL")


def test_blind_compare_records_disagreement_instead_of_resolving_it():
    judge = ScriptedJudge(["1", "1"])  # position-biased judge
    result = quality.blind_compare(judge, task="t", full_response="FULL",
                                   optimized_response="OPT")
    assert result["agreed"] is False
    assert result["winner"] == "disagreement"


# ------------------------------------------------------------ extraction
def _chunks():
    items = load_context_text(
        "We firmly agreed to keep the API v1 compatible forever.\n\n"
        "Random chat about lunch options near the office.\n")
    return {c.id: c for c in chunk_items(items)}


def test_extraction_accepts_only_verbatim_quotes():
    chunks = _chunks()
    cid = next(i for i, c in chunks.items()
               if "API v1" in c.content)
    proposals = json.dumps([
        {"chunk_id": cid, "record_type": "invariant",
         "content": "keep the API v1 compatible forever",
         "confidence": 0.9, "exactness": "SEMANTIC", "status": "ACTIVE",
         "reason": "compatibility promise"},
        {"chunk_id": cid, "record_type": "invariant",
         "content": "the API must stay compatible",  # paraphrase
         "confidence": 0.9, "exactness": "SEMANTIC", "status": "ACTIVE",
         "reason": "paraphrased"},
        {"chunk_id": "block-000000000000", "record_type": "decision",
         "content": "anything", "confidence": 0.5, "exactness": "SEMANTIC",
         "status": "ACTIVE", "reason": "invented span"},
        {"chunk_id": cid, "record_type": "vibe", "content": "keep",
         "confidence": 0.5, "exactness": "SEMANTIC", "status": "ACTIVE",
         "reason": "bad type"},
    ])
    accepted, rejected = validate_proposals(proposals, chunks,
                                            model_provenance="m-x")
    assert len(accepted) == 1
    assert accepted[0]["model_provenance"] == "m-x"
    assert accepted[0]["source"]["content_hash"]
    reasons = " | ".join(r["reason"] for r in rejected)
    assert "paraphrase rejected" in reasons
    assert "invented source span" in reasons
    assert "illegal record_type" in reasons


def test_extraction_unparseable_payload_rejected_wholesale():
    accepted, rejected = validate_proposals("I think the key decision is...",
                                            _chunks(), model_provenance="m")
    assert accepted == []
    assert "unparseable" in rejected[0]["reason"]


def test_extraction_never_proposes_superseded_or_active_upgrade_beyond_rules():
    chunks = _chunks()
    cid = next(iter(chunks))
    proposals = json.dumps([
        {"chunk_id": cid, "record_type": "decision",
         "content": chunks[cid].content[:20], "confidence": 1.5,
         "exactness": "SEMANTIC", "status": "ACTIVE", "reason": "conf oob"},
        {"chunk_id": cid, "record_type": "decision",
         "content": chunks[cid].content[:20], "confidence": 0.9,
         "exactness": "SEMANTIC", "status": "SUPERSEDED",
         "reason": "model may not declare supersession"},
    ])
    accepted, rejected = validate_proposals(proposals, chunks,
                                            model_provenance="m")
    assert accepted == []
    assert len(rejected) == 2
