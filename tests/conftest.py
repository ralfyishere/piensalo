"""Shared fixtures: run everything in an isolated temp project root."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Allow `python3 -m pytest` from the repo root without installation.
SRC = Path(__file__).resolve().parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def project_root(tmp_path, monkeypatch):
    """A temp cwd that also pins FABLE_THINK_ROOT for loop state."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("FABLE_THINK_ROOT", str(tmp_path))
    return tmp_path
