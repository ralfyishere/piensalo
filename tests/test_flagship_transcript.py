"""Anti-drift parity test: demo.sh output must equal the committed TRANSCRIPT.md,
and the flagship drafts must keep producing the expected findings."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from piensalo.cli.main import main

REPO = Path(__file__).resolve().parent.parent
FLAGSHIP = REPO / "examples" / "flagship"

_TS = re.compile(r"\d{4}-\d{2}-\d{2}T[0-9:.+\-]+")


def _normalize(text: str) -> str:
    lines = []
    for ln in text.splitlines():
        ln = ln.rstrip()
        ln = ln.replace(str(REPO), "<REPO>")
        ln = _TS.sub("<TIMESTAMP>", ln)
        lines.append(ln)
    return "\n".join(lines).strip()


def _run_demo() -> str:
    env = dict(os.environ)
    env["PYTHON"] = sys.executable
    proc = subprocess.run(
        ["bash", str(FLAGSHIP / "demo.sh")],
        capture_output=True,
        text=True,
        cwd=REPO,
        env=env,
    )
    assert proc.returncode == 0, proc.stderr
    return proc.stdout + proc.stderr


def test_demo_matches_committed_transcript():
    fresh = _run_demo()
    transcript = (FLAGSHIP / "TRANSCRIPT.md").read_text(encoding="utf-8")
    committed = transcript.split("```text\n", 1)[1].rsplit("\n```", 1)[0]
    assert _normalize(fresh) == _normalize(committed), (
        "demo.sh output drifted from examples/flagship/TRANSCRIPT.md — "
        "regenerate the transcript deliberately or fix the regression"
    )


def test_expected_findings_hold(capsys):
    expected = json.loads((FLAGSHIP / "expected-findings.json").read_text(encoding="utf-8"))
    task = str(FLAGSHIP / "task.md")
    contract = str(FLAGSHIP / "contract.json")

    # Broken draft: the declared defect class must be detected and repaired-for.
    exp_b = expected["draft-broken.md"]
    broken = str(FLAGSHIP / "draft-broken.md")
    rc = main(["inspect", "--task", task, "--draft", broken, "--contract", contract])
    out = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(out[: out.rindex("}") + 1])
    assert payload["no_repair_needed"] is exp_b["no_repair_needed"]
    assert exp_b["defect"] in payload["defects_detected"]
    assert payload["selected_repairs"] == [exp_b["selected_repair"]]

    rc = main(["verify", "--task", task, "--draft", broken, "--contract", contract])
    out = capsys.readouterr().out
    assert rc == 1
    assert exp_b["verify_failed_contains"] in out

    # Correct draft: correct abstention plus a clean deterministic verify.
    exp_c = expected["draft-correct.md"]
    correct = str(FLAGSHIP / "draft-correct.md")
    rc = main(["inspect", "--task", task, "--draft", correct, "--contract", contract])
    out = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(out[: out.rindex("}") + 1])
    assert payload["no_repair_needed"] is exp_c["no_repair_needed"]
    assert "NO REPAIR NEEDED" in out

    rc = main(["verify", "--task", task, "--draft", correct, "--contract", contract])
    out = capsys.readouterr().out
    assert rc == 0
    assert exp_c["verify_deterministic_contains"] in out
