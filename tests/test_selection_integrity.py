"""Selection-integrity layer (NR-9 guard): grounding verdicts, minimum
expansion, supersession truth, and full-context fallback.

Regression source: cortex-value tasks 05/06 — the optimizer shipped
superseded or template values because required-value provenance was never
checked against the selection.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from piensalo.adapters.base import ModelAdapter, ModelResponse
from piensalo.context import integrity
from piensalo.context.ingest import load_context_text
from piensalo.context.runtime import run_optimized
from piensalo.verify import contract as contract_mod


@dataclass
class Chunk:
    id: str
    content: str
    tokens: int = 10
    disposition: str = "OMITTED_LOW_RELEVANCE"
    kind: str = "prose"
    status: str = ""
    record_type: str = ""
    reason: str = ""


@dataclass
class Sel:
    chunks: list = field(default_factory=list)
    selected_tokens: int = 0


def _contract(*names):
    return contract_mod.convert_task_contract(
        {"required_output_fields": [{"name": n} for n in names]})


# ------------------------------------------------------------- verdicts

def test_unsupported_when_candidates_exist_but_none_selected():
    sel = Sel([Chunk("c1", "the port registry allocation is 9443")])
    rep = integrity.evaluate(_contract("PORT"), sel)
    assert rep["requirements"]["PORT"]["verdict"] == "UNSUPPORTED"
    assert rep["all_supported"] is False


def test_ambiguous_when_old_value_selected_current_omitted():
    # The exact 05 failure shape: an early mention is in the packet, the
    # final-value paragraph is omitted.
    sel = Sel([
        Chunk("old", "draft version 2.4.0 appears in the notes",
              disposition="INCLUDED_RELEVANT"),
        Chunk("new", "the version that will be tagged is 2.4.1"),
    ])
    rep = integrity.evaluate(_contract("VERSION"), sel)
    assert rep["requirements"]["VERSION"]["verdict"] == "AMBIGUOUS"
    assert rep["requirements"]["VERSION"]["missing_chunks"] == ["new"]


def test_supported_only_when_all_candidates_in_packet():
    sel = Sel([
        Chunk("a", "port moved to 8443 earlier", disposition="INCLUDED_RELEVANT"),
        Chunk("b", "final port is 9443", disposition="INCLUDED_RELEVANT"),
    ])
    rep = integrity.evaluate(_contract("PORT"), sel)
    assert rep["requirements"]["PORT"]["verdict"] == "SUPPORTED"
    assert rep["all_supported"] is True


def test_unmeasured_when_no_lexical_candidate_exists():
    # 06 shape: the field name 'DB' never appears as a word in the notes.
    sel = Sel([Chunk("x", "the analytics store is postgres",
                     disposition="INCLUDED_RELEVANT")])
    rep = integrity.evaluate(_contract("DB"), sel)
    assert rep["requirements"]["DB"]["verdict"] == "UNMEASURED"
    assert rep["all_supported"] is False  # UNMEASURED never counts as support


def test_superseded_only_marker_records():
    sel = Sel([
        Chunk("d1", "DECISION: retention is 90 days", kind="marker_record",
              status="SUPERSEDED", record_type="decision",
              disposition="INCLUDED_RELEVANT"),
        Chunk("d2", "DECISION: retention is 30 days", kind="marker_record",
              status="ACTIVE", record_type="decision"),
    ])
    rep = integrity.evaluate(_contract("RETENTION"), sel)
    assert rep["requirements"]["RETENTION"]["verdict"] == "SUPERSEDED_ONLY"


def test_conflicted_two_active_decisions_selected():
    sel = Sel([
        Chunk("d1", "DECISION: region is us-east-1", kind="marker_record",
              status="ACTIVE", record_type="decision",
              disposition="INCLUDED_RELEVANT"),
        Chunk("d2", "DECISION: region is eu-west-1", kind="marker_record",
              status="ACTIVE", record_type="decision",
              disposition="INCLUDED_RELEVANT"),
    ])
    rep = integrity.evaluate(_contract("REGION"), sel)
    assert rep["requirements"]["REGION"]["verdict"] == "CONFLICTED"


def test_minimum_expansion_lists_only_missing_candidates():
    sel = Sel([
        Chunk("in", "version note one", disposition="INCLUDED_RELEVANT"),
        Chunk("out1", "version final paragraph"),
        Chunk("unrelated", "the office plants died"),
    ])
    rep = integrity.evaluate(_contract("VERSION"), sel)
    assert integrity.expansion_ids(rep, sel) == ["out1"]


def test_extra_ids_promote_to_supported():
    sel = Sel([
        Chunk("in", "date proposal one", disposition="INCLUDED_RELEVANT"),
        Chunk("out", "the committed date paragraph"),
    ])
    rep = integrity.evaluate(_contract("DATE"), sel)
    assert rep["all_supported"] is False
    rep2 = integrity.evaluate(_contract("DATE"), sel, extra_ids=("out",))
    assert rep2["requirements"]["DATE"]["verdict"] == "SUPPORTED"


def test_no_contract_gate_vacuously_open():
    rep = integrity.evaluate(None, Sel([]))
    assert rep["all_supported"] is True


# ------------------------------------------- end-to-end runtime behavior

class ValueSensitiveAdapter(ModelAdapter):
    """Answers with the current value ONLY when its paragraph is in the
    prompt — the exact wrong-value mechanism from tasks 05/06."""

    provider = "mock"

    def complete(self, prompt: str) -> ModelResponse:
        text = ("VERSION: 2.4.1" if "actually tagged is 2.4.1" in prompt
                else "VERSION: 2.4.0")
        return ModelResponse(text=text, requested_model=self.requested_model,
                             resolved_model=self.requested_model,
                             provider="mock", tokens_in=len(prompt) // 4,
                             tokens_out=4, wall_seconds=0.0)


_CTX = (
    "The changelog draft briefly said 2.4.0 before the branch cut; that "
    "version note is obsolete and hand-edited.\n\n"
    "Completely unrelated paragraph about the conference booth artwork, "
    "tablets, banners and a long tangent that scores high on nothing.\n\n"
    "The version that will be actually tagged is 2.4.1, confirmed twice."
)


def test_runtime_integrity_prevents_wrong_value_acceptance():
    """With the guard, the runtime must never accept a packet that cannot
    ground VERSION in every candidate paragraph: it expands or falls back,
    and the final answer carries the current value."""
    items = load_context_text(_CTX, name="t")
    rr = run_optimized(
        task_text="State the final version. Output exactly one line: "
                  "VERSION: <x.y.z>",
        items=items, budget=200, adapter=ValueSensitiveAdapter("m"),
        contract=_contract("VERSION"), fallback="run")
    assert rr.integrity is not None
    assert rr.integrity["preflight_expansion_rounds"] >= 1  # guard engaged
    assert rr.response_text == "VERSION: 2.4.1"
    # Either the packet was integrity-expanded to include the 2.4.1
    # paragraph, or the runtime fell back to full context — both are safe;
    # accepting 2.4.0 (the pre-repair behavior) is the regression.
    assert rr.outcome in ("OPTIMIZED CONTEXT ACCEPTED",
                          "SAFE FALLBACK (EXECUTED)")


def test_runtime_integrity_fallback_when_budget_cannot_hold_evidence():
    """If the candidates cannot fit the budget, integrity must trigger a
    full-context fallback rather than ship an under-grounded packet."""
    items = load_context_text(_CTX, name="t")
    rr = run_optimized(
        task_text="State the final version. Output exactly one line: "
                  "VERSION: <x.y.z>",
        items=items, budget=40, adapter=ValueSensitiveAdapter("m"),
        contract=_contract("VERSION"), fallback="run")
    # Budget 40 cannot hold both version paragraphs + task envelope.
    assert rr.outcome in ("SAFE FALLBACK (EXECUTED)",
                          "OPTIMIZATION REJECTED — FULL CONTEXT REQUIRED")
    if rr.outcome == "SAFE FALLBACK (EXECUTED)":
        assert rr.response_text == "VERSION: 2.4.1"
