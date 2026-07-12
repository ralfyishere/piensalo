"""piensalo.repair — the repair library and its loader.

The library is ten micro-skills stored as markdown data files under
``library/``. Each is a single targeted intervention with an observable
trigger, a bounded procedure, a required output, and an honest evidence
status. The scanner (``piensalo.inspect.scanner``) maps demonstrated
defects to these repairs; this module only loads and lists them.
"""
from __future__ import annotations

from pathlib import Path

LIBRARY_DIR = Path(__file__).resolve().parent / "library"


def list_repairs() -> list[str]:
    """Return the names of all repairs in the library, sorted."""
    return sorted(p.stem for p in LIBRARY_DIR.glob("*.md"))


def load_repair(name: str) -> str:
    """Return the full markdown text of one repair by name."""
    path = LIBRARY_DIR / f"{name}.md"
    if not path.is_file():
        raise KeyError(
            f"unknown repair: {name!r} (available: {', '.join(list_repairs())})"
        )
    return path.read_text(encoding="utf-8")
