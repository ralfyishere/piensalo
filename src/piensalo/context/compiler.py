"""The Consequence Compiler: transcript -> Continuation Capsule.

Deterministic and provider-independent: same input bytes, goal, and budget
produce byte-identical capsule.json / resume.md / verification.json on any
platform. No clock, no randomness, no network, no model call, no
credential. ``source_model`` / ``target_model`` are optional pass-through
metadata only.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from piensalo.context import render, schema
from piensalo.context.parser import ParseResult, RawItem, parse_transcript
from piensalo.context.tokens import ESTIMATOR, estimate_tokens

# Sections a raw record type lands in.
_TYPE_TO_KEY = {
    "decision": "decisions",
    "constraint": "invariants",
    "invariant": "invariants",
    "stop_condition": "stop_conditions",
    "completed": "completed",
    "failed_approach": "failed_approaches",
    "open_question": "open_questions",
    "open_action": "open_actions",
    "artifact": "active_artifacts",
    "unstructured": "open_questions",  # UNVERIFIED leftovers stay visible
}

VERIFICATION_TESTS = (
    "schema_valid",
    "capsule_id_stable",
    "serialization_stable",
    "source_hash_integrity",
    "record_reference_integrity",
    "exact_content_preserved_in_resume",
    "superseded_not_rendered_as_active",
    "supersession_links_consistent",
    "next_action_present",
    "stop_conditions_present",
    "token_budget_compliance",
    "behavioral_equivalence",  # always UNMEASURED in this MVP
)


class CompileError(ValueError):
    """Honest compilation failure with a specific reason."""


@dataclass
class CompileResult:
    capsule: dict
    resume_md: str
    verification: dict
    refused: bool


def _make_reference(artifact_id: str, location: str, content: str,
                    content_type: str = "text/plain",
                    access_policy: str = "local") -> dict:
    return {
        "artifact_id": artifact_id,
        "location": location,
        "content_type": content_type,
        "content_hash": schema.sha256_text(content),
        "access_policy": access_policy,
    }


def _record_from_item(item: RawItem, parsed: ParseResult) -> dict:
    span = parsed.line_span_text(item.line_start, item.line_end)
    return schema.make_record(
        item.record_type,
        item.content,
        status=item.status,
        exactness=item.exactness,
        importance=item.importance,
        confidence=item.confidence,
        provenance=f"transcript lines {item.line_start}-{item.line_end}",
        source_reference=_make_reference(
            "transcript", f"lines:{item.line_start}-{item.line_end}", span),
        created_at=item.created_at,
        expiry=item.expiry,
    )


def _resolve_supersessions(items: list[RawItem], records: list[dict],
                           omissions: list[dict], warnings: list[str]) -> None:
    """Link SUPERSEDES directives; unresolved targets are surfaced, never
    silently dropped and never invented."""
    for idx, item in enumerate(items):
        if not item.supersedes_text:
            continue
        rec = records[idx]
        target_idx = None
        for j in range(idx - 1, -1, -1):  # nearest earlier match wins
            if records[j]["content"] == item.supersedes_text \
                    or records[j]["id"] == item.supersedes_text:
                target_idx = j
                break
        if target_idx is None:
            omissions.append({
                "kind": "unresolved_supersession",
                "lines": f"{item.line_start}-{item.line_end}",
                "preview": item.supersedes_text[:120],
                "detail": "SUPERSEDES target matched no earlier record by "
                          "exact content or id; the link is recorded here, "
                          "not invented",
            })
            warnings.append(
                f"unresolved SUPERSEDES at lines {item.line_start}-"
                f"{item.line_end}: {item.supersedes_text!r}")
            continue
        target = records[target_idx]
        rec["supersedes"] = target["id"]
        target["superseded_by"] = rec["id"]
        if target["status"] in ("ACTIVE", "TEMPORARY", "CONTESTED"):
            target["status"] = "SUPERSEDED"


def _last_of(items: list[RawItem], records: list[dict], rtype: str,
             omissions: list[dict]) -> str:
    """Content of the LAST record of a singleton type (objective /
    next_action); earlier ones are preserved as known omissions with their
    source spans — a documented deterministic rule, not an inference."""
    matches = [(i, r) for i, r in enumerate(records)
               if r["record_type"] == rtype]
    if not matches:
        return ""
    for i, r in matches[:-1]:
        omissions.append({
            "kind": f"earlier_{rtype}",
            "lines": f"{items[i].line_start}-{items[i].line_end}",
            "preview": r["content"][:120],
            "detail": f"an earlier {rtype.upper().replace('_', ' ')} was "
                      "restated later; the final statement is carried as "
                      "current, this one remains by reference",
        })
    return matches[-1][1]["content"]


def compile_capsule(
    transcript_text: str,
    *,
    fmt: str,
    goal: str,
    token_budget: int,
    source_path: str = "transcript",
    project_state: dict | None = None,
    project_state_text: str | None = None,
    source_model: str | None = None,
    target_model: str | None = None,
) -> CompileResult:
    """Compile one transcript into capsule + resume + verification report."""
    if not goal or not goal.strip():
        raise CompileError("a non-empty --goal is required")
    if token_budget <= 0:
        raise CompileError(f"token budget must be positive, got {token_budget}")

    parsed = parse_transcript(transcript_text, fmt)
    warnings = list(parsed.warnings)
    omissions = [dict(o) for o in parsed.omissions]

    records = [_record_from_item(item, parsed) for item in parsed.items]
    schema.dedupe_record_ids(records)
    _resolve_supersessions(parsed.items, records, omissions, warnings)

    objective = _last_of(parsed.items, records, "objective", omissions)
    next_action = _last_of(parsed.items, records, "next_action", omissions)
    success_conditions = [r["content"] for r in records
                          if r["record_type"] == "success_condition"]
    if not objective:
        warnings.append("transcript declares no OBJECTIVE")
    if not next_action:
        warnings.append("transcript declares no NEXT ACTION")

    capsule: dict = {
        "schema_version": schema.SCHEMA_VERSION,
        "capsule_id": "",
        "source_hash": schema.sha256_text(transcript_text),
        "source_path": source_path,
        "compiled_for": {
            "goal": goal,
            "source_model": source_model,   # optional metadata, any provider
            "target_model": target_model,   # optional metadata, any provider
            "token_budget": token_budget,
        },
        "mission": {
            "objective": objective,
            "success_conditions": success_conditions,
        },
        "state": project_state if project_state is not None else {},
        "next_action": next_action,
        "references": {
            "transcript": _make_reference(
                "transcript", f"file:{source_path}", transcript_text),
        },
        "verification_tests": list(VERIFICATION_TESTS),
        "known_omissions": omissions,
        "risk": {
            "behavioral_equivalence": "UNMEASURED",
            "unsafe_omissions": [],
            "notes": warnings,
        },
    }
    for key in schema.RECORD_LIST_KEYS:
        capsule[key] = []
    for rec in records:
        key = _TYPE_TO_KEY.get(rec["record_type"])
        if key:
            capsule[key].append(rec)

    if project_state_text is not None:
        capsule["references"]["project_state"] = _make_reference(
            "project_state", "file:project-state.json", project_state_text,
            content_type="application/json")

    # Budget-aware render. Omission entries are appended BEFORE the fit
    # check for each drop, so the rendered packet and the sealed capsule
    # always agree about what was omitted.
    refused = False
    dropped: list[str] = []
    resume_md: str | None = None
    text = render.render_resume(capsule)
    if estimate_tokens(text) <= token_budget:
        resume_md = text
    else:
        for section in render.DROPPABLE_SECTIONS:
            dropped.append(section)
            capsule["known_omissions"].append({
                "kind": "budget_omission",
                "lines": "-",
                "preview": section,
                "detail": f"section {section!r} omitted from resume.md to "
                          f"meet the {token_budget}-token budget; fully "
                          "recoverable from capsule.json",
            })
            text = render.render_resume(capsule,
                                        dropped_sections=tuple(dropped))
            if estimate_tokens(text) <= token_budget:
                resume_md = text
                break
        if resume_md is None:
            # Honest refusal: nothing was partially rendered, so no
            # budget omissions remain recorded.
            refused = True
            capsule["known_omissions"] = [
                om for om in capsule["known_omissions"]
                if om.get("kind") != "budget_omission"]
            capsule["risk"]["notes"] = list(capsule["risk"]["notes"]) + [
                "resume.md refused: critical working set exceeds the "
                "token budget"]
            resume_md = render.render_refusal(capsule, token_budget,
                                              estimate_tokens(text))

    original_tokens = estimate_tokens(transcript_text)
    resume_tokens = estimate_tokens(resume_md)
    capsule["metrics"] = {
        "token_estimator": ESTIMATOR,
        "original_tokens_est": original_tokens,
        "resume_tokens_est": resume_tokens,
        "token_budget": token_budget,
        "resume_within_budget": (not refused) and resume_tokens <= token_budget,
        "gross_compression_ratio_est": (
            round(original_tokens / resume_tokens, 2) if resume_tokens else None
        ),
        "net_savings": "UNMEASURED (retrieval + behavioral verification not "
                       "implemented; a smaller capsule is not automatically "
                       "a successful result)",
    }
    capsule["capsule_id"] = schema.compute_capsule_id(capsule)

    errors = schema.validate_capsule(capsule)
    if errors:  # a compiler bug, surfaced honestly rather than shipped
        raise CompileError(
            "compiled capsule failed its own schema validation:\n  "
            + "\n  ".join(errors))

    from piensalo.context.verify import verify_bundle
    verification = verify_bundle(capsule, resume_md,
                                 transcript_text=transcript_text,
                                 refused=refused)
    return CompileResult(capsule=capsule, resume_md=resume_md,
                         verification=verification, refused=refused)


def compile_to_dir(transcript_path: str, output_dir: str, **kwargs) -> CompileResult:
    """Compile a transcript file and write the three artifacts."""
    from pathlib import Path

    from piensalo.context.parser import detect_format
    tp = Path(transcript_path)
    if not tp.is_file():
        raise CompileError(f"transcript not found: {transcript_path}")
    text = tp.read_text(encoding="utf-8")
    fmt = kwargs.pop("fmt", None) or detect_format(transcript_path)

    ps_path = kwargs.pop("project_state_path", None)
    if ps_path:
        ps_file = Path(ps_path)
        if not ps_file.is_file():
            raise CompileError(f"project-state file not found: {ps_path}")
        ps_text = ps_file.read_text(encoding="utf-8")
        try:
            ps = json.loads(ps_text)
        except json.JSONDecodeError as e:
            raise CompileError(f"project-state is not valid JSON: {e}") from e
        if not isinstance(ps, dict):
            raise CompileError("project-state must be a JSON object")
        kwargs["project_state"] = ps
        kwargs["project_state_text"] = ps_text

    result = compile_capsule(text, fmt=fmt, source_path=str(transcript_path),
                             **kwargs)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "capsule.json").write_text(
        schema.canonical_json(result.capsule), encoding="utf-8")
    (out / "resume.md").write_text(result.resume_md, encoding="utf-8")
    (out / "verification.json").write_text(
        schema.canonical_json(result.verification), encoding="utf-8")
    return result
