"""CLI smoke tests: every subcommand runs offline and exits cleanly."""
from __future__ import annotations

import json

from piensalo.cli.main import main

TASK = (
    "Compute the compounded total: 5% per month over 12 months on a base of "
    "1000. You must output exactly the line TOTAL: <value> and nothing after it."
)
DRAFT = "TOTAL: 1795.86\nDerivation: 1000 * 1.05 ** 12 = 1795.856..."


def _write_fixtures(root):
    task = root / "task.md"
    draft = root / "draft.md"
    contract = root / "contract.json"
    task.write_text(TASK, encoding="utf-8")
    draft.write_text(DRAFT, encoding="utf-8")
    contract.write_text(
        json.dumps(
            {
                "required_output_fields": [{"name": "TOTAL", "format": "number"}],
                "no_extra_lines": True,
            }
        ),
        encoding="utf-8",
    )
    return task, draft, contract


def test_think_offline(project_root, capsys):
    task, _, _ = _write_fixtures(project_root)
    assert main(["think", str(task), "--offline"]) == 0
    out = capsys.readouterr().out
    assert "Cognitive program" in out or "cognitive program" in out.lower()
    assert "## Task" in out


def test_think_modes(project_root, capsys):
    task, _, _ = _write_fixtures(project_root)
    for mode in ("prose", "prompt"):
        assert main(["think", str(task), "--offline", "--mode", mode]) == 0
        assert capsys.readouterr().out.strip()


def test_inspect(project_root, capsys):
    task, draft, contract = _write_fixtures(project_root)
    rc = main(
        ["inspect", "--task", str(task), "--draft", str(draft), "--contract", str(contract)]
    )
    assert rc == 0
    out = capsys.readouterr().out
    payload = json.loads(out[: out.rindex("}") + 1])
    assert "candidate_scores" in payload


def test_repair(project_root, capsys):
    task, draft, _ = _write_fixtures(project_root)
    assert main(["repair", "--task", str(task), "--draft", str(draft)]) == 0
    out = capsys.readouterr().out
    assert "NO REPAIR NEEDED" in out or "Selected repair" in out


def test_verify(project_root, capsys):
    task, draft, contract = _write_fixtures(project_root)
    rc = main(
        ["verify", "--task", str(task), "--draft", str(draft), "--contract", str(contract)]
    )
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["contract"]["all_present"] is True
    assert "layered_verdict" in payload


def test_loop_help(project_root, capsys):
    assert main(["loop"]) == 0
    assert "start GOAL.md" in capsys.readouterr().out


def test_skill_list_and_inspect(project_root, capsys):
    assert main(["skill", "list"]) == 0
    out = capsys.readouterr().out
    assert "rederive-the-numbers" in out
    assert main(["skill", "inspect", "rederive-the-numbers"]) == 0
    assert "Procedure" in capsys.readouterr().out


def test_skill_lint_builtin_library(project_root, capsys):
    assert main(["skill", "lint"]) == 0
    assert "lint ok" in capsys.readouterr().out


def test_skill_create_and_export(project_root, capsys):
    assert main(["skill", "create", "my-new-skill"]) == 0
    created = project_root / "skills" / "my-new-skill" / "SKILL.md"
    assert created.exists()
    capsys.readouterr()
    target = project_root / "exported"
    assert main(["skill", "export", "my-new-skill", "--target", str(target)]) == 0
    assert (target / "my-new-skill" / "SKILL.md").exists()
    # Built-in repairs are exportable too.
    assert main(["skill", "export", "boundary-case-check", "--target", str(target)]) == 0
    assert (target / "boundary-case-check" / "SKILL.md").exists()


def test_doctor(project_root, capsys):
    import sys

    expected = 0 if sys.version_info >= (3, 10) else 1
    assert main(["doctor"]) == expected
    out = capsys.readouterr().out
    assert "python:" in out
    assert "network: not checked" in out


def test_version(capsys):
    assert main(["version"]) == 0
    assert "piensalo" in capsys.readouterr().out
