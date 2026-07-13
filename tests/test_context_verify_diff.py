"""Context MVP: deterministic verification (stale/missing/tamper) + diff."""
from __future__ import annotations

import json
from pathlib import Path

from piensalo.context import diff as diff_mod
from piensalo.context import schema, verify
from piensalo.context.compiler import compile_to_dir

TRANSCRIPT = """\
OBJECTIVE: Ship the widget.
DECISION: Use the PIENSALO organization for hosting.
DECISION: Use ralfyishere because personal creator attribution is the strategy.
SUPERSEDES: Use the PIENSALO organization for hosting.
CONSTRAINT: Never force-push to main.
ARTIFACT: src/widget/core.py
STOP CONDITION: Stop if the suite fails twice in a row.
NEXT ACTION: Run `uv run pytest -q`.
"""


def _bundle(tmp_path: Path, text: str = TRANSCRIPT, budget: int = 5000,
            name: str = "out"):
    src = tmp_path / "transcript.txt"
    src.write_text(text, encoding="utf-8")
    out = tmp_path / name
    result = compile_to_dir(str(src), str(out), goal="continue",
                            token_budget=budget)
    return src, out, result


def test_fresh_bundle_verifies_with_source(tmp_path):
    _, out, _ = _bundle(tmp_path)
    report = verify.verify_dir(str(out))
    checks = report["checks"]
    assert checks["source_hash_integrity"]["status"] == "PASS"
    assert checks["record_reference_integrity"]["status"] == "PASS"
    assert checks["exact_content_preserved_in_resume"]["status"] == "PASS"
    assert checks["superseded_not_rendered_as_active"]["status"] == "PASS"
    assert report["verdict"] in ("DETERMINISTICALLY VERIFIED",
                                 "SAFE WITH QUALIFICATIONS")
    assert report["behavioral_equivalence"] == "UNMEASURED"
    assert checks["behavioral_equivalence"]["status"] == "UNMEASURED"


def test_stale_source_is_detected_and_unsafe(tmp_path):
    src, out, _ = _bundle(tmp_path)
    src.write_text(TRANSCRIPT.replace("widget", "gadget"), encoding="utf-8")
    report = verify.verify_dir(str(out))
    assert report["checks"]["source_hash_integrity"]["status"] == "STALE"
    assert report["verdict"] == "UNSAFE TO RESUME"


def test_missing_source_is_explicit_and_qualified(tmp_path):
    src, out, _ = _bundle(tmp_path)
    src.unlink()
    report = verify.verify_dir(str(out))
    assert report["checks"]["source_hash_integrity"]["status"] == "MISSING"
    assert report["checks"]["record_reference_integrity"]["status"] == "MISSING"
    assert report["verdict"] == "SAFE WITH QUALIFICATIONS"


def test_tampered_capsule_fails_id_stability(tmp_path):
    _, out, _ = _bundle(tmp_path)
    cap_path = out / "capsule.json"
    capsule = json.loads(cap_path.read_text(encoding="utf-8"))
    capsule["next_action"] = "Do something else entirely."
    cap_path.write_text(schema.canonical_json(capsule), encoding="utf-8")
    report = verify.verify_dir(str(out))
    assert report["checks"]["capsule_id_stable"]["status"] == "FAIL"
    assert report["verdict"] == "UNSAFE TO RESUME"


def test_noncanonical_serialization_fails(tmp_path):
    _, out, _ = _bundle(tmp_path)
    cap_path = out / "capsule.json"
    capsule = json.loads(cap_path.read_text(encoding="utf-8"))
    cap_path.write_text(json.dumps(capsule), encoding="utf-8")  # compact form
    report = verify.verify_dir(str(out))
    assert report["checks"]["serialization_stable"]["status"] == "FAIL"
    assert report["verdict"] == "UNSAFE TO RESUME"


def test_exact_content_dropped_from_resume_fails(tmp_path):
    _, out, _ = _bundle(tmp_path)
    resume = out / "resume.md"
    resume.write_text(
        resume.read_text(encoding="utf-8").replace("src/widget/core.py",
                                                   "src/widget/[path]"),
        encoding="utf-8")
    report = verify.verify_dir(str(out))
    assert report["checks"]["exact_content_preserved_in_resume"]["status"] == "FAIL"
    assert report["verdict"] == "UNSAFE TO RESUME"


def test_unmeasured_never_becomes_a_pass(tmp_path):
    """Even a perfect structural run keeps behavioral equivalence UNMEASURED
    and never emits SAFE TO RESUME."""
    _, out, _ = _bundle(tmp_path)
    report = verify.verify_dir(str(out))
    assert report["behavioral_equivalence"] == "UNMEASURED"
    assert "SAFE TO RESUME" not in report["verdict"]
    assert report["checks"]["behavioral_equivalence"]["status"] == "UNMEASURED"


def test_refused_bundle_verdict_requires_expansion(tmp_path):
    _, out, _ = _bundle(tmp_path, budget=40, name="tiny")
    report = verify.verify_dir(str(out))
    assert report["verdict"] == "REQUIRES EXPANSION"
    assert report["checks"]["token_budget_compliance"]["status"] == "FAIL"


# ------------------------------------------------------------------ diff
CHANGED = TRANSCRIPT.replace(
    "NEXT ACTION: Run `uv run pytest -q`.",
    "OPEN ACTION: Document the diff command.\n"
    "NEXT ACTION: Ship the docs.",
).replace("CONSTRAINT: Never force-push to main.",
          "CONSTRAINT: Never force-push to main.\n"
          "DECISION: Adopt trunk-based development.")


def test_diff_reports_added_and_changed(tmp_path):
    _, out_a, _ = _bundle(tmp_path, name="a")
    _, out_b, _ = _bundle(tmp_path, text=CHANGED, name="b")
    d = diff_mod.diff_paths(str(out_a), str(out_b))
    added = [e["content"] for e in d["sections"]["decisions"]["added"]]
    assert "Adopt trunk-based development." in added
    assert d["next_action"] == {"a": "Run `uv run pytest -q`.",
                                "b": "Ship the docs."}
    assert "removed" not in d["sections"].get("stop_conditions", {})
    assert isinstance(d["token_delta"]["resume_tokens_est"], int)


def test_diff_detects_supersession_between_versions(tmp_path):
    v1 = ("OBJECTIVE: O.\nDECISION: Use X.\nNEXT ACTION: n.\n")
    v2 = ("OBJECTIVE: O.\nDECISION: Use X.\nDECISION: Use Y.\n"
          "SUPERSEDES: Use X.\nNEXT ACTION: n.\n")
    _, out_a, _ = _bundle(tmp_path, text=v1, name="v1")
    _, out_b, _ = _bundle(tmp_path, text=v2, name="v2")
    d = diff_mod.diff_paths(str(out_a), str(out_b))
    sup = d["sections"]["decisions"]["superseded"]
    assert [e["content"] for e in sup] == ["Use X."]
    added = [e["content"] for e in d["sections"]["decisions"]["added"]]
    assert "Use Y." in added


def test_diff_identical_capsules_is_empty(tmp_path):
    _, out_a, _ = _bundle(tmp_path, name="s1")
    _, out_b, _ = _bundle(tmp_path, name="s2")
    d = diff_mod.diff_paths(str(out_a), str(out_b))
    assert d["sections"] == {}
    assert d["token_delta"] == {"original_tokens_est": 0,
                                "resume_tokens_est": 0}
    assert "no structural changes" in diff_mod.render_diff(d)


def test_diff_json_rendering_is_canonical(tmp_path):
    _, out_a, _ = _bundle(tmp_path, name="j1")
    _, out_b, _ = _bundle(tmp_path, text=CHANGED, name="j2")
    d = diff_mod.diff_paths(str(out_a), str(out_b))
    assert schema.canonical_json(d) == schema.canonical_json(
        json.loads(schema.canonical_json(d)))
