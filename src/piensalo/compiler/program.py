"""Compile a task + selected operations into a cognitive program.

The compiler applies cheap, deterministic objective-recovery heuristics to
the task text (first-sentence intent extraction, deliverable detection,
constraint listing), selects the relevant core operations, and renders the
result in one of three modes:

- ``prose``  — concise prose instructions for a human or model to follow;
- ``packet`` — a structured JSON packet for programmatic consumption;
- ``prompt`` — a full rendered prompt for manual copy/paste.

Everything here is offline: no model call, no network, stdlib only.
"""
from __future__ import annotations

import json
import re

from piensalo.core import load_operations

MODES = ("prose", "packet", "prompt")

_DELIVERABLE_HINTS = re.compile(
    r"\b(write|produce|create|generate|build|output|deliver|return|draft|"
    r"summari[sz]e|list|report|answer|compute|calculate|implement|fix)\b",
    re.I,
)
_CONSTRAINT_CLAUSE = re.compile(
    r"[^.\n]*\b(must not|must|only|never|without|except|at most|at least|"
    r"do not|don't|exactly|verbatim|no more than)\b[^.\n]*",
    re.I,
)
_NUMERIC_TASK = re.compile(r"\d+\s*%|compound|per (month|year|day)|rate", re.I)
_MULTI_PART = re.compile(r"^\s*(?:\d+[.)]|[-*])\s+\S", re.M)


def analyze_task(task_text: str) -> dict:
    """Deterministic heuristics: intent, deliverables, constraints."""
    text = task_text.strip()
    first_sentence = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)[0][:300] if text else ""
    deliverables = sorted(
        {m.group(0).lower() for m in _DELIVERABLE_HINTS.finditer(text)}
    )
    constraints = [m.group(0).strip() for m in _CONSTRAINT_CLAUSE.finditer(text)][:12]
    return {
        "stated_intent": first_sentence,
        "deliverable_verbs": deliverables,
        "constraints": constraints,
        "has_numeric_work": bool(_NUMERIC_TASK.search(text)),
        "is_multi_part": bool(_MULTI_PART.search(text)) or text.count("?") > 1,
        "word_count": len(text.split()),
    }


def select_operations(task_text: str, names: list[str] | None = None) -> list[dict]:
    """Select operations for a task, in canonical program order.

    An explicit ``names`` list wins. Otherwise a small always-on spine is
    extended by heuristic matches (constraint-heavy or multi-part tasks
    pull in the corresponding operations).
    """
    ops = load_operations()
    if names:
        unknown = set(names) - {op["name"] for op in ops}
        if unknown:
            raise KeyError(f"unknown operations: {', '.join(sorted(unknown))}")
        return [op for op in ops if op["name"] in set(names)]
    info = analyze_task(task_text)
    selected = {"recover_objective", "execute", "inspect_result", "verify", "deliver"}
    if info["constraints"] or info["word_count"] > 150:
        selected.add("identify_constraints")
    if info["is_multi_part"] or info["word_count"] > 200:
        selected.update({"decompose_problem", "locate_load_bearing_uncertainty"})
    if info["has_numeric_work"] or info["is_multi_part"]:
        selected.add("select_cheapest_discriminating_test")
    selected.update({"classify_failure", "apply_targeted_repair"})
    return [op for op in ops if op["name"] in selected]


def compile_program(task_text: str, mode: str = "prompt", operations: list[str] | None = None):
    """Compile ``task_text`` into a cognitive program.

    ``mode`` selects the output form: ``prose`` (str), ``packet`` (dict),
    or ``prompt`` (str). ``operations`` optionally pins the operation
    names; by default they are selected heuristically.
    """
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, got {mode!r}")
    info = analyze_task(task_text)
    ops = select_operations(task_text, operations)
    packet = {
        "schema": "piensalo/program/v1",
        "task_analysis": info,
        "operations": [
            {
                "name": op["name"],
                "trigger": op["trigger"],
                "procedure": op["procedure"],
                "stop_condition": op["stop_condition"],
                "verification": op["verification"],
                "evidence_status": op["evidence_status"],
            }
            for op in ops
        ],
        "delivery_rules": [
            "Partition the completion claim: delivered-and-verified / "
            "delivered-unverified / not delivered.",
            "Absent output is UNMEASURED, never silently scored.",
            "No repair without a demonstrated, observable defect.",
        ],
    }
    if mode == "packet":
        return packet
    if mode == "prose":
        return _render_prose(task_text, info, ops)
    return _render_prompt(task_text, info, ops)


def _render_prose(task_text: str, info: dict, ops: list[dict]) -> str:
    lines = ["Cognitive program (concise):", ""]
    lines.append(f"Objective (heuristic read): {info['stated_intent'] or '(empty task)'}")
    if info["constraints"]:
        lines.append("Constraints detected:")
        lines.extend(f"  - {c}" for c in info["constraints"])
    lines.append("")
    for i, op in enumerate(ops, 1):
        lines.append(f"{i}. {op['name']}: {op['procedure'][0]} Stop when: {op['stop_condition']}")
    return "\n".join(lines)


def _render_prompt(task_text: str, info: dict, ops: list[dict]) -> str:
    lines = [
        "# Cognitive program",
        "",
        "Work the task below by running these operations in order. Each has a",
        "stop condition — do not continue an operation past it.",
        "",
        f"Interpreted objective (veto if wrong): {info['stated_intent'] or '(none stated)'}",
        "",
    ]
    if info["constraints"]:
        lines.append("## Constraints extracted from the task (check each before delivery)")
        lines.extend(f"- {c}" for c in info["constraints"])
        lines.append("")
    for i, op in enumerate(ops, 1):
        lines.append(f"## {i}. {op['name']}")
        for j, step in enumerate(op["procedure"], 1):
            lines.append(f"{j}. {step}")
        lines.append(f"Stop condition: {op['stop_condition']}")
        lines.append(f"Verify: {op['verification']}")
        lines.append("")
    lines.append("## Task")
    lines.append("")
    lines.append(task_text.strip())
    return "\n".join(lines)


def render_packet_json(packet: dict) -> str:
    """Stable JSON rendering of a compiled packet."""
    return json.dumps(packet, indent=2)
