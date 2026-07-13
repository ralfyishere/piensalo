"""repair: honest offline packet by default; adapter mode writes + re-inspects."""
from __future__ import annotations

import json

from piensalo.cli.main import main

TASK = (
    "Compute the compounded total: 5% per month over 12 months on a base of "
    "1000. You must output exactly the line TOTAL: <value>."
)
BROKEN = "TOTAL: 1600.00\n"  # asserted figure, no visible derivation
REPAIRED = "TOTAL: 1795.86\nDerivation: 1000 * 1.05 ** 12 = 1795.856...\n"
CLEAN = REPAIRED  # a draft that needs no repair


def _fixtures(root, draft_text=BROKEN):
    task = root / "task.md"
    draft = root / "draft.md"
    task.write_text(TASK, encoding="utf-8")
    draft.write_text(draft_text, encoding="utf-8")
    return task, draft


def test_default_mode_emits_labeled_packet_and_applies_nothing(project_root, capsys):
    task, draft = _fixtures(project_root)
    assert main(["repair", "--task", str(task), "--draft", str(draft)]) == 0
    out = capsys.readouterr().out
    assert out.startswith("REPAIR PACKET — instructions for a model; nothing has been applied.")
    assert "READY-TO-PASTE PROMPT" in out
    assert TASK.split(".")[0] in out  # task text is in the packet
    assert "TOTAL: 1600.00" in out  # draft is in the packet
    assert "rederive-the-numbers" in out  # repair skill body is in the packet
    assert draft.read_text(encoding="utf-8") == BROKEN  # source untouched
    assert not (project_root / "draft.repaired.md").exists()  # nothing written


def test_no_repair_needed_exits_zero_and_never_calls_adapter(project_root, capsys):
    task, draft = _fixtures(project_root, CLEAN)
    # The response file does not exist; if the adapter ran, this would fail.
    rc = main(
        ["repair", "--task", str(task), "--draft", str(draft),
         "--adapter", "manual", "--response-file", str(project_root / "absent.md")]
    )
    assert rc == 0
    assert "NO REPAIR NEEDED" in capsys.readouterr().out
    assert not (project_root / "draft.repaired.md").exists()


def test_adapter_mode_writes_output_sidecar_and_reinspects(project_root, capsys):
    task, draft = _fixtures(project_root)
    response = project_root / "model-response.md"
    response.write_text(REPAIRED, encoding="utf-8")
    rc = main(
        ["repair", "--task", str(task), "--draft", str(draft),
         "--adapter", "manual", "--response-file", str(response)]
    )
    assert rc == 0
    out = capsys.readouterr().out
    repaired = project_root / "draft.repaired.md"  # default: next to the draft
    assert repaired.read_text(encoding="utf-8") == REPAIRED
    assert draft.read_text(encoding="utf-8") == BROKEN  # source NEVER overwritten
    prov = json.loads((project_root / "draft.repaired.md.provenance.json").read_text())
    assert prov["adapter"] == "manual"
    for key in ("requested_model", "resolved_model", "started_at", "finished_at",
                "input_sha256", "output_sha256"):
        assert key in prov, key
    assert set(prov["input_sha256"]) == {"task", "draft", "prompt"}
    # Re-inspection happened and is stated honestly — never "repair succeeded".
    assert "re-inspection of repaired draft" in out
    assert "not proof of correctness" in out
    assert "repair succeeded" not in out.lower()


def test_adapter_mode_reports_remaining_defects(project_root, capsys):
    task, draft = _fixtures(project_root)
    response = project_root / "model-response.md"
    response.write_text("TOTAL: 1700.00\n", encoding="utf-8")  # still no derivation
    rc = main(
        ["repair", "--task", str(task), "--draft", str(draft),
         "--adapter", "manual", "--response-file", str(response)]
    )
    assert rc == 0  # wrote + reinspected; remaining defects are reported, not hidden
    out = capsys.readouterr().out
    assert "remaining observable defect(s): number-without-derivation" in out


def test_refuses_existing_output_without_force(project_root, capsys):
    task, draft = _fixtures(project_root)
    response = project_root / "model-response.md"
    response.write_text(REPAIRED, encoding="utf-8")
    existing = project_root / "draft.repaired.md"
    existing.write_text("precious", encoding="utf-8")
    rc = main(
        ["repair", "--task", str(task), "--draft", str(draft),
         "--adapter", "manual", "--response-file", str(response)]
    )
    assert rc == 1
    assert "--force" in capsys.readouterr().err
    assert existing.read_text(encoding="utf-8") == "precious"
    # With --force it proceeds.
    rc = main(
        ["repair", "--task", str(task), "--draft", str(draft),
         "--adapter", "manual", "--response-file", str(response), "--force"]
    )
    assert rc == 0
    assert existing.read_text(encoding="utf-8") == REPAIRED


def test_refuses_output_onto_source(project_root, capsys):
    task, draft = _fixtures(project_root)
    rc = main(
        ["repair", "--task", str(task), "--draft", str(draft),
         "--adapter", "manual", "--output", str(draft), "--force"]
    )
    assert rc == 1
    assert "refusing to overwrite source" in capsys.readouterr().err
    assert draft.read_text(encoding="utf-8") == BROKEN


def test_adapter_failure_is_nonzero(project_root, capsys):
    task, draft = _fixtures(project_root)
    rc = main(
        ["repair", "--task", str(task), "--draft", str(draft),
         "--adapter", "manual", "--response-file", str(project_root / "missing.md")]
    )
    assert rc == 1
    assert not (project_root / "draft.repaired.md").exists()


def test_non_manual_adapter_requires_model(project_root, capsys):
    task, draft = _fixtures(project_root)
    for adapter in ("claude-cli", "openai", "ollama"):
        rc = main(["repair", "--task", str(task), "--draft", str(draft),
                   "--adapter", adapter])
        assert rc == 1
        assert "--model" in capsys.readouterr().err
