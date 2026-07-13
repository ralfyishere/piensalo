"""Output-contract boundary adapter (a surface tool, not a cognitive skill).

Separates the required SURFACE format of an answer from the reasoning that
produced it. Given a task's declared contract (fields plus an exact-format
flag), it (1) emits the exact submission-format block to append to any
prompt, (2) validates field presence in a draft before submission, and
(3) normalizes HARMLESS markdown decoration (bold/italic/backticks around
an otherwise-correct required line) ONLY when the task did not demand a
verbatim exact format. It never changes substantive content.

Internal contract form::

    {"fields": [{"name": str, "pattern": "<line regex, ^ anchored>",
                 "required": bool}],
     "exact_format": bool,
     "final_line": "<field name>" | None}

``load_task_contract`` also accepts the task-contract form used by eval
harnesses (``required_output_fields`` with ``order_required`` /
``no_extra_lines`` / ``forbidden`` flags) and converts it. Skipping that
conversion makes ``check`` iterate an empty field list and report
``all_present: true`` vacuously — which silently disables
missing-deliverable detection downstream, so always load through it.
"""
from __future__ import annotations

import json
import re


def load_task_contract(path: str) -> dict:
    """Load a contract JSON file, converting the task-contract form
    (``required_output_fields`` [{name, format}], ``order_required``,
    ``no_extra_lines``, ``forbidden``) into the internal form. A file
    already in internal form (has ``fields``) passes through unchanged.
    """
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return convert_task_contract(d)


def convert_task_contract(d: dict) -> dict:
    """Convert an in-memory task contract dict to the internal form."""
    if "fields" in d:  # already internal form
        return d
    fields = [
        {
            "name": f["name"],
            "pattern": r"^" + re.escape(f["name"]) + r":",
            "required": True,
            # Optional declared expected value: makes the field's VALUE
            # deterministically checkable downstream (verify). Absent by
            # default — presence-only contracts stay presence-only.
            "expected": f.get("expected"),
        }
        for f in d.get("required_output_fields", [])
    ]
    exact = bool(d.get("order_required") or d.get("no_extra_lines") or d.get("forbidden"))
    final = d["required_output_fields"][-1]["name"] if d.get("required_output_fields") else None
    return {"fields": fields, "exact_format": exact, "final_line": final}


def emit(contract: dict) -> str:
    """Render the submission-format block to append to a prompt."""
    lines = ["## REQUIRED SUBMISSION FORMAT (surface only — reasoning goes above this)"]
    for f in contract.get("fields", []):
        req = "REQUIRED" if f.get("required", True) else "optional"
        lines.append(f"- A line for '{f['name']}' ({req}), matching: {f['pattern']}")
    if contract.get("exact_format"):
        lines.append(
            "- EXACT FORMAT: emit these lines VERBATIM at column 0 — no bold, "
            "no backticks, no bullets, nothing after the final required line."
        )
    else:
        lines.append(
            "- Plain lines; light markdown is tolerated but the literal "
            "field text must be present."
        )
    if contract.get("final_line"):
        lines.append(f"- The LAST line must be the '{contract['final_line']}' field.")
    return "\n".join(lines)


def _strip_deco(line: str) -> str:
    """Remove harmless markdown decoration from one line."""
    s = line.strip()
    s = re.sub(r"^[-*]\s+", "", s)  # bullet
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)  # bold
    s = re.sub(r"\*(.+?)\*", r"\1", s)  # italic
    s = re.sub(r"`(.+?)`", r"\1", s)  # code span
    return s


def check(contract: dict, draft: str) -> dict:
    """Validate required-field presence in a draft.

    Under a non-exact contract, a field found only after decoration
    stripping counts as present and is flagged recoverable-by-normalize.
    Under an exact-format contract, only raw hits count.
    """
    present: list[dict] = []
    missing: list[dict] = []
    lines = draft.splitlines()
    exact = contract.get("exact_format")
    for f in contract.get("fields", []):
        if not f.get("required", True):
            continue
        pat = f["pattern"]
        raw_hit = any(re.search(pat, line) for line in lines)
        deco_hit = raw_hit or (
            not exact and any(re.search(pat, _strip_deco(line)) for line in lines)
        )
        (present if deco_hit else missing).append(
            {
                "field": f["name"],
                "raw_ok": raw_hit,
                "recoverable_by_normalize": (deco_hit and not raw_hit),
            }
        )
    return {
        "all_present": not missing,
        "present": present,
        "missing": missing,
        "exact_format": bool(exact),
    }


def normalize(contract: dict, draft: str) -> str:
    """Rewrite decorated required lines to plain form — non-exact contracts
    only. Under an exact-format contract the draft is returned untouched:
    normalization must never manufacture compliance the author didn't
    produce. Content is never changed either way.
    """
    if contract.get("exact_format"):
        return draft
    pats = [f["pattern"] for f in contract.get("fields", []) if f.get("required", True)]
    out = []
    for line in draft.splitlines():
        stripped = _strip_deco(line)
        if stripped != line.strip() and any(re.search(p, stripped) for p in pats):
            out.append(stripped)  # decorated required line -> plain
        else:
            out.append(line)
    return "\n".join(out)
