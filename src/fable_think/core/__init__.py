"""fable_think.core — the cognitive core: 11 named operations.

Loads and exposes the operation definitions from ``operations.json``. The
operations are data, not code: the compiler assembles them into programs,
and the CLI renders them. This module only provides typed access.
"""
from __future__ import annotations

import json
from pathlib import Path

_OPS_PATH = Path(__file__).resolve().parent / "operations.json"


def load_operations() -> list[dict]:
    """Return the 11 operation definitions in program order."""
    with open(_OPS_PATH, encoding="utf-8") as f:
        return json.load(f)["operations"]


def get_operation(name: str) -> dict:
    """Return one operation by name; raise KeyError if unknown."""
    for op in load_operations():
        if op["name"] == name:
            return op
    raise KeyError(f"unknown operation: {name}")


def operation_names() -> list[str]:
    """Return the operation names in canonical program order."""
    return [op["name"] for op in load_operations()]
