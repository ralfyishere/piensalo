"""think input resolution: file vs literal text, path-like errors, overrides."""
from __future__ import annotations

from piensalo.cli.main import main

TASK_TEXT = "Compute the compounded total: 5% per month over 12 months on a base of 1000."


def test_existing_file(project_root, capsys):
    task = project_root / "task.md"
    task.write_text(TASK_TEXT, encoding="utf-8")
    assert main(["think", str(task), "--offline"]) == 0
    assert "compounded total" in capsys.readouterr().out


def test_file_with_spaces_in_name(project_root, capsys):
    task = project_root / "my task file.md"
    task.write_text(TASK_TEXT, encoding="utf-8")
    assert main(["think", str(task), "--offline"]) == 0
    assert "compounded total" in capsys.readouterr().out


def test_inline_text(project_root, capsys):
    assert main(["think", "Summarize the quarterly revenue trend", "--offline"]) == 0
    assert "quarterly revenue trend" in capsys.readouterr().out


def test_missing_pathlike_is_hard_error(project_root, capsys):
    rc = main(["think", "no-such-task.md", "--offline"])
    assert rc != 0
    err = capsys.readouterr().err
    assert "file not found" in err
    assert "--text" in err  # points at the escape hatch


def test_missing_path_with_separator_is_hard_error(project_root, capsys):
    rc = main(["think", "sub/dir/task", "--offline"])
    assert rc != 0
    assert "file not found" in capsys.readouterr().err


def test_text_override_forces_literal(project_root, capsys):
    # Looks like a path, but --text always wins and treats it literally.
    assert main(["think", "--text", "notes.md", "--offline"]) == 0
    assert "notes.md" in capsys.readouterr().out


def test_file_override_forces_file(project_root, capsys):
    task = project_root / "task.md"
    task.write_text(TASK_TEXT, encoding="utf-8")
    assert main(["think", "--file", str(task), "--offline"]) == 0
    assert "compounded total" in capsys.readouterr().out


def test_file_override_missing_is_error(project_root, capsys):
    assert main(["think", "--file", str(project_root / "gone.md"), "--offline"]) == 1


def test_file_and_text_are_mutually_exclusive(project_root, capsys):
    rc = main(["think", "--file", "x.md", "--text", "y", "--offline"])
    assert rc != 0
    assert "mutually exclusive" in capsys.readouterr().err
