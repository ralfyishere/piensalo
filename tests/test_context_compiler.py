"""Context MVP: compiler — determinism, supersession, exactness, budget."""
from __future__ import annotations

import json

import pytest

from piensalo.context import schema
from piensalo.context.compiler import CompileError, compile_capsule
from piensalo.context.tokens import estimate_tokens

FULL = """\
OBJECTIVE: Ship the widget service alpha.
SUCCESS CONDITION: All tests pass on CI.

Unstructured planning chatter that resists classification.

DECISION: Use the PIENSALO organization for hosting.
DECISION: Use ralfyishere because personal creator attribution is the strategy.
SUPERSEDES: Use the PIENSALO organization for hosting.
DECISION [CONTESTED]: Adopt a weekly release cadence.
DECISION [TEMPORARY]: Freeze dependency upgrades during the alpha.
EXPIRES: 2026-09-01
DECISION [EXPIRED]: Target Python 3.9 support.
DECISION [UNVERIFIED]: Marketing wants a rename, reportedly.
CONSTRAINT: Never force-push to main.
CONSTRAINT [EXACT]: Keep p95 latency under 250 ms.
INVARIANT: The core stays dependency-free.
STOP CONDITION: Stop if the suite fails twice in a row.
COMPLETED: Implemented the schema module.
FAILED APPROACH: Global singleton state; caused test pollution.
ARTIFACT: src/widget/core.py
ARTIFACT: commit 0feb1234abcd5678
OPEN QUESTION: Should the parser accept YAML?
OPEN ACTION: Write the diff renderer.
NEXT ACTION: Run `uv run pytest -q` and fix the first failure.
"""


def _compile(text: str = FULL, budget: int = 5000, **kw):
    kw.setdefault("fmt", "text")
    kw.setdefault("goal", "continue the project")
    return compile_capsule(text, token_budget=budget, **kw)


def test_repeated_compilation_is_byte_identical():
    a, b = _compile(), _compile()
    assert schema.canonical_json(a.capsule) == schema.canonical_json(b.capsule)
    assert a.resume_md == b.resume_md
    assert schema.canonical_json(a.verification) == schema.canonical_json(b.verification)
    assert a.capsule["capsule_id"] == b.capsule["capsule_id"]


def test_supersession_active_vs_historical_truth():
    capsule = _compile().capsule
    by_content = {d["content"]: d for d in capsule["decisions"]}
    old = by_content["Use the PIENSALO organization for hosting."]
    new = by_content[
        "Use ralfyishere because personal creator attribution is the strategy."]
    assert old["status"] == "SUPERSEDED"          # never deleted
    assert new["status"] == "ACTIVE"
    assert new["supersedes"] == old["id"]
    assert old["superseded_by"] == new["id"]


def test_superseded_never_rendered_as_current():
    result = _compile()
    assert "Use the PIENSALO organization" not in result.resume_md
    assert "Use ralfyishere" in result.resume_md


def test_all_six_decision_states_representable():
    capsule = _compile().capsule
    statuses = {d["status"] for d in capsule["decisions"]}
    assert statuses == {"ACTIVE", "SUPERSEDED", "CONTESTED", "TEMPORARY",
                        "EXPIRED", "UNVERIFIED"}


def test_temporary_decision_carries_expiry():
    capsule = _compile().capsule
    temp = [d for d in capsule["decisions"] if d["status"] == "TEMPORARY"][0]
    assert temp["expiry"] == "2026-09-01"


def test_exact_strings_survive_byte_for_byte():
    result = _compile()
    text = schema.canonical_json(result.capsule)
    for exact in (
        "src/widget/core.py",                       # exact filename
        "commit 0feb1234abcd5678",                  # exact commit hash
        "Run `uv run pytest -q` and fix the first failure.",  # exact command
        "Keep p95 latency under 250 ms.",           # exact numerical value
        "Stop if the suite fails twice in a row.",  # exact stop condition
    ):
        assert exact in text
        assert exact in result.resume_md


def test_windows_style_paths_survive_unmangled():
    text = "ARTIFACT: C:\\repo\\src\\main.py\nNEXT ACTION: open it.\n"
    result = _compile(text)
    assert "C:\\repo\\src\\main.py" in result.resume_md
    raw = schema.canonical_json(result.capsule)
    assert "C:\\\\repo\\\\src\\\\main.py" in raw  # JSON-escaped, byte-stable


def test_unstructured_content_is_omitted_honestly_not_invented():
    capsule = _compile().capsule
    kinds = [o["kind"] for o in capsule["known_omissions"]]
    assert "unstructured" in kinds
    assert all(d["content"] != "Unstructured planning chatter that resists "
               "classification." for d in capsule["decisions"])


def test_unresolved_supersession_is_surfaced():
    text = ("DECISION: New direction.\n"
            "SUPERSEDES: A decision that was never recorded.\n")
    result = _compile(text)
    kinds = [o["kind"] for o in result.capsule["known_omissions"]]
    assert "unresolved_supersession" in kinds
    assert any("unresolved SUPERSEDES" in n
               for n in result.capsule["risk"]["notes"])


def test_last_objective_wins_earlier_kept_by_reference():
    text = ("OBJECTIVE: First objective.\n"
            "OBJECTIVE: Second, current objective.\n")
    capsule = _compile(text).capsule
    assert capsule["mission"]["objective"] == "Second, current objective."
    assert any(o["kind"] == "earlier_objective"
               for o in capsule["known_omissions"])


def test_source_and_record_references_are_content_addressed():
    capsule = _compile().capsule
    assert capsule["source_hash"] == schema.sha256_text(FULL)
    ref = capsule["references"]["transcript"]
    assert set(ref) == set(schema.REFERENCE_FIELDS)
    rec = capsule["decisions"][0]
    assert rec["source_reference"]["artifact_id"] == "transcript"
    assert rec["source_reference"]["location"].startswith("lines:")


def test_metrics_report_estimates_only_no_savings_claim():
    m = _compile().capsule["metrics"]
    assert m["original_tokens_est"] == estimate_tokens(FULL)
    assert "estimate" in m["token_estimator"]
    assert "UNMEASURED" in m["net_savings"]
    assert "not automatically" in m["net_savings"]


def test_insufficient_budget_refuses_honestly():
    result = _compile(budget=40)
    assert result.refused
    assert "COMPILATION REFUSED" in result.resume_md
    assert "REQUIRES EXPANSION" in result.resume_md
    assert result.verification["verdict"] == "REQUIRES EXPANSION"
    # The capsule itself remains complete: nothing was silently lost.
    assert schema.validate_capsule(result.capsule) == []
    assert any(d["content"].startswith("Use ralfyishere")
               for d in result.capsule["decisions"])


def test_budget_trimming_drops_documented_sections_first():
    generous = _compile()
    full_tokens = estimate_tokens(generous.resume_md)
    tight = _compile(budget=full_tokens - 5)
    assert not tight.refused, "trimming droppable sections must fit -5 tokens"
    kinds = [o["kind"] for o in tight.capsule["known_omissions"]]
    assert "budget_omission" in kinds
    # Critical truth still present after trimming.
    assert "Use ralfyishere" in tight.resume_md
    assert "Never force-push to main." in tight.resume_md


def test_project_state_is_carried_and_referenced():
    ps_text = json.dumps({"branch": "context-mvp", "tests": 88})
    result = _compile(project_state=json.loads(ps_text),
                      project_state_text=ps_text)
    assert result.capsule["state"] == {"branch": "context-mvp", "tests": 88}
    assert "project_state" in result.capsule["references"]


def test_model_fields_are_optional_metadata_only():
    plain = _compile()
    assert plain.capsule["compiled_for"]["source_model"] is None
    assert plain.capsule["compiled_for"]["target_model"] is None
    tagged = _compile(source_model="some-model-a", target_model="some-model-b")
    assert tagged.capsule["compiled_for"]["source_model"] == "some-model-a"
    # Metadata does not change any record or the mission.
    assert tagged.capsule["decisions"] == plain.capsule["decisions"]
    assert tagged.capsule["mission"] == plain.capsule["mission"]


def test_empty_goal_and_bad_budget_are_errors():
    with pytest.raises(CompileError, match="--goal"):
        compile_capsule(FULL, fmt="text", goal="  ", token_budget=100)
    with pytest.raises(CompileError, match="must be positive"):
        compile_capsule(FULL, fmt="text", goal="g", token_budget=0)


def test_jsonl_and_text_transcripts_both_compile():
    jsonl = "\n".join([
        json.dumps({"type": "objective", "content": "Ship it."}),
        json.dumps({"role": "assistant",
                    "content": "DECISION: Use sqlite.\nfree prose\n"}),
        json.dumps({"tool_use": "bash", "output": "ok"}),
        json.dumps({"type": "next_action", "content": "Run the demo."}),
    ])
    result = _compile(jsonl, fmt="jsonl")
    capsule = result.capsule
    assert capsule["mission"]["objective"] == "Ship it."
    assert any(d["content"] == "Use sqlite." for d in capsule["decisions"])
    unverified = [r for r in schema.iter_records(capsule)
                  if r["status"] == "UNVERIFIED"]
    assert unverified, "unknown JSONL object must survive as UNVERIFIED"
    assert capsule["next_action"] == "Run the demo."
