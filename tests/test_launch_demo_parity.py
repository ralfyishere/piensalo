"""Anti-drift: the committed launch-demo transcript must match the script.

The launch demo is offline and deterministic, so LAUNCH-TRANSCRIPT.md must
equal a fresh run of launch-demo.sh byte-for-byte. If optimizer output,
committed evidence, or the script changes, this test fails until the
transcript is regenerated — so a recorded demo can never silently drift
from shipping behavior.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT / "examples" / "context-optimizer"
SCRIPT = DEMO_DIR / "launch-demo.sh"
TRANSCRIPT = DEMO_DIR / "LAUNCH-TRANSCRIPT.md"


def _fenced_console_block(md: str) -> str:
    """Extract the single ```console fenced block, minus the leading
    `$ ...` invocation line."""
    m = re.search(r"```console\n(.*?)```", md, re.S)
    assert m, "LAUNCH-TRANSCRIPT.md lost its ```console fence"
    body = m.group(1)
    lines = body.split("\n")
    assert lines[0].startswith("$ "), "transcript fence must start with `$ `"
    return "\n".join(lines[1:])


def test_launch_transcript_matches_fresh_run():
    assert SCRIPT.is_file(), "launch-demo.sh missing"
    proc = subprocess.run(["sh", str(SCRIPT)], capture_output=True, text=True)
    assert proc.returncode == 0, f"launch-demo.sh failed:\n{proc.stderr}"
    fresh = proc.stdout
    committed = _fenced_console_block(TRANSCRIPT.read_text(encoding="utf-8"))
    # The fence body carries a trailing newline before ```; normalize both.
    assert fresh.rstrip("\n") == committed.rstrip("\n"), (
        "LAUNCH-TRANSCRIPT.md drifted from launch-demo.sh output — "
        "regenerate it (see the header of LAUNCH-TRANSCRIPT.md)")


def test_launch_demo_makes_no_model_call_and_leaks_no_paths():
    text = SCRIPT.read_text(encoding="utf-8")
    # The default demo must not invoke a live adapter run.
    assert "context run " not in text
    assert "--adapter" not in text.split("Run the model comparison")[0]
    transcript = TRANSCRIPT.read_text(encoding="utf-8")
    for needle in ("/Users/", "wecheckai"):
        assert needle not in transcript, f"{needle!r} leaked into transcript"


def test_recorded_step_is_labeled_recorded_not_live():
    transcript = TRANSCRIPT.read_text(encoding="utf-8")
    assert "RECORDED committed model run" in transcript
    assert "NOT generated live" in transcript
    assert "integrity: recorded run matches current context.txt" in transcript
