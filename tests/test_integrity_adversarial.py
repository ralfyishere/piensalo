"""Adversarial deterministic tests for the safety repairs (release review).

Each scenario probes a way the integrity / acceptance / routing layers could
overclaim or misfire. The invariant under test everywhere: **lexical evidence
is never called semantic truth** — where deterministic support cannot be
established the layer must say AMBIGUOUS / CONFLICTED / UNMEASURED and expand
or fall back safely, and known limitation classes are pinned down explicitly
rather than hidden.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from piensalo.context import integrity
from piensalo.gateway.protocol import ContentBlock, Message, NormalizedRequest
from piensalo.gateway.router import CortexRouter, extract_features
from piensalo.verify import contract as contract_mod
from piensalo.verify.acceptance import evaluate_repair


@dataclass
class C:
    id: str
    content: str
    tokens: int = 10
    disposition: str = "OMITTED_LOW_RELEVANCE"
    kind: str = "prose"
    status: str = ""
    record_type: str = ""
    reason: str = ""


@dataclass
class S:
    chunks: list = field(default_factory=list)
    selected_tokens: int = 0


def K(*names):
    return contract_mod.convert_task_contract(
        {"required_output_fields": [{"name": n} for n in names]})


def _req(text):
    return NormalizedRequest(model="m", messages=[
        Message(role="user", content=[ContentBlock(type="text", text=text)])])


# 1 — same field label, two conflicting values, both selected.
def test_conflicting_prose_values_both_in_view_is_supported_not_truth():
    """SUPPORTED here means 'all lexical evidence is in the packet' — the
    model sees the same conflicting mentions a full-context run would. The
    report must carry the honest evidence-type label, never semantic truth."""
    s = S([C("a", "the port is 8080", disposition="INCLUDED_RELEVANT"),
           C("b", "the port is 9443", disposition="INCLUDED_RELEVANT")])
    rep = integrity.evaluate(K("PORT"), s)
    assert rep["requirements"]["PORT"]["verdict"] == "SUPPORTED"
    assert rep["evidence_type"] == "lexical-stem"
    assert "never semantic truth" in rep["note"]


# 2 — current value expressed only through a paraphrase.
def test_paraphrase_only_grounding_is_unmeasured_never_supported():
    s = S([C("a", "we ship on the fifteenth of September",
             disposition="INCLUDED_RELEVANT")])
    rep = integrity.evaluate(K("DATE"), s)
    assert rep["requirements"]["DATE"]["verdict"] == "UNMEASURED"
    assert rep["all_supported"] is False  # forces expansion/fallback path


# 3 — wrong value sits near the correct field name; another mention omitted.
def test_wrong_value_near_field_name_with_omitted_mention_is_ambiguous():
    s = S([C("a", "port 8443 collides with the ingress controller",
             disposition="INCLUDED_RELEVANT"),
           C("b", "the final port allocation is 9443")])
    rep = integrity.evaluate(K("PORT"), s)
    assert rep["requirements"]["PORT"]["verdict"] == "AMBIGUOUS"
    assert rep["requirements"]["PORT"]["missing_chunks"] == ["b"]


# 4 — correct value appears only in a superseded chunk.
def test_active_selected_with_superseded_history_omitted_stays_conservative():
    s = S([C("d1", "DECISION: retention 30 days", kind="marker_record",
             status="ACTIVE", record_type="decision",
             disposition="INCLUDED_RELEVANT"),
           C("d2", "DECISION: retention 90 days", kind="marker_record",
             status="SUPERSEDED", record_type="decision")])
    rep = integrity.evaluate(K("RETENTION"), s)
    # Conservative: history off-packet -> AMBIGUOUS (expand), never a silent
    # SUPPORTED that hides the supersession chain.
    assert rep["requirements"]["RETENTION"]["verdict"] == "AMBIGUOUS"


def test_only_superseded_selected_is_never_current_support():
    s = S([C("d1", "DECISION: retention 90 days", kind="marker_record",
             status="SUPERSEDED", record_type="decision",
             disposition="INCLUDED_RELEVANT"),
           C("d2", "DECISION: retention 30 days", kind="marker_record",
             status="ACTIVE", record_type="decision")])
    rep = integrity.evaluate(K("RETENTION"), s)
    assert rep["requirements"]["RETENTION"]["verdict"] == "SUPERSEDED_ONLY"


# 5 — multiple selected chunks disagreeing (marker records).
def test_two_selected_active_decisions_conflict():
    s = S([C("d1", "DECISION: region us-east-1", kind="marker_record",
             status="ACTIVE", record_type="decision",
             disposition="INCLUDED_RELEVANT"),
           C("d2", "DECISION: region eu-west-1", kind="marker_record",
             status="ACTIVE", record_type="decision",
             disposition="INCLUDED_RELEVANT")])
    rep = integrity.evaluate(K("REGION"), s)
    assert rep["requirements"]["REGION"]["verdict"] == "CONFLICTED"
    assert rep["all_supported"] is False


# 6 — requirement with no deterministically extractable grounding at all.
def test_no_grounding_anywhere_is_unmeasured_and_blocks_optimization():
    s = S([C("a", "the analytics store is postgres",
             disposition="INCLUDED_RELEVANT")])
    rep = integrity.evaluate(K("DB"), s)
    assert rep["requirements"]["DB"]["verdict"] == "UNMEASURED"
    assert rep["all_supported"] is False
    assert integrity.expansion_ids(rep, s) == []  # nothing to expand: fallback


# 7 — exact-delivery instruction without the original trigger phrases.
def test_extended_exact_delivery_phrasings_fire():
    for text in ("Respond with the JSON object alone.",
                 "Give me just the function, skip commentary.",
                 "Your entire reply must be the three-line poem."):
        assert extract_features(_req(text))["exact_delivery_contract"] is True, text


def test_novel_phrasing_can_still_miss_documented_limitation():
    """The lexical trigger set cannot be exhaustive. A miss means THINK
    applies as before (pre-repair status quo) — documented, not hidden."""
    f = extract_features(_req("Keep your response to a bare minimum answer."))
    assert f["exact_delivery_contract"] is False


# 8 — exact-format language inside QUOTED source material.
def test_quoted_exact_format_fires_signal_benign_false_positive():
    """Known limitation: quoted spec text trips the signal. The failure mode
    is THINK *abstention* on a task that didn't need suppression — measured
    safe (skipping THINK never damaged a task in the frozen runs), unlike the
    inverse error. Pinned here so a future change is a conscious decision."""
    t = ('Summarize the spec below in one paragraph.\n'
         'The spec says: "output exactly three lines and nothing else".')
    f = extract_features(_req(t))
    assert f["exact_delivery_contract"] is True
    d = CortexRouter().decide(_req(t))
    assert "THINK" not in d.decision


# acceptance: quoted/decorated repair of an already-broken draft must still
# never smuggle in delivery damage.
def test_acceptance_never_trades_one_violation_for_another():
    contract = contract_mod.convert_task_contract(
        {"required_output_fields": [{"name": "A"}, {"name": "B"}],
         "no_extra_lines": True})
    broken = "A: 1"                       # B missing
    swapped = "B: 2"                      # fixes B, loses A
    res = evaluate_repair(contract, broken, swapped)
    assert res["accept"] is False
    assert res["verdict"] == "REJECTED_REGRESSION"
    assert res["output"] == broken
