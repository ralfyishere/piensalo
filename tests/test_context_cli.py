"""Context MVP: CLI behavior for compile / inspect / verify / diff."""
from __future__ import annotations

import json

from piensalo.cli.main import main

TRANSCRIPT = """\
OBJECTIVE: Ship the widget.
DECISION: Use the PIENSALO organization for hosting.
DECISION: Use ralfyishere because personal creator attribution is the strategy.
SUPERSEDES: Use the PIENSALO organization for hosting.
CONSTRAINT: Never force-push to main.
STOP CONDITION: Stop if the suite fails twice in a row.
NEXT ACTION: Run `uv run pytest -q`.
"""


def _compile(root, budget=5000, name="out"):
    src = root / "transcript.txt"
    src.write_text(TRANSCRIPT, encoding="utf-8")
    out = root / name
    code = main(["context", "compile", str(src), "--goal", "continue",
                 "--budget", str(budget), "--output", str(out)])
    return code, src, out


def test_compile_writes_three_artifacts(project_root, capsys):
    code, _, out = _compile(project_root)
    assert code == 0
    assert (out / "capsule.json").is_file()
    assert (out / "resume.md").is_file()
    assert (out / "verification.json").is_file()
    stdout = capsys.readouterr().out
    assert "behavioral equivalence: UNMEASURED" in stdout


def test_compile_missing_transcript_exits_2(project_root, capsys):
    code = main(["context", "compile", "nope.txt", "--goal", "g",
                 "--budget", "100", "--output", "o"])
    assert code == 2
    assert "not found" in capsys.readouterr().err


def test_compile_insufficient_budget_exits_3(project_root, capsys):
    code, _, out = _compile(project_root, budget=40, name="tiny")
    assert code == 3
    assert "COMPILATION REFUSED" in (out / "resume.md").read_text(encoding="utf-8")
    assert "honest refusal" in capsys.readouterr().err


def test_inspect_shows_required_sections(project_root, capsys):
    _compile(project_root)
    capsys.readouterr()
    assert main(["context", "inspect", str(project_root / "out")]) == 0
    stdout = capsys.readouterr().out
    for needle in (
        "mission objective: Ship the widget.",
        "ACTIVE decisions",
        "SUPERSEDED decisions (historical truth, not current)",
        "Stop conditions",
        "next action: Run `uv run pytest -q`.",
        "exact references:",
        "token estimates",
        "gross compression ratio",
        "behavioral equivalence: UNMEASURED",
    ):
        assert needle in stdout, needle
    # inspect must not claim behavioral equivalence
    assert "behaviorally equivalent" not in stdout


def test_verify_passing_bundle_exits_0(project_root, capsys):
    _compile(project_root)
    capsys.readouterr()
    code = main(["context", "verify", str(project_root / "out"),
                 "--transcript", str(project_root / "transcript.txt")])
    stdout = capsys.readouterr().out
    assert code == 0
    assert "verdict:" in stdout
    assert "UNMEASURED" in stdout


def test_verify_stale_source_exits_1(project_root, capsys):
    _, src, out = _compile(project_root)
    src.write_text(TRANSCRIPT + "EXTRA LINE\n", encoding="utf-8")
    code = main(["context", "verify", str(out), "--transcript", str(src)])
    assert code == 1
    assert '"STALE"' in capsys.readouterr().out


def test_verify_schema_invalid_capsule_is_unsafe(project_root, capsys):
    bad = project_root / "bad"
    bad.mkdir()
    (bad / "capsule.json").write_text("{}", encoding="utf-8")
    code = main(["context", "verify", str(bad)])
    assert code == 1
    out = capsys.readouterr().out
    assert "UNSAFE TO RESUME" in out
    assert "capsule missing key" in out


def test_verify_unreadable_capsule_exits_2(project_root, capsys):
    bad = project_root / "bad"
    bad.mkdir()
    (bad / "capsule.json").write_text("{not json", encoding="utf-8")
    code = main(["context", "verify", str(bad)])
    assert code == 2
    assert "not valid JSON" in capsys.readouterr().err


def test_diff_human_and_json(project_root, capsys):
    _compile(project_root, name="a")
    (project_root / "t2.txt").write_text(
        TRANSCRIPT + "DECISION: Adopt trunk-based development.\n",
        encoding="utf-8")
    main(["context", "compile", str(project_root / "t2.txt"), "--goal",
          "continue", "--budget", "5000", "--output",
          str(project_root / "b")])
    capsys.readouterr()
    assert main(["context", "diff", str(project_root / "a"),
                 str(project_root / "b")]) == 0
    human = capsys.readouterr().out
    assert "added" in human and "trunk-based" in human
    assert main(["context", "diff", str(project_root / "a"),
                 str(project_root / "b"), "--json"]) == 0
    machine = json.loads(capsys.readouterr().out)
    assert machine["sections"]["decisions"]["added"]


def test_compile_accepts_project_state_and_model_metadata(project_root, capsys):
    src = project_root / "transcript.txt"
    src.write_text(TRANSCRIPT, encoding="utf-8")
    ps = project_root / "state.json"
    ps.write_text(json.dumps({"branch": "context-mvp"}), encoding="utf-8")
    code = main(["context", "compile", str(src), "--goal", "g", "--budget",
                 "5000", "--output", str(project_root / "meta"),
                 "--project-state", str(ps),
                 "--source-model", "any-model-at-all"])
    assert code == 0
    capsule = json.loads(
        (project_root / "meta" / "capsule.json").read_text(encoding="utf-8"))
    assert capsule["state"] == {"branch": "context-mvp"}
    assert capsule["compiled_for"]["source_model"] == "any-model-at-all"
