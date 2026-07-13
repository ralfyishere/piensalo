"""resume.md renderer: the L1 active working set, and nothing else.

Renders only ACTIVE / CONTESTED / TEMPORARY truth. SUPERSEDED, EXPIRED and
UNVERIFIED material stays in the capsule (historical truth, reachable by
reference) and is never rendered as current. Output is plain text usable by
pasting into ANY AI system — no provider-specific instructions are added.

EXACT record content is emitted verbatim (byte-for-byte), including
multi-line content, so exactness survives the render.
"""
from __future__ import annotations

RENDER_STATUSES = ("ACTIVE", "CONTESTED", "TEMPORARY")

# (section title, capsule key) in render order.
_SECTIONS = (
    ("Active decisions", "decisions"),
    ("Critical constraints and invariants", "invariants"),
    ("Completed work", "completed"),
    ("Failed approaches — do not repeat these", "failed_approaches"),
    ("Relevant artifacts", "active_artifacts"),
    ("Open questions", "open_questions"),
    ("Open actions", "open_actions"),
    ("Stop conditions", "stop_conditions"),
)

# Sections droppable under budget pressure, in drop order. Decisions,
# constraints, invariants, failed approaches, stop conditions, artifacts
# and the next action are NEVER dropped — losing them changes behavior.
DROPPABLE_SECTIONS = ("Completed work", "Open questions")


def _render_record(rec: dict) -> str:
    prefix = f"- [{rec['id']}]"
    if rec["status"] != "ACTIVE":
        prefix += f" ({rec['status']})"
    if rec.get("expiry"):
        prefix += f" (expires: {rec['expiry']})"
    return f"{prefix}\n{rec['content']}"


def render_resume(capsule: dict, *, dropped_sections: tuple[str, ...] = ()) -> str:
    """Render the continuation packet. Deterministic for equal capsules."""
    mission = capsule["mission"]
    lines: list[str] = []
    add = lines.append
    add("# Continuation packet")
    add("")
    add("Compiled by PIENSALO Context. Deterministic structural compilation;")
    add("behavioral equivalence: UNMEASURED (no behavioral verification was run).")
    add("This packet is plain text and model-independent: paste it into any AI")
    add("system to continue the work described below.")
    add("")
    add(f"Compilation goal: {capsule['compiled_for']['goal']}")
    add("")
    add("## Objective")
    add("")
    add(mission["objective"] if mission["objective"] else
        "(no explicit OBJECTIVE was declared in the source transcript)")
    if mission["success_conditions"]:
        add("")
        add("## Success conditions")
        add("")
        for sc in mission["success_conditions"]:
            add(f"- {sc}")
    for title, key in _SECTIONS:
        if title in dropped_sections:
            continue
        records = [r for r in capsule[key] if r["status"] in RENDER_STATUSES]
        if not records:
            continue
        add("")
        add(f"## {title}")
        add("")
        for rec in records:
            add(_render_record(rec))
    add("")
    add("## Next action")
    add("")
    add(capsule["next_action"] if capsule["next_action"] else
        "(no explicit NEXT ACTION was declared in the source transcript)")
    add("")
    add("## Known limitations")
    add("")
    add("- behavioral equivalence: UNMEASURED — structural checks only.")
    if dropped_sections:
        add("- Omitted under token budget (recoverable from capsule.json): "
            + ", ".join(dropped_sections) + ".")
    for om in capsule["known_omissions"]:
        if om.get("kind") == "budget_omission":
            continue  # covered by the compact dropped-sections line above
        add(f"- [{om.get('kind', 'omission')}] lines {om.get('lines', '?')}: "
            f"{om.get('preview', om.get('detail', ''))}")
    add("")
    add("## Source-expansion references")
    add("")
    add("Every record id above maps to an exact, content-hashed source span in")
    add("capsule.json (references + per-record source_reference). Expand by")
    add("opening the source at the recorded location; a hash mismatch means")
    add("the source changed since compilation (STALE) and must not be trusted")
    add("as the original.")
    for name in sorted(capsule["references"]):
        ref = capsule["references"][name]
        add(f"- {name}: {ref['location']} "
            f"(sha256 {ref['content_hash'][:16]}..., {ref['access_policy']})")
    add("")
    return "\n".join(lines)


def render_refusal(capsule: dict, budget: int, needed: int) -> str:
    """Honest refusal render: never a silently lossy packet."""
    return "\n".join([
        "# Continuation packet — COMPILATION REFUSED (REQUIRES EXPANSION)",
        "",
        f"The token budget ({budget}) is too small to carry the critical",
        f"working set (estimated {needed} tokens) after dropping every",
        "non-critical section. Emitting a lossy packet would silently discard",
        "active decisions, constraints, failed approaches, or stop",
        "conditions — that changes behavior, so PIENSALO Context refuses.",
        "",
        "Options: raise --budget, or split the goal into a narrower task.",
        "The full capsule.json remains available and complete.",
        "",
    ])


__all__ = [
    "render_resume", "render_refusal",
    "RENDER_STATUSES", "DROPPABLE_SECTIONS",
]
