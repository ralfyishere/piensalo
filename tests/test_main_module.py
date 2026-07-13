"""``python -m piensalo`` must work — CI invokes the CLI exactly that way."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _env_with_src() -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO / "src") + os.pathsep + env.get("PYTHONPATH", "")
    return env


def test_python_dash_m_help_exits_zero():
    proc = subprocess.run(
        [sys.executable, "-m", "piensalo", "--help"],
        capture_output=True,
        text=True,
        cwd=REPO,
        env=_env_with_src(),
    )
    assert proc.returncode == 0, proc.stderr
    assert "piensalo" in proc.stdout


def test_python_dash_m_version():
    proc = subprocess.run(
        [sys.executable, "-m", "piensalo", "version"],
        capture_output=True,
        text=True,
        cwd=REPO,
        env=_env_with_src(),
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.startswith("piensalo ")
