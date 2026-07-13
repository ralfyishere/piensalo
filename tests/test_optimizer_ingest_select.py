"""Optimizer: ingestion/normalization and task-specific selection."""
from __future__ import annotations

import json

import pytest

from piensalo.context import optimize as optimize_mod
from piensalo.context import select
from piensalo.context.ingest import IngestError, load_artifacts, load_context_text

MARKED = """\
OBJECTIVE: Harden the widgets service.
DECISION: Host on the shared cluster.
DECISION: Host on a dedicated cluster after the March incident.
SUPERSEDES: Host on the shared cluster.
CONSTRAINT [EXACT]: Deploy only with `make deploy ENV=staging TAG=beta`.
ARTIFACT: commit 4f2a9c1e7b3d5a20
STOP CONDITION: Stop if error rate exceeds 0.5% for 10 minutes.
FAILED APPROACH: Redis response caching; stale checkout totals.

A long discussion about the logo color and weekend plans. Nothing here
touches engineering at all.

The CI job widgets-tests fails in test_acquire_timeout with a 5 second
timeout since the pool rewrite merged.

NEXT ACTION: Reproduce with `pytest -q tests/store`.
"""

TASK = ("Fix the failing CI job widgets-tests. Use the exact deploy command "
        "and report the commit you base the fix on.")


def _optimize(text=MARKED, task=TASK, budget=2000, **kw):
    items = load_context_text(text)
    return optimize_mod.optimize(task_text=task, items=items, budget=budget,
                                 **kw)


# ------------------------------------------------------------- ingestion
def test_plain_text_single_item():
    items = load_context_text("just ordinary prose\nwith two lines")
    assert len(items) == 1
    assert items[0].role == "text"
    assert items[0].source_hash


def test_generic_jsonl_messages_normalize():
    text = "\n".join([
        json.dumps({"role": "user", "content": "please fix CI",
                    "timestamp": "2026-07-01T00:00:00Z"}),
        json.dumps({"role": "assistant", "content": "on it",
                    "model": "some-model-x"}),
        json.dumps({"tool": "bash", "output": "214 passed",
                    "tool_name": "bash"}),
    ])
    items = load_context_text(text, fmt="jsonl")
    assert [i.role for i in items] == ["user", "assistant", "tool"]
    assert items[0].timestamp == "2026-07-01T00:00:00Z"
    assert items[1].model_provenance == "some-model-x"
    assert items[2].tool_name == "bash"
    assert items[2].content == "214 passed"


def test_generic_chat_json_with_messages_key():
    doc = {"messages": [
        {"role": "system", "content": "be careful"},
        {"role": "user", "content": [{"type": "text", "text": "block style"}]},
    ]}
    items = load_context_text(json.dumps(doc), fmt="json")
    assert [i.role for i in items] == ["system", "user"]
    assert items[1].content == "block style"


def test_unknown_jsonl_object_preserved_verbatim():
    items = load_context_text(json.dumps({"weird": True, "n": 3}),
                              fmt="jsonl")
    assert items[0].role == "text"
    assert json.loads(items[0].content) == {"weird": True, "n": 3}


def test_invalid_json_and_role_are_hard_errors():
    with pytest.raises(IngestError, match="invalid JSON"):
        load_context_text("{oops", fmt="jsonl")
    with pytest.raises(IngestError, match="unknown message role"):
        load_context_text(json.dumps({"role": "wizard", "content": "x"}),
                          fmt="jsonl")


def test_artifact_directory_ingestion_bounded(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("def f():\n    return 1\n",
                                           encoding="utf-8")
    (tmp_path / "src" / "big.bin").write_bytes(b"\x00" * 10)
    (tmp_path / "src" / "__pycache__").mkdir()
    (tmp_path / "src" / "__pycache__" / "a.pyc").write_text("x")
    items = load_artifacts([str(tmp_path / "src")])
    assert len(items) == 1  # .bin and __pycache__ excluded
    assert items[0].role == "artifact"
    assert items[0].artifact_ref.endswith("a.py")


def test_missing_artifact_is_specific_error():
    with pytest.raises(IngestError, match="artifact not found"):
        load_artifacts(["definitely/not/here"])


# ------------------------------------------------------------- selection
def test_mandatory_context_always_preserved():
    result = _optimize()
    manifest = select.manifest(result.selection)
    mandatory = {c["id"]: c for c in manifest["chunks"]
                 if c["disposition"] == "INCLUDED_MANDATORY"}
    types = {c["record_type"] for c in mandatory.values()}
    assert {"constraint", "artifact", "stop_condition", "decision",
            "objective", "next_action"} <= types
    for needle in ("`make deploy ENV=staging TAG=beta`",
                   "commit 4f2a9c1e7b3d5a20"):
        assert needle in result.packet


def test_superseded_removed_from_active_context_not_deleted():
    result = _optimize()
    assert "Host on the shared cluster." not in result.packet
    manifest = select.manifest(result.selection)
    superseded = [c for c in manifest["chunks"]
                  if c["disposition"] == "OMITTED_SUPERSEDED"]
    assert len(superseded) == 1
    assert superseded[0]["superseded_by"]
    # Historical truth survives in the capsule too.
    assert any(d["status"] == "SUPERSEDED"
               for d in result.capsule["decisions"])


def test_distractor_prose_omitted_even_with_room():
    result = _optimize(budget=100_000)
    assert "logo color" not in result.packet
    assert "widgets-tests fails in test_acquire_timeout" in result.packet
    manifest = select.manifest(result.selection)
    low = [c for c in manifest["chunks"]
           if c["disposition"] == "OMITTED_LOW_RELEVANCE"]
    assert low and all("shared terms" in c["reason"] for c in low)


def test_task_specific_selection_differs_by_task():
    ci = _optimize(task="Fix the failing CI job widgets-tests today.")
    copy = _optimize(task="Write launch copy about the logo color and the "
                          "weekend announcement discussion.")
    assert "test_acquire_timeout" in ci.packet
    assert "test_acquire_timeout" not in copy.packet
    assert "logo color" in copy.packet
    assert "logo color" not in ci.packet


def test_deduplication():
    text = MARKED + "\nCONSTRAINT [EXACT]: Deploy only with `make deploy ENV=staging TAG=beta`.\n"
    result = _optimize(text)
    manifest = select.manifest(result.selection)
    dups = [c for c in manifest["chunks"]
            if c["disposition"] == "OMITTED_DUPLICATE"]
    assert len(dups) == 1
    assert result.packet.count("`make deploy ENV=staging TAG=beta`") == 1


def test_every_chunk_has_inspectable_factors_and_reason():
    result = _optimize()
    for c in select.manifest(result.selection)["chunks"]:
        assert c["disposition"] in select.DISPOSITIONS
        assert c["reason"]
        assert set(c["score_factors"]) >= {
            "task_relevance", "criticality", "exactness_weight",
            "artifact_dependency", "recency", "status_weight", "token_cost"}
        assert c["source"]["content_hash"]


def test_budget_refusal_when_mandatory_exceeds_budget():
    result = _optimize(budget=60)
    assert result.refused
    assert result.report["refused"] is True
    assert "never truncated" in result.selection.refusal_reason
    assert result.packet == ""


def test_report_required_fields_and_unmeasured():
    r = _optimize().report
    for key in ("task", "source_context_hash", "original_tokens_est",
                "mandatory_context_tokens", "selected_context_tokens",
                "omitted_context_tokens", "optimized_context_tokens",
                "gross_reduction", "selection_method", "known_omissions",
                "critical_records_retained", "exact_records_retained",
                "risk", "behavioral_status"):
        assert key in r, key
    assert r["behavioral_status"] == "UNMEASURED"


def test_determinism_of_optimize():
    a, b = _optimize(), _optimize()
    assert a.packet == b.packet
    assert select.manifest(a.selection) == select.manifest(b.selection)
    assert a.capsule["capsule_id"] == b.capsule["capsule_id"]


def test_adapter_assisted_mode_requires_explicit_adapter():
    with pytest.raises(ValueError, match="called silently"):
        _optimize(mode="adapter-assisted")


def test_cross_model_metadata_is_optional_and_neutral():
    tagged = _optimize(source_model="model-alpha")
    plain = _optimize()
    assert tagged.capsule["compiled_for"]["source_model"] == "model-alpha"
    assert tagged.packet == plain.packet  # metadata never changes content
