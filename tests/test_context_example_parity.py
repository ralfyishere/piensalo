"""Anti-drift: the committed examples/context/generated/ output must be
exactly what the shipping code produces from the committed transcript, and
the capsule must match the hand-authored expected-active-state.json.

If compile behavior changes, regenerate with examples/context/demo.sh and
re-review the diff — this test makes silent divergence impossible.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from piensalo.context import verify
from piensalo.context.compiler import compile_to_dir

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "context"

# Mirrors examples/context/demo.sh exactly.
DEMO_GOAL = "Continue the acme-widgets beta-hardening work in a fresh session"
DEMO_BUDGET = 1200


@pytest.fixture(scope="module")
def regenerated(tmp_path_factory):
    out = tmp_path_factory.mktemp("regen")
    import os
    cwd = os.getcwd()
    os.chdir(EXAMPLE)  # demo.sh compiles from its own directory
    try:
        result = compile_to_dir(
            "transcript.txt", str(out), goal=DEMO_GOAL,
            token_budget=DEMO_BUDGET,
            project_state_path="project-state.json")
    finally:
        os.chdir(cwd)
    return out, result


def test_generated_files_match_shipping_code_byte_for_byte(regenerated):
    out, _ = regenerated
    for name in ("capsule.json", "resume.md", "verification.json"):
        committed = (EXAMPLE / "generated" / name).read_text(encoding="utf-8")
        fresh = (out / name).read_text(encoding="utf-8")
        assert committed == fresh, (
            f"examples/context/generated/{name} drifted from program output; "
            "regenerate with examples/context/demo.sh and review the diff")


def test_capsule_matches_expected_active_state(regenerated):
    _, result = regenerated
    capsule = result.capsule
    expected = json.loads(
        (EXAMPLE / "expected-active-state.json").read_text(encoding="utf-8"))

    assert capsule["mission"]["objective"] == expected["objective"]
    by_status: dict[str, list[str]] = {}
    for d in capsule["decisions"]:
        by_status.setdefault(d["status"], []).append(d["content"])
    assert by_status.get("ACTIVE", []) == expected["active_decisions"]
    assert by_status.get("SUPERSEDED", []) == expected["superseded_decisions"]
    assert by_status.get("CONTESTED", []) == expected["contested_decisions"]
    assert by_status.get("UNVERIFIED", []) == expected["unverified_decisions"]
    assert [f["content"] for f in capsule["failed_approaches"]] == \
        expected["failed_approaches"]
    assert capsule["next_action"] == expected["next_action"]

    unstructured = [o for o in capsule["known_omissions"]
                    if o["kind"] == "unstructured"]
    assert len(unstructured) == expected["unstructured_omission_count"]


def test_exact_strings_survive_and_superseded_stays_historical(regenerated):
    _, result = regenerated
    expected = json.loads(
        (EXAMPLE / "expected-active-state.json").read_text(encoding="utf-8"))
    for exact in expected["must_survive_exact"]:
        assert exact in result.resume_md, f"EXACT lost from resume: {exact!r}"
    for gone in expected["must_not_render_as_current"]:
        assert gone not in result.resume_md, (
            f"superseded content rendered as current: {gone!r}")
        assert any(d["content"] == gone and d["status"] == "SUPERSEDED"
                   for d in result.capsule["decisions"]), (
            "superseded content must remain in the capsule as history")


def test_example_is_smaller_than_source_and_verifies(regenerated):
    _, result = regenerated
    m = result.capsule["metrics"]
    assert m["resume_tokens_est"] < m["original_tokens_est"], (
        "the demo resume must be smaller than its source transcript")
    report = verify.verify_dir(str(EXAMPLE / "generated"))
    assert report["verdict"] == "SAFE WITH QUALIFICATIONS"
    assert report["checks"]["source_hash_integrity"]["status"] == "PASS"
    assert report["behavioral_equivalence"] == "UNMEASURED"
