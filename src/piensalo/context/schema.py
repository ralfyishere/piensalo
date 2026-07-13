"""Continuation Capsule schema: typed records, statuses, canonical JSON.

Provider-independent by construction: stdlib only, no model SDK, no
network, no credentials. Model provenance (``source_model`` /
``target_model``) is OPTIONAL metadata — nothing in the schema requires
any specific provider or model family.

Determinism contract: identical inputs produce byte-identical capsules.
Therefore nothing in this module reads the clock, the environment, or any
randomness source. ``created_at`` fields are carried as data when the
input supplies them and are null otherwise.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

SCHEMA_VERSION = "context-capsule/1"

DECISION_STATUSES = (
    "ACTIVE",
    "SUPERSEDED",
    "CONTESTED",
    "TEMPORARY",
    "EXPIRED",
    "UNVERIFIED",
)

EXACTNESS_CLASSES = ("EXACT", "SEMANTIC", "REGENERABLE", "DISPOSABLE")

RECORD_TYPES = (
    "objective",
    "success_condition",
    "decision",
    "constraint",
    "invariant",
    "stop_condition",
    "completed",
    "failed_approach",
    "open_question",
    "open_action",
    "next_action",
    "artifact",
    "unstructured",
)

# Record types whose content must survive byte-for-byte (EXACT by default).
_EXACT_BY_DEFAULT = ("stop_condition", "artifact")

# Top-level capsule keys, in canonical order.
CAPSULE_KEYS = (
    "schema_version",
    "capsule_id",
    "source_hash",
    "source_path",
    "compiled_for",
    "mission",
    "state",
    "invariants",
    "decisions",
    "completed",
    "failed_approaches",
    "open_questions",
    "open_actions",
    "active_artifacts",
    "stop_conditions",
    "next_action",
    "references",
    "verification_tests",
    "known_omissions",
    "risk",
    "metrics",
)

RECORD_FIELDS = (
    "id",
    "record_type",
    "status",
    "importance",
    "confidence",
    "exactness",
    "content",
    "provenance",
    "source_reference",
    "created_at",
    "supersedes",
    "superseded_by",
    "expiry",
    "risk_if_omitted",
    "risk_if_stale",
)

REFERENCE_FIELDS = (
    "artifact_id",
    "location",
    "content_type",
    "content_hash",
    "access_policy",
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def default_exactness(record_type: str) -> str:
    return "EXACT" if record_type in _EXACT_BY_DEFAULT else "SEMANTIC"


def make_record(
    record_type: str,
    content: str,
    *,
    status: str = "ACTIVE",
    exactness: str | None = None,
    importance: str = "normal",
    confidence: str = "stated",
    provenance: str | None = None,
    source_reference: dict | None = None,
    created_at: str | None = None,
    supersedes: str | None = None,
    superseded_by: str | None = None,
    expiry: str | None = None,
    risk_if_omitted: str | None = None,
    risk_if_stale: str | None = None,
) -> dict:
    """Build one typed consequence record with a deterministic id."""
    if record_type not in RECORD_TYPES:
        raise ValueError(f"unknown record_type: {record_type!r}")
    if status not in DECISION_STATUSES:
        raise ValueError(f"unknown status: {status!r}")
    exactness = exactness or default_exactness(record_type)
    if exactness not in EXACTNESS_CLASSES:
        raise ValueError(f"unknown exactness: {exactness!r}")
    rid = f"{record_type}-{sha256_text(record_type + chr(10) + content)[:12]}"
    return {
        "id": rid,
        "record_type": record_type,
        "status": status,
        "importance": importance,
        "confidence": confidence,
        "exactness": exactness,
        "content": content,
        "provenance": provenance,
        "source_reference": source_reference,
        "created_at": created_at,
        "supersedes": supersedes,
        "superseded_by": superseded_by,
        "expiry": expiry,
        "risk_if_omitted": risk_if_omitted,
        "risk_if_stale": risk_if_stale,
    }


def dedupe_record_ids(records: list[dict]) -> None:
    """Make duplicate content ids unique deterministically (-2, -3, ...)."""
    seen: dict[str, int] = {}
    for rec in records:
        base = rec["id"]
        n = seen.get(base, 0) + 1
        seen[base] = n
        if n > 1:
            rec["id"] = f"{base}-{n}"


def canonical_json(obj: Any) -> str:
    """Stable serialization: sorted keys, fixed separators, UTF-8, trailing
    newline. Byte-identical for equal inputs on every platform."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ": "), indent=2) + "\n"


def compute_capsule_id(capsule: dict) -> str:
    """Capsule id = hash of the canonical capsule with its id field blanked.
    Recomputable by anyone; stable across recompilations of equal input."""
    clone = dict(capsule)
    clone["capsule_id"] = ""
    return "cap-" + sha256_text(canonical_json(clone))[:16]


def validate_reference(ref: dict, where: str) -> list[str]:
    errors = []
    if not isinstance(ref, dict):
        return [f"{where}: reference must be an object, got {type(ref).__name__}"]
    for field in REFERENCE_FIELDS:
        if field not in ref:
            errors.append(f"{where}: reference missing field {field!r}")
    return errors


def validate_record(rec: dict, where: str) -> list[str]:
    errors = []
    if not isinstance(rec, dict):
        return [f"{where}: record must be an object, got {type(rec).__name__}"]
    for field in RECORD_FIELDS:
        if field not in rec:
            errors.append(f"{where}: missing field {field!r}")
    if rec.get("record_type") not in RECORD_TYPES:
        errors.append(f"{where}: unknown record_type {rec.get('record_type')!r}")
    if rec.get("status") not in DECISION_STATUSES:
        errors.append(f"{where}: unknown status {rec.get('status')!r}")
    if rec.get("exactness") not in EXACTNESS_CLASSES:
        errors.append(f"{where}: unknown exactness {rec.get('exactness')!r}")
    if not isinstance(rec.get("content"), str) or not rec.get("content"):
        errors.append(f"{where}: content must be a non-empty string")
    if rec.get("source_reference") is not None:
        errors.extend(validate_reference(rec["source_reference"],
                                         f"{where}.source_reference"))
    return errors


_RECORD_LIST_KEYS = (
    "invariants", "decisions", "completed", "failed_approaches",
    "open_questions", "open_actions", "active_artifacts", "stop_conditions",
)


def validate_capsule(capsule: dict) -> list[str]:
    """Return a list of specific validation errors; empty means valid.

    Honest failure: nothing is silently defaulted — a missing or malformed
    field is reported, never repaired.
    """
    errors: list[str] = []
    if not isinstance(capsule, dict):
        return ["capsule must be a JSON object"]
    for key in CAPSULE_KEYS:
        if key not in capsule:
            errors.append(f"capsule missing key {key!r}")
    if errors:
        return errors
    if capsule["schema_version"] != SCHEMA_VERSION:
        errors.append(
            f"schema_version {capsule['schema_version']!r} != {SCHEMA_VERSION!r}")
    for key in _RECORD_LIST_KEYS:
        val = capsule[key]
        if not isinstance(val, list):
            errors.append(f"{key} must be a list")
            continue
        for i, rec in enumerate(val):
            errors.extend(validate_record(rec, f"{key}[{i}]"))
    cf = capsule["compiled_for"]
    if not isinstance(cf, dict):
        errors.append("compiled_for must be an object")
    else:
        for field in ("goal", "source_model", "target_model", "token_budget"):
            if field not in cf:
                errors.append(f"compiled_for missing field {field!r}")
        if not isinstance(cf.get("token_budget"), int):
            errors.append("compiled_for.token_budget must be an integer")
    mission = capsule["mission"]
    if not isinstance(mission, dict) or "objective" not in mission \
            or "success_conditions" not in mission:
        errors.append("mission must contain objective and success_conditions")
    if not isinstance(capsule["references"], dict):
        errors.append("references must be an object")
    else:
        for name, ref in capsule["references"].items():
            errors.extend(validate_reference(ref, f"references[{name!r}]"))
    if not isinstance(capsule["next_action"], str):
        errors.append("next_action must be a string")
    if not isinstance(capsule["known_omissions"], list):
        errors.append("known_omissions must be a list")
    risk = capsule["risk"]
    if not isinstance(risk, dict) or "behavioral_equivalence" not in risk:
        errors.append("risk must declare behavioral_equivalence")
    elif risk["behavioral_equivalence"] != "UNMEASURED":
        # This MVP performs no behavioral verification; any other value
        # would be a fabricated claim.
        errors.append(
            "risk.behavioral_equivalence must be 'UNMEASURED' in this "
            f"schema version, got {risk['behavioral_equivalence']!r}")
    # Cross-link consistency: SUPERSEDED requires superseded_by; a live
    # supersedes pointer requires the target to exist and point back.
    all_records = {r["id"]: r for k in _RECORD_LIST_KEYS for r in capsule[k]
                   if isinstance(r, dict) and "id" in r}
    for rec in all_records.values():
        rid = rec["id"]
        if rec.get("status") == "SUPERSEDED" and not rec.get("superseded_by"):
            errors.append(f"{rid}: SUPERSEDED without superseded_by")
        target = rec.get("supersedes")
        if target:
            if target not in all_records:
                errors.append(f"{rid}: supersedes unknown record {target!r}")
            elif all_records[target].get("superseded_by") != rid:
                errors.append(
                    f"{rid}: supersedes {target} but target's superseded_by "
                    f"is {all_records[target].get('superseded_by')!r}")
    return errors


def load_capsule(path: str) -> dict:
    """Load and validate a capsule file; raise ValueError with every
    specific problem on failure."""
    from pathlib import Path
    p = Path(path)
    if p.is_dir():
        p = p / "capsule.json"
    if not p.is_file():
        raise ValueError(f"capsule not found: {p}")
    try:
        capsule = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"capsule is not valid JSON: {p}: {e}") from e
    errors = validate_capsule(capsule)
    if errors:
        raise ValueError(f"invalid capsule {p}:\n  " + "\n  ".join(errors))
    return capsule


def iter_records(capsule: dict):
    """Yield every consequence record in canonical section order."""
    for key in _RECORD_LIST_KEYS:
        yield from capsule[key]


RECORD_LIST_KEYS = _RECORD_LIST_KEYS
