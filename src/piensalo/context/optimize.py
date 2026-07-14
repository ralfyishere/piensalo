"""The Context Optimizer: task-specific budgeted context construction.

Lifecycle implemented here (deterministic portion): full available context
-> chunk + classify -> preserve mandatory -> rank optional by task
relevance -> build a budgeted, target-model-neutral optimized packet.
Model execution and behavioral verification live in ``runtime``/
``evaluate``; without a model run the behavioral status is UNMEASURED.

Refusal is a first-class outcome: when mandatory context cannot fit the
budget, the optimizer refuses instead of truncating critical information.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from piensalo.context import schema, select
from piensalo.context.ingest import NormalizedItem, load_artifacts, load_context_file
from piensalo.context.select import Chunk, Selection
from piensalo.context.tokens import ESTIMATOR, estimate_tokens

SELECTION_METHOD = (
    "deterministic lexical+structural ranking v1 "
    "(inspectable factors; no model call)")

_PACKET_SECTIONS = (
    ("Critical constraints and invariants", ("constraint", "invariant")),
    ("Active decisions", ("decision",)),
    ("Failed approaches — do not repeat these", ("failed_approach",)),
    ("Required artifacts and exact identifiers", ("artifact",)),
    ("Completed work", ("completed",)),
    ("Open questions", ("open_question",)),
    ("Open actions", ("open_action",)),
    ("Stop conditions", ("stop_condition",)),
)


@dataclass
class OptimizeResult:
    packet: str                   # optimized-context.md ("" when refused)
    selection: Selection
    capsule: dict
    report: dict
    refused: bool


def _selected(sel: Selection) -> list[Chunk]:
    return [c for c in sel.chunks
            if c.disposition in ("INCLUDED_MANDATORY", "INCLUDED_RELEVANT")]


def render_packet(task_text: str, sel: Selection, *,
                  extra_chunk_ids: tuple[str, ...] = ()) -> str:
    """Render the neutral optimized packet. No provider-specific content.

    ``extra_chunk_ids`` inlines expansion chunks (bounded expansion path)
    on top of the base selection.
    """
    by_id = {c.id: c for c in sel.chunks}
    included = _selected(sel) + [by_id[i] for i in extra_chunk_ids]
    lines: list[str] = []
    add = lines.append
    add("# Optimized context packet")
    add("")
    add("Task-specific context compiled by PIENSALO Context Optimizer.")
    add("Behavioral status of this packet is reported separately; treat the")
    add("omissions section as authoritative about what was left out.")
    add("")
    add("## Task")
    add("")
    add(task_text.strip())

    markers = {rt: [c for c in included
                    if c.kind == "marker_record" and c.record_type == rt]
               for rt in select._CRITICALITY}
    if markers.get("objective"):
        add("")
        add("## Objective")
        add("")
        for c in markers["objective"]:
            add(c.content)
    if markers.get("success_condition"):
        add("")
        add("## Success conditions")
        add("")
        for c in markers["success_condition"]:
            add(f"- {c.content}")
    for title, types in _PACKET_SECTIONS:
        rows = [c for t in types for c in markers.get(t, [])]
        if not rows:
            continue
        add("")
        add(f"## {title}")
        add("")
        for c in rows:
            tag = f" ({c.status})" if c.status != "ACTIVE" else ""
            add(f"- [{c.id}]{tag}")
            add(c.content)
    evidence = [c for c in included if c.kind in ("block", "artifact_block")]
    if evidence:
        add("")
        add("## Relevant evidence (selected from the source context)")
        add("")
        for c in evidence:
            add(f"- [{c.id}] ({c.source['location']})")
            add(c.content)
    if markers.get("next_action"):
        add("")
        add("## Next action")
        add("")
        add(markers["next_action"][-1].content)

    omitted = [c for c in sel.chunks
               if c.disposition.startswith("OMITTED")
               or c.disposition == "REFERENCED_NOT_INLINE"]
    add("")
    add("## Note on omitted material")
    add("")
    if omitted:
        # Operational phrasing matters: an alarming "N chunks were
        # omitted!" makes models refuse to answer even when every needed
        # fact is present (observed with a real model during evaluation).
        add("Material judged irrelevant to this task "
            f"({len(omitted)} chunk(s), mostly unrelated discussion) was "
            "deliberately filtered out; the sections above contain "
            "everything assessed as necessary for this task, and exact "
            "identifiers are quoted verbatim. Answer directly from the "
            "context above. Only if a fact you are explicitly required to "
            "report is genuinely absent, state that it is missing instead "
            "of guessing.")
    else:
        add("Nothing was omitted; the full source context is above.")
    handles = [c.id for c in sel.chunks
               if c.disposition in ("REQUIRES_EXPANSION",
                                    "REFERENCED_NOT_INLINE")
               and c.id not in extra_chunk_ids]
    if handles:
        add("")
        add("## Expansion handles")
        add("")
        add("If information seems missing, these omitted chunk ids can be")
        add("expanded from selection-manifest.json (highest value first):")
        for h in handles[:10]:
            add(f"- {h}")
    add("")
    return "\n".join(lines)


def _capsule_from_chunks(sel: Selection, *, task_text: str, goal: str,
                         budget: int, source_hash: str, source_path: str,
                         source_model: str | None) -> dict:
    """A valid Continuation Capsule view of the optimization inputs."""
    type_to_key = {
        "decision": "decisions", "constraint": "invariants",
        "invariant": "invariants", "stop_condition": "stop_conditions",
        "completed": "completed", "failed_approach": "failed_approaches",
        "open_question": "open_questions", "open_action": "open_actions",
        "artifact": "active_artifacts",
    }
    capsule: dict = {
        "schema_version": schema.SCHEMA_VERSION,
        "capsule_id": "",
        "source_hash": source_hash,
        "source_path": source_path,
        "compiled_for": {"goal": goal, "source_model": source_model,
                         "target_model": None, "token_budget": budget},
        "mission": {"objective": "", "success_conditions": []},
        "state": {},
        "next_action": "",
        "references": {"context": {
            "artifact_id": "context", "location": f"file:{source_path}",
            "content_type": "text/plain", "content_hash": source_hash,
            "access_policy": "local"}},
        "verification_tests": ["schema_valid", "capsule_id_stable"],
        "known_omissions": [],
        "risk": {"behavioral_equivalence": "UNMEASURED",
                 "unsafe_omissions": [], "notes": []},
    }
    for key in schema.RECORD_LIST_KEYS:
        capsule[key] = []
    id_map: dict[str, str] = {}
    marker_chunks = [c for c in sel.chunks if c.kind == "marker_record"]
    for c in marker_chunks:
        if c.record_type == "objective":
            capsule["mission"]["objective"] = c.content
            continue
        if c.record_type == "success_condition":
            capsule["mission"]["success_conditions"].append(c.content)
            continue
        if c.record_type == "next_action":
            capsule["next_action"] = c.content
            continue
        key = type_to_key.get(c.record_type or "")
        if not key:
            continue
        rec = schema.make_record(
            c.record_type, c.content, status=c.status,
            exactness=c.exactness,
            provenance=f"context {c.source['location']}",
            source_reference=c.source)
        id_map[c.id] = rec["id"]
        capsule[key].append(rec)
    schema.dedupe_record_ids([r for k in schema.RECORD_LIST_KEYS
                              for r in capsule[k]])
    for c in marker_chunks:  # translate supersession links to record ids
        if c.supersedes and c.id in id_map and c.supersedes in id_map:
            for k in schema.RECORD_LIST_KEYS:
                for rec in capsule[k]:
                    if rec["id"] == id_map[c.id]:
                        rec["supersedes"] = id_map[c.supersedes]
                    if rec["id"] == id_map[c.supersedes]:
                        rec["superseded_by"] = id_map[c.id]
    if not capsule["mission"]["objective"]:
        capsule["mission"]["objective"] = f"(task-derived) {task_text.strip()[:200]}"
    for c in sel.chunks:
        if c.disposition.startswith("OMITTED") \
                or c.disposition in ("REQUIRES_EXPANSION",
                                     "REFERENCED_NOT_INLINE"):
            capsule["known_omissions"].append({
                "kind": c.disposition.lower(),
                "lines": c.source["location"],
                "preview": c.content[:120],
                "detail": c.reason,
            })
    capsule["metrics"] = {
        "token_estimator": ESTIMATOR,
        "original_tokens_est": 0,   # set by optimize()
        "resume_tokens_est": 0,
        "token_budget": budget,
        "resume_within_budget": True,
        "gross_compression_ratio_est": None,
        "net_savings": "UNMEASURED (reported by the runtime token ledger)",
    }
    return capsule


def optimize(*, task_text: str, items: list[NormalizedItem], budget: int,
             source_path: str = "context", source_model: str | None = None,
             mode: str = "deterministic",
             extraction_adapter=None) -> OptimizeResult:
    """Build the budgeted optimized packet from normalized context items."""
    if budget <= 0:
        raise ValueError(f"token budget must be positive, got {budget}")
    if mode not in ("deterministic", "adapter-assisted", "hybrid"):
        raise ValueError(f"unknown mode {mode!r}")

    chunks = select.chunk_items(items)
    if mode in ("adapter-assisted", "hybrid"):
        from piensalo.context.extraction import propose_and_validate
        if extraction_adapter is None:
            raise ValueError(
                f"mode {mode!r} requires an explicitly configured "
                "extraction adapter — no model is ever called silently")
        chunks = propose_and_validate(
            extraction_adapter, chunks, task_text=task_text,
            hybrid=(mode == "hybrid"))

    source_text = "\n\n".join(i.content for i in items)
    original_tokens = estimate_tokens(source_text)
    task_artifacts = tuple(sorted({c.artifact_ref for c in chunks
                                   if c.artifact_ref}))
    reserved = estimate_tokens(task_text) + 150  # packet headers/handles
    sel = select.select_chunks(chunks, task_text=task_text, budget=budget,
                               task_artifacts=task_artifacts,
                               reserved_tokens=reserved)
    source_hash = schema.sha256_text(source_text)
    packet = "" if sel.refused else render_packet(task_text, sel)
    optimized_tokens = estimate_tokens(packet)

    capsule = _capsule_from_chunks(
        sel, task_text=task_text, goal=task_text.strip().split("\n")[0][:200],
        budget=budget, source_hash=source_hash, source_path=source_path,
        source_model=source_model)
    capsule["metrics"]["original_tokens_est"] = original_tokens
    capsule["metrics"]["resume_tokens_est"] = optimized_tokens
    capsule["metrics"]["resume_within_budget"] = (
        not sel.refused and optimized_tokens <= budget)
    if optimized_tokens:
        capsule["metrics"]["gross_compression_ratio_est"] = round(
            original_tokens / optimized_tokens, 2)
    capsule["capsule_id"] = schema.compute_capsule_id(capsule)
    errors = schema.validate_capsule(capsule)
    if errors:
        raise ValueError("optimizer capsule failed schema validation:\n  "
                         + "\n  ".join(errors))

    included = _selected(sel)
    report = {
        "task": task_text.strip(),
        "source_context_hash": source_hash,
        "original_tokens_est": original_tokens,
        "mandatory_context_tokens": sel.mandatory_tokens,
        "selected_context_tokens": sel.selected_tokens,
        "omitted_context_tokens": sel.omitted_tokens,
        "optimized_context_tokens": optimized_tokens,
        "gross_reduction": (
            None if sel.refused else round(
                1.0 - optimized_tokens / original_tokens, 4)
            if original_tokens else None),
        "selection_method": SELECTION_METHOD,
        "mode": mode,
        "token_estimator": ESTIMATOR,
        "known_omissions": len(capsule["known_omissions"]),
        "critical_records_retained": sum(
            1 for c in included if c.disposition == "INCLUDED_MANDATORY"),
        "exact_records_retained": sum(
            1 for c in included if c.exactness == "EXACT"),
        "refused": sel.refused,
        "refusal_reason": sel.refusal_reason,
        "risk": {
            "behavioral_equivalence": "UNMEASURED",
            "notes": ([] if not sel.refused else
                      ["OPTIMIZATION REFUSED — full context required"]),
        },
        "behavioral_status": "UNMEASURED",
    }
    return OptimizeResult(packet=packet, selection=sel, capsule=capsule,
                          report=report, refused=sel.refused)


def optimize_to_dir(*, task_path: str, context_path: str,
                    artifact_paths: list[str], budget: int, output_dir: str,
                    source_model: str | None = None,
                    mode: str = "deterministic",
                    extraction_adapter=None) -> OptimizeResult:
    task_file = Path(task_path)
    if not task_file.is_file():
        raise ValueError(f"task file not found: {task_path}")
    task_text = task_file.read_text(encoding="utf-8")
    items = load_context_file(context_path)
    arts = load_artifacts(artifact_paths)
    for a in arts:
        a.index += len(items)
    items = items + arts

    result = optimize(task_text=task_text, items=items, budget=budget,
                      source_path=context_path, source_model=source_model,
                      mode=mode, extraction_adapter=extraction_adapter)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "optimized-context.md").write_text(
        result.packet if not result.refused else
        "OPTIMIZATION REFUSED — FULL CONTEXT REQUIRED\n\n"
        + (result.selection.refusal_reason or "") + "\n",
        encoding="utf-8")
    (out / "selection-manifest.json").write_text(
        schema.canonical_json(select.manifest(result.selection)),
        encoding="utf-8")
    (out / "optimization-report.json").write_text(
        schema.canonical_json(result.report), encoding="utf-8")
    (out / "capsule.json").write_text(
        schema.canonical_json(result.capsule), encoding="utf-8")
    return result
