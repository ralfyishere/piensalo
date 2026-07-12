"""Loop lifecycle tests: start, gate, step, close, checkpoints, handoff.

The public loop is git-free: checkpoints are JSON snapshots under
.fable-think/checkpoints/ and handoff staleness is detected via a state
fingerprint, so these tests need no repository.
"""
from __future__ import annotations

import json

import pytest

from fable_think.loop import controller
from fable_think.loop.state import LoopPaths, jload, jsave

GOOD_ACTION = {
    "id": "act-1",
    "title": "one bounded improvement",
    "status": "pending",
    "verifier": "run the check script",
    "success_criteria": "check exits 0",
    "stop_condition": "one cycle",
    "evidence_producing": True,
}

BAD_ACTION = {
    "id": "act-bad",
    "title": "vibes",
    "status": "pending",
    # no verifier / stop_condition / success_criteria
}


@pytest.fixture
def paths(project_root):
    p = LoopPaths(project_root).ensure()
    jsave(p.session_provenance, {"session_id": "s1", "resolved_model": "test-model"})
    return p


def _start(project_root, paths, queue):
    goal = project_root / "GOAL.md"
    goal.write_text("# goal: improve one thing per cycle", encoding="utf-8")
    jsave(paths.queue, {"queue": queue})
    assert controller.main(["start", str(goal)]) == 0


def test_start_writes_state_prompt_checkpoint(project_root, paths, capsys):
    _start(project_root, paths, [GOOD_ACTION])
    st = jload(paths.state)
    assert st["driving_model"] == "test-model"
    assert st["cycle_count"] == 0
    assert paths.next_prompt.exists()
    assert list(paths.checkpoints.glob("ckpt-*start*.json"))
    assert "loop started" in capsys.readouterr().out


def test_full_cycle_lifecycle(project_root, paths, capsys):
    _start(project_root, paths, [GOOD_ACTION])
    # Open a cycle: prints the execution packet.
    assert controller.main(["step"]) == 0
    out = capsys.readouterr().out
    assert "EXECUTION PACKET cycle-001" in out
    assert jload(paths.state)["open_cycle"]["action"] == "act-1"

    # Close it with a verified outcome.
    outcome = project_root / "OUTCOME.json"
    outcome.write_text(
        json.dumps(
            {
                "result_summary": "improved and verified",
                "evidence_files": ["evidence.txt"],
                "verifier_ran": True,
                "tokens_spent": 1000,
                "candidates": [
                    {"candidate_id": "cand-1", "disposition": "archived"}
                ],
            }
        ),
        encoding="utf-8",
    )
    assert controller.main(["step", "close", str(outcome)]) == 0
    st = jload(paths.state)
    assert st["cycle_count"] == 1
    assert st["open_cycle"] is None
    assert st["queue"][0]["status"] == "done"
    # Candidate archived, trace appended, checkpoint written.
    assert (paths.archive / "cand-1.json").exists()
    assert "cycle-001" in paths.traces.read_text(encoding="utf-8")
    assert list(paths.checkpoints.glob("ckpt-*close-cycle-001*.json"))

    # Handoff prompt is consistent with the saved state.
    assert controller.main(["verify-handoff"]) == 0


def test_prompt_gate_refuses_unverifiable_action(project_root, paths, capsys):
    _start(project_root, paths, [BAD_ACTION])
    with pytest.raises(SystemExit) as exc:
        controller.main(["step"])
    assert exc.value.code == 4
    out = capsys.readouterr().out
    assert "PROMPT GATE FAILED" in out
    assert "no verifier" in out


def test_model_switch_is_a_hard_stop(project_root, paths, capsys):
    _start(project_root, paths, [GOOD_ACTION])
    # A safeguard silently switches the session's resolved model.
    jsave(paths.session_provenance, {"session_id": "s1", "resolved_model": "other-model"})
    with pytest.raises(SystemExit) as exc:
        controller.main(["step"])
    assert exc.value.code == 2
    assert "MODEL_SWITCH_STOP" in capsys.readouterr().out


def test_verify_handoff_detects_stale_prompt(project_root, paths, capsys):
    _start(project_root, paths, [GOOD_ACTION])
    # Mutate state after the prompt was generated -> fingerprint drifts.
    st = jload(paths.state)
    st["cycle_count"] = 99
    jsave(paths.state, st)
    assert controller.main(["verify-handoff"]) == 1
    assert "STALE HANDOFF" in capsys.readouterr().err


def test_outcome_without_verifier_is_rejected(project_root, paths, capsys):
    _start(project_root, paths, [GOOD_ACTION])
    assert controller.main(["step"]) == 0
    capsys.readouterr()
    outcome = project_root / "OUTCOME.json"
    outcome.write_text(
        json.dumps(
            {
                "result_summary": "did stuff",
                "evidence_files": [],
                "verifier_ran": False,
                "tokens_spent": 10,
            }
        ),
        encoding="utf-8",
    )
    assert controller.main(["step", "close", str(outcome)]) == 1
    assert "verifier did not run" in capsys.readouterr().err


def test_status_and_stop(project_root, paths, capsys):
    _start(project_root, paths, [GOOD_ACTION])
    assert controller.main(["status"]) == 0
    assert "driving model: test-model" in capsys.readouterr().out
    assert controller.main(["stop", "done for today"]) == 0
    assert "loop stopped" in capsys.readouterr().out
    # A stopped loop refuses to open new cycles.
    assert controller.main(["step"]) == 1
    assert "stopped" in capsys.readouterr().err
