"""On-disk state layout and helpers for the bounded loop.

All loop state lives under ``<root>/.fable-think/`` where ``<root>`` is
the ``FABLE_THINK_ROOT`` environment variable if set, else the current
working directory. The public loop has NO git dependency: instead of
clean-tree gates and commit hashes, every open/close/stop writes a JSON
checkpoint snapshot of the full state into ``checkpoints/``, and handoff
prompts record a content fingerprint of the saved state file. A stale
handoff is detected by comparing that fingerprint against the state file
on disk.

Layout::

    .fable-think/
      state.json                 canonical loop state
      queue.json                 action queue (operator-authored)
      next-prompt.md             regenerated handoff prompt
      traces.jsonl               append-only cycle trace index
      provenance.jsonl           append-only model-provenance ledger
      session-provenance.json    resolved model for the current session
      ledger.json                optional task-set consumption ledger
      candidate-archive/         archived candidate JSON files
      checkpoints/               JSON state snapshots (the undo path)
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def now() -> str:
    """UTC timestamp in the ledger format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class LoopPaths:
    """Resolves and creates the loop's on-disk layout."""

    def __init__(self, root: str | os.PathLike | None = None):
        self.root = Path(root or os.environ.get("FABLE_THINK_ROOT") or os.getcwd())
        self.state_dir = self.root / ".fable-think"
        self.state = self.state_dir / "state.json"
        self.queue = self.state_dir / "queue.json"
        self.next_prompt = self.state_dir / "next-prompt.md"
        self.traces = self.state_dir / "traces.jsonl"
        self.provenance = self.state_dir / "provenance.jsonl"
        self.session_provenance = self.state_dir / "session-provenance.json"
        self.ledger = self.state_dir / "ledger.json"
        self.archive = self.state_dir / "candidate-archive"
        self.checkpoints = self.state_dir / "checkpoints"

    def ensure(self) -> "LoopPaths":
        """Create the state directory tree; idempotent."""
        self.archive.mkdir(parents=True, exist_ok=True)
        self.checkpoints.mkdir(parents=True, exist_ok=True)
        self.traces.touch(exist_ok=True)
        return self


def jload(path: Path, default=None):
    """Load JSON from ``path`` or return ``default`` if it doesn't exist."""
    if not path.exists():
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def jsave(path: Path, data) -> None:
    """Write JSON with a stable, reviewable format."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def state_fingerprint(paths: LoopPaths) -> str:
    """Short content hash of the saved state file (the git-free analogue
    of a commit hash for handoff-staleness detection)."""
    if not paths.state.exists():
        return "NO-STATE"
    return hashlib.sha256(paths.state.read_bytes()).hexdigest()[:12]


def write_checkpoint(paths: LoopPaths, state: dict, label: str) -> str:
    """Snapshot the full state as JSON; returns the checkpoint filename.

    Checkpoints are the loop's undo path: restoring one is a plain file
    copy back to ``state.json``.
    """
    paths.checkpoints.mkdir(parents=True, exist_ok=True)
    name = f"ckpt-{now().replace(':', '')}-{label}.json"
    jsave(paths.checkpoints / name, {"ts": now(), "label": label, "state": state})
    return name


def resolved_model(paths: LoopPaths) -> str:
    """The session's resolved model per the provenance file, else UNKNOWN."""
    prov = jload(paths.session_provenance, {})
    return prov.get("resolved_model", "UNKNOWN")


def provenance_line(paths: LoopPaths, kind: str, extra: dict) -> None:
    """Append one line to the append-only model-provenance ledger."""
    line = {"ts": now(), "kind": kind, "resolved_model": resolved_model(paths)}
    line.update(extra)
    paths.provenance.parent.mkdir(parents=True, exist_ok=True)
    with open(paths.provenance, "a", encoding="utf-8") as f:
        f.write(json.dumps(line) + "\n")
