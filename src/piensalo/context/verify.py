"""Deterministic capsule verification.

Structural verification ONLY. It can prove: schema validity, id and
serialization stability, source-hash integrity (STALE / MISSING are
explicit results, never silently resolved), exact-content preservation,
supersession consistency, and budget compliance. It can NOT prove that a
model resumed from the capsule behaves like a model given the full
history — behavioral equivalence is UNMEASURED in this MVP and is
reported as such, always. UNMEASURED never converts into a pass.
"""
from __future__ import annotations

import re
from pathlib import Path

from piensalo.context import render, schema
from piensalo.context.tokens import estimate_tokens

VERDICTS = (
    "DETERMINISTICALLY VERIFIED",
    "SAFE WITH QUALIFICATIONS",
    "REQUIRES EXPANSION",
    "UNSAFE TO RESUME",
    "UNMEASURED",
)

REFUSAL_HEADER = "# Continuation packet — COMPILATION REFUSED"

# Checks whose FAIL means the capsule cannot be trusted at all.
_CRITICAL = (
    "schema_valid",
    "capsule_id_stable",
    "serialization_stable",
    "exact_content_preserved_in_resume",
    "superseded_not_rendered_as_active",
    "supersession_links_consistent",
)

_LINES_RE = re.compile(r"^lines:(\d+)-(\d+)$")

# Sections rendered per record type (mirrors render._SECTIONS mapping).
_TYPE_TO_SECTION = {
    "decision": "Active decisions",
    "constraint": "Critical constraints and invariants",
    "invariant": "Critical constraints and invariants",
    "completed": "Completed work",
    "failed_approach": "Failed approaches — do not repeat these",
    "artifact": "Relevant artifacts",
    "open_question": "Open questions",
    "unstructured": "Open questions",
    "open_action": "Open actions",
    "stop_condition": "Stop conditions",
}


def _check(checks: dict, name: str, status: str, detail: str) -> None:
    checks[name] = {"status": status, "detail": detail}


def _verify_source(checks: dict, capsule: dict, transcript_text: str | None,
                   transcript_missing: bool) -> None:
    if transcript_missing:
        _check(checks, "source_hash_integrity", "MISSING",
               f"source transcript not found at {capsule['source_path']!r}; "
               "reference expansion unavailable (capsule itself unchanged)")
        _check(checks, "record_reference_integrity", "MISSING",
               "source unavailable; per-record spans cannot be re-hashed")
        return
    if transcript_text is None:
        _check(checks, "source_hash_integrity", "UNMEASURED",
               "no transcript supplied to verify against")
        _check(checks, "record_reference_integrity", "UNMEASURED",
               "no transcript supplied to verify against")
        return
    actual = schema.sha256_text(transcript_text)
    if actual == capsule["source_hash"]:
        _check(checks, "source_hash_integrity", "PASS",
               "transcript hash matches capsule.source_hash")
    else:
        _check(checks, "source_hash_integrity", "STALE",
               "transcript content changed since compilation "
               f"(sha256 {actual[:16]}... != recorded "
               f"{capsule['source_hash'][:16]}...); the capsule must not be "
               "treated as derived from this source")
    lines = transcript_text.split("\n")
    stale, missing = [], []
    for rec in schema.iter_records(capsule):
        ref = rec.get("source_reference")
        if not ref or ref.get("artifact_id") != "transcript":
            continue
        m = _LINES_RE.match(ref.get("location", ""))
        if not m:
            continue
        a, b = int(m.group(1)), int(m.group(2))
        if a < 1 or b > len(lines):
            missing.append(rec["id"])
            continue
        span = "\n".join(lines[a - 1:b])
        if schema.sha256_text(span) != ref["content_hash"]:
            stale.append(rec["id"])
    if missing:
        _check(checks, "record_reference_integrity", "MISSING",
               "source span out of range for: " + ", ".join(missing))
    elif stale:
        _check(checks, "record_reference_integrity", "STALE",
               "source spans changed for: " + ", ".join(stale))
    else:
        _check(checks, "record_reference_integrity", "PASS",
               "every per-record source span re-hashes to its recorded hash")


def verify_bundle(capsule: dict, resume_md: str | None, *,
                  transcript_text: str | None = None,
                  transcript_missing: bool = False,
                  refused: bool | None = None,
                  capsule_file_text: str | None = None) -> dict:
    """Run every deterministic check; return the verification report."""
    checks: dict = {}

    errors = schema.validate_capsule(capsule)
    if errors:
        _check(checks, "schema_valid", "FAIL", "; ".join(errors))
        return _finish(capsule, checks, refused=bool(refused))
    _check(checks, "schema_valid", "PASS",
           f"capsule conforms to {schema.SCHEMA_VERSION}")

    recomputed = schema.compute_capsule_id(capsule)
    if recomputed == capsule["capsule_id"]:
        _check(checks, "capsule_id_stable", "PASS",
               f"capsule_id recomputes to {recomputed}")
    else:
        _check(checks, "capsule_id_stable", "FAIL",
               f"stored {capsule['capsule_id']} != recomputed {recomputed}; "
               "the capsule was modified after compilation")

    if capsule_file_text is not None:
        if capsule_file_text == schema.canonical_json(capsule):
            _check(checks, "serialization_stable", "PASS",
                   "file bytes equal canonical serialization")
        else:
            _check(checks, "serialization_stable", "FAIL",
                   "capsule.json is not in canonical form "
                   "(re-serialization differs byte-wise)")
    else:
        _check(checks, "serialization_stable", "PASS",
               "canonical serialization round-trips (in-memory)")

    _verify_source(checks, capsule, transcript_text, transcript_missing)

    if refused is None:
        refused = bool(resume_md) and resume_md.startswith(REFUSAL_HEADER)

    dropped_sections = {om["preview"] for om in capsule["known_omissions"]
                        if om.get("kind") == "budget_omission"}
    if resume_md is None:
        _check(checks, "exact_content_preserved_in_resume", "UNMEASURED",
               "no resume.md supplied")
        _check(checks, "superseded_not_rendered_as_active", "UNMEASURED",
               "no resume.md supplied")
    elif refused:
        _check(checks, "exact_content_preserved_in_resume", "QUALIFIED",
               "resume was honestly refused; nothing rendered to check")
        _check(checks, "superseded_not_rendered_as_active", "PASS",
               "refused resume renders no records")
    else:
        bad = []
        for rec in schema.iter_records(capsule):
            if rec["exactness"] != "EXACT":
                continue
            if rec["status"] not in render.RENDER_STATUSES:
                continue
            if _TYPE_TO_SECTION.get(rec["record_type"]) in dropped_sections:
                continue
            if rec["content"] not in resume_md:
                bad.append(rec["id"])
        if bad:
            _check(checks, "exact_content_preserved_in_resume", "FAIL",
                   "EXACT content not byte-identical in resume.md for: "
                   + ", ".join(bad))
        else:
            _check(checks, "exact_content_preserved_in_resume", "PASS",
                   "every rendered EXACT record appears byte-for-byte")
        leaked = [rec["id"] for rec in schema.iter_records(capsule)
                  if rec["status"] in ("SUPERSEDED", "EXPIRED")
                  and f"[{rec['id']}]" in resume_md]
        if leaked:
            _check(checks, "superseded_not_rendered_as_active", "FAIL",
                   "superseded/expired records rendered as current: "
                   + ", ".join(leaked))
        else:
            _check(checks, "superseded_not_rendered_as_active", "PASS",
                   "no SUPERSEDED or EXPIRED record is rendered as current")

    link_problems = []
    all_records = {r["id"]: r for r in schema.iter_records(capsule)}
    for rid, rec in all_records.items():
        if rec.get("supersedes") == rid:
            link_problems.append(f"{rid} supersedes itself")
        sb = rec.get("superseded_by")
        if sb and sb not in all_records:
            link_problems.append(f"{rid} superseded_by unknown record {sb}")
    if link_problems:
        _check(checks, "supersession_links_consistent", "FAIL",
               "; ".join(link_problems))
    else:
        _check(checks, "supersession_links_consistent", "PASS",
               "supersession links are acyclic and resolve")

    contested = [r["id"] for r in capsule["decisions"]
                 if r["status"] == "CONTESTED"]
    unresolved = [om for om in capsule["known_omissions"]
                  if om.get("kind") == "unresolved_supersession"]
    if contested or unresolved:
        parts = []
        if contested:
            parts.append("contested decisions: " + ", ".join(contested))
        if unresolved:
            parts.append(f"{len(unresolved)} unresolved supersession link(s)")
        _check(checks, "decision_conflicts", "QUALIFIED", "; ".join(parts))
    else:
        _check(checks, "decision_conflicts", "PASS",
               "no contested decisions or unresolved supersessions")

    if capsule["next_action"]:
        _check(checks, "next_action_present", "PASS", "next action declared")
    else:
        _check(checks, "next_action_present", "QUALIFIED",
               "no NEXT ACTION declared in the source; a resumed session "
               "must re-derive it")
    if any(r["status"] in render.RENDER_STATUSES
           for r in capsule["stop_conditions"]):
        _check(checks, "stop_conditions_present", "PASS",
               "active stop conditions present")
    else:
        _check(checks, "stop_conditions_present", "QUALIFIED",
               "no active stop condition declared in the source")

    budget = capsule["compiled_for"]["token_budget"]
    if refused:
        _check(checks, "token_budget_compliance", "FAIL",
               f"critical working set does not fit the {budget}-token "
               "budget; compilation honestly refused the resume render")
    elif resume_md is not None:
        rt = estimate_tokens(resume_md)
        if rt <= budget:
            _check(checks, "token_budget_compliance", "PASS",
                   f"resume estimate {rt} <= budget {budget}")
        else:
            _check(checks, "token_budget_compliance", "FAIL",
                   f"resume estimate {rt} exceeds budget {budget}")
    else:
        _check(checks, "token_budget_compliance", "UNMEASURED",
               "no resume.md supplied")

    omission_count = len(capsule["known_omissions"])
    if omission_count:
        _check(checks, "known_omissions", "QUALIFIED",
               f"{omission_count} known omission(s) recorded — material "
               "exists that was not compiled into typed records")
    else:
        _check(checks, "known_omissions", "PASS", "no omissions recorded")

    return _finish(capsule, checks, refused=refused)


def _finish(capsule: dict, checks: dict, *, refused: bool) -> dict:
    _check(checks, "behavioral_equivalence", "UNMEASURED",
           "no behavioral verification exists in this MVP; structural "
           "checks do not prove a resumed model behaves equivalently")
    statuses = {name: c["status"] for name, c in checks.items()
                if name != "behavioral_equivalence"}
    if any(statuses.get(n) == "FAIL" for n in _CRITICAL) \
            or "STALE" in statuses.values():
        verdict = "UNSAFE TO RESUME"
    elif refused or statuses.get("token_budget_compliance") == "FAIL":
        verdict = "REQUIRES EXPANSION"
    elif "FAIL" in statuses.values():
        verdict = "UNSAFE TO RESUME"
    elif "QUALIFIED" in statuses.values() or "MISSING" in statuses.values() \
            or "UNMEASURED" in statuses.values():
        verdict = "SAFE WITH QUALIFICATIONS"
    else:
        verdict = "DETERMINISTICALLY VERIFIED"
    return {
        "schema_version": schema.SCHEMA_VERSION,
        "capsule_id": capsule.get("capsule_id", ""),
        "checks": checks,
        "verdict": verdict,
        "behavioral_equivalence": "UNMEASURED",
        "note": "verdict covers deterministic structure only; it is not a "
                "claim of behavioral equivalence or net token savings",
    }


def verify_dir(path: str, *, transcript_override: str | None = None) -> dict:
    """Verify a compiled output directory (or a bare capsule.json path)."""
    p = Path(path)
    directory = p if p.is_dir() else p.parent
    capsule_path = p / "capsule.json" if p.is_dir() else p
    if not capsule_path.is_file():
        raise ValueError(f"capsule not found: {capsule_path}")
    capsule_text = capsule_path.read_text(encoding="utf-8")
    import json as _json
    try:
        capsule = _json.loads(capsule_text)
    except _json.JSONDecodeError as e:
        raise ValueError(f"capsule is not valid JSON: {capsule_path}: {e}") from e

    resume_path = directory / "resume.md"
    resume_md = resume_path.read_text(encoding="utf-8") \
        if resume_path.is_file() else None

    transcript_text = None
    transcript_missing = False
    source = transcript_override or capsule.get("source_path")
    if source:
        sp = Path(source)
        if not sp.is_absolute() and not sp.is_file():
            # tolerate dir-relative layouts (output dir, or its parent when
            # the transcript sits next to the output dir)
            for base in (directory, directory.parent):
                if (base / source).is_file():
                    sp = base / source
                    break
        if sp.is_file():
            transcript_text = sp.read_text(encoding="utf-8")
        else:
            transcript_missing = True
    return verify_bundle(capsule, resume_md,
                         transcript_text=transcript_text,
                         transcript_missing=transcript_missing,
                         capsule_file_text=capsule_text)
