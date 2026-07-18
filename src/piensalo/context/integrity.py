"""Selection integrity: prove that context-dependent requirements remain
grounded in the selected context before an optimized packet is executed.

Root cause (NR-9): the runtime verified that required output *lines* were
present, not that their *values* stayed grounded in selected chunks — so a
packet that dropped the paragraph carrying the current value verified "pass"
and shipped a superseded or invented value.

This layer is deterministic and provider-neutral. For every contract-declared
requirement it records the candidate source chunks, which of them are in the
packet, and an integrity verdict:

    SUPPORTED        every lexical mention of the requirement is in the packet
    AMBIGUOUS        some mentions are selected, others omitted — the packet
                     cannot prove it carries the current value
    UNSUPPORTED      mentions exist in the source but none are selected
    CONFLICTED       two or more selected ACTIVE marker records compete
    SUPERSEDED_ONLY  only superseded marker records are selected while an
                     active one exists off-packet
    UNMEASURED       the lexical layer finds no mention at all — support
                     cannot be established deterministically

Honesty rule: the evidence type is **lexical-stem** — a SUPPORTED verdict
means "all lexical evidence for this requirement is in view", never semantic
truth. UNMEASURED never counts as support. Optimization proceeds only when
every critical requirement is SUPPORTED; otherwise the runtime expands the
minimum missing chunks, re-evaluates, and falls back to full context when
integrity still cannot be established.
"""
from __future__ import annotations

import re

VERDICTS = ("SUPPORTED", "AMBIGUOUS", "UNSUPPORTED", "CONFLICTED",
            "SUPERSEDED_ONLY", "UNMEASURED")

_INCLUDED = ("INCLUDED_MANDATORY", "INCLUDED_RELEVANT")


def _stem_pattern(name: str) -> re.Pattern:
    """Word-stem match for a requirement identifier: 'PORT' matches port,
    ports; 'VERSION' matches version, versioning. Deterministic, lowercase."""
    return re.compile(r"\b" + re.escape(name.lower()) + r"\w*", re.IGNORECASE)


def requirement_names(contract: dict | None) -> list[str]:
    if not contract:
        return []
    return [f["name"] for f in contract.get("fields", []) if f.get("required", True)]


def _is_selected(chunk, extra_ids: frozenset) -> bool:
    return chunk.disposition in _INCLUDED or chunk.id in extra_ids


def _verdict_for(candidates: list, selected: list) -> str:
    if not candidates:
        return "UNMEASURED"
    if not selected:
        return "UNSUPPORTED"
    # Marker-record supersession truth: a superseded value may remain as
    # history but must never be presented as current merely because it
    # matched a keyword.
    sel_markers = [c for c in selected if getattr(c, "kind", "") == "marker_record"]
    if sel_markers:
        sel_active = [c for c in sel_markers
                      if getattr(c, "status", "") in ("ACTIVE", "CONTESTED", "TEMPORARY")]
        omitted_active = [c for c in candidates
                          if c not in selected
                          and getattr(c, "kind", "") == "marker_record"
                          and getattr(c, "status", "") in ("ACTIVE", "CONTESTED",
                                                           "TEMPORARY")]
        if not sel_active and omitted_active:
            return "SUPERSEDED_ONLY"
        if len(sel_active) >= 2 and any(
                getattr(a, "record_type", "") == "decision" for a in sel_active):
            return "CONFLICTED"
    if any(c not in selected for c in candidates):
        return "AMBIGUOUS"
    return "SUPPORTED"


def evaluate(contract: dict | None, selection, *,
             extra_ids: tuple[str, ...] = ()) -> dict:
    """Deterministic integrity report for a selection against a contract.

    ``extra_ids`` are chunk ids already promoted by expansion (treated as
    selected). Returns a report with a per-requirement record and the gate
    flag ``all_supported``.
    """
    extras = frozenset(extra_ids)
    names = requirement_names(contract)
    chunks = list(getattr(selection, "chunks", []) or [])
    report: dict = {
        "evidence_type": "lexical-stem",
        "note": ("SUPPORTED means every lexical mention of the requirement "
                 "is inside the packet — never semantic truth"),
        "requirements": {},
    }
    for name in names:
        pat = _stem_pattern(name)
        candidates = [c for c in chunks if pat.search(c.content or "")]
        selected = [c for c in candidates if _is_selected(c, extras)]
        verdict = _verdict_for(candidates, selected)
        report["requirements"][name] = {
            "requirement": name,
            "required_evidence": "lexical-stem mention in a selected chunk",
            "candidate_chunks": [c.id for c in candidates],
            "selected_chunks": [c.id for c in selected],
            "missing_chunks": [c.id for c in candidates if c not in selected],
            "verdict": verdict,
        }
    verdicts = [r["verdict"] for r in report["requirements"].values()]
    report["all_supported"] = bool(names) and all(v == "SUPPORTED" for v in verdicts)
    if not names:
        # No contract-declared requirements: integrity has nothing to gate.
        report["all_supported"] = True
        report["note"] += " | no required fields declared: gate vacuously open"
    report["summary"] = {v: verdicts.count(v) for v in VERDICTS if v in verdicts}
    return report


def expansion_ids(report: dict, selection) -> list[str]:
    """The minimum missing chunks: every candidate supporting an
    un-SUPPORTED requirement that is not yet selected, in selection order,
    deduplicated."""
    by_id = {c.id: c for c in getattr(selection, "chunks", []) or []}
    seen: list[str] = []
    for r in report["requirements"].values():
        if r["verdict"] == "SUPPORTED":
            continue
        for cid in r["missing_chunks"]:
            if cid not in seen and cid in by_id:
                seen.append(cid)
    return seen
