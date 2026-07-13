"""Deterministic transcript parsers (plain text and JSONL).

Honesty contract: this parser recognizes EXPLICIT structure only. It never
infers a decision, constraint, or next action from free prose — arbitrary
natural-language consequence extraction is NOT deterministically solved,
and pretending otherwise would fabricate capsule content. Unstructured
material is preserved by source reference and surfaced as a known
omission (or, for unknown JSONL objects, an UNVERIFIED record) — never
invented into a typed consequence.

Recognized plain-text markers (line-anchored; one optional bracket tag —
either a decision status like [CONTESTED] or an exactness class like
[EXACT])::

    OBJECTIVE:            SUCCESS CONDITION:      DECISION:
    SUPERSEDES:           CONSTRAINT:             INVARIANT:
    STOP CONDITION:       COMPLETED:              FAILED APPROACH:
    OPEN QUESTION:        OPEN ACTION:            NEXT ACTION:
    ARTIFACT:             EXPIRES:

Continuation lines (indented by two+ spaces or a tab) extend the previous
marker's content. Everything else is unstructured.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from piensalo.context import schema

MARKER_TO_TYPE = {
    "OBJECTIVE": "objective",
    "SUCCESS CONDITION": "success_condition",
    "DECISION": "decision",
    "CONSTRAINT": "constraint",
    "INVARIANT": "invariant",
    "STOP CONDITION": "stop_condition",
    "COMPLETED": "completed",
    "FAILED APPROACH": "failed_approach",
    "OPEN QUESTION": "open_question",
    "OPEN ACTION": "open_action",
    "NEXT ACTION": "next_action",
    "ARTIFACT": "artifact",
}

_DIRECTIVE_MARKERS = ("SUPERSEDES", "EXPIRES")

_MARKER_RE = re.compile(
    r"^(?P<marker>" + "|".join(
        re.escape(m) for m in tuple(MARKER_TO_TYPE) + _DIRECTIVE_MARKERS
    ) + r")(?:\s*\[(?P<tag>[A-Z]+)\])?:\s*(?P<rest>.*)$"
)
_CONTINUATION_RE = re.compile(r"^(?:  +|\t)(?P<rest>\S.*)$")

_JSONL_RECORD_KEYS = {
    "type", "content", "status", "exactness", "supersedes", "expiry",
    "created_at", "importance", "confidence",
}


class ParseError(ValueError):
    """Honest, specific parse failure — never a silent default."""


@dataclass
class RawItem:
    """One parsed item before compilation."""
    record_type: str
    content: str
    line_start: int
    line_end: int
    status: str = "ACTIVE"
    exactness: str | None = None
    supersedes_text: str | None = None   # unresolved target (text or id)
    expiry: str | None = None
    created_at: str | None = None
    importance: str = "normal"
    confidence: str = "stated"


@dataclass
class ParseResult:
    items: list[RawItem] = field(default_factory=list)
    omissions: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_lines: list[str] = field(default_factory=list)

    def line_span_text(self, start: int, end: int) -> str:
        return "\n".join(self.source_lines[start - 1:end])


def _flush_unstructured(result: ParseResult, start: int, end: int) -> None:
    if start == 0:
        return
    text = result.line_span_text(start, end)
    preview = text if len(text) <= 120 else text[:117] + "..."
    result.omissions.append({
        "kind": "unstructured",
        "lines": f"{start}-{end}",
        "preview": preview,
        "detail": "unstructured content not deterministically classifiable; "
                  "available via source reference, not invented into a record",
    })


def parse_text(text: str, *, artifact_id: str = "transcript") -> ParseResult:
    """Parse a plain-text transcript into raw items + honest omissions."""
    result = ParseResult(source_lines=text.split("\n"))
    current: RawItem | None = None
    last_decision: RawItem | None = None
    unstructured_start = 0
    unstructured_end = 0

    def close_unstructured() -> None:
        nonlocal unstructured_start, unstructured_end
        _flush_unstructured(result, unstructured_start, unstructured_end)
        unstructured_start = unstructured_end = 0

    for lineno, line in enumerate(result.source_lines, 1):
        if not line.strip():
            continue
        m = _MARKER_RE.match(line)
        if m:
            close_unstructured()
            marker, tag, rest = m.group("marker"), m.group("tag"), m.group("rest")
            rest = rest.strip()
            if not rest:
                raise ParseError(f"line {lineno}: {marker}: has no content")
            if marker == "SUPERSEDES":
                if last_decision is None:
                    raise ParseError(
                        f"line {lineno}: SUPERSEDES: appears before any DECISION:")
                if last_decision.supersedes_text is not None:
                    raise ParseError(
                        f"line {lineno}: DECISION at line "
                        f"{last_decision.line_start} already has a SUPERSEDES")
                last_decision.supersedes_text = rest
                current = None
                continue
            if marker == "EXPIRES":
                if current is None:
                    raise ParseError(
                        f"line {lineno}: EXPIRES: appears before any record")
                current.expiry = rest
                continue
            status = "ACTIVE"
            exactness: str | None = None
            if tag:
                if tag in schema.DECISION_STATUSES:
                    status = tag
                elif tag in schema.EXACTNESS_CLASSES:
                    exactness = tag
                else:
                    raise ParseError(
                        f"line {lineno}: unknown tag [{tag}] (allowed: "
                        f"{', '.join(schema.DECISION_STATUSES)} or "
                        f"{', '.join(schema.EXACTNESS_CLASSES)})")
            current = RawItem(
                record_type=MARKER_TO_TYPE[marker],
                content=rest,
                line_start=lineno,
                line_end=lineno,
                status=status,
                exactness=exactness,
            )
            result.items.append(current)
            if current.record_type == "decision":
                last_decision = current
            continue
        cont = _CONTINUATION_RE.match(line)
        if cont and current is not None:
            current.content += "\n" + cont.group("rest")
            current.line_end = lineno
            continue
        # Unstructured line.
        current = None
        if unstructured_start == 0:
            unstructured_start = lineno
        unstructured_end = lineno
    close_unstructured()
    return result


def _parse_jsonl_typed(obj: dict, lineno: int) -> RawItem:
    unknown = set(obj) - _JSONL_RECORD_KEYS
    if unknown:
        raise ParseError(
            f"line {lineno}: unknown record field(s): {', '.join(sorted(unknown))}")
    rtype = obj["type"]
    if rtype not in schema.RECORD_TYPES or rtype == "unstructured":
        allowed = ", ".join(t for t in schema.RECORD_TYPES if t != "unstructured")
        raise ParseError(
            f"line {lineno}: unknown record type {rtype!r} (allowed: {allowed})")
    content = obj.get("content")
    if not isinstance(content, str) or not content:
        raise ParseError(f"line {lineno}: record content must be a non-empty string")
    status = obj.get("status", "ACTIVE")
    if status not in schema.DECISION_STATUSES:
        raise ParseError(
            f"line {lineno}: unknown status {status!r} "
            f"(allowed: {', '.join(schema.DECISION_STATUSES)})")
    exactness = obj.get("exactness")
    if exactness is not None and exactness not in schema.EXACTNESS_CLASSES:
        raise ParseError(
            f"line {lineno}: unknown exactness {exactness!r} "
            f"(allowed: {', '.join(schema.EXACTNESS_CLASSES)})")
    return RawItem(
        record_type=rtype,
        content=content,
        line_start=lineno,
        line_end=lineno,
        status=status,
        exactness=exactness,
        supersedes_text=obj.get("supersedes"),
        expiry=obj.get("expiry"),
        created_at=obj.get("created_at"),
        importance=obj.get("importance", "normal"),
        confidence=obj.get("confidence", "stated"),
    )


def parse_jsonl(text: str, *, artifact_id: str = "transcript") -> ParseResult:
    """Parse a JSONL transcript.

    Three line shapes are accepted:
    - typed record objects (``{"type": "decision", "content": ...}``);
    - message objects (``{"role": ..., "content": ...}``) whose content is
      scanned with the plain-text marker parser;
    - any other JSON object becomes an UNVERIFIED unstructured record —
      preserved, never reinterpreted.
    A line that is not valid JSON is a hard, specific error.
    """
    result = ParseResult(source_lines=text.split("\n"))
    for lineno, line in enumerate(result.source_lines, 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            raise ParseError(f"line {lineno}: invalid JSON: {e}") from e
        if not isinstance(obj, dict):
            raise ParseError(
                f"line {lineno}: each JSONL line must be an object, "
                f"got {type(obj).__name__}")
        if "type" in obj:
            result.items.append(_parse_jsonl_typed(obj, lineno))
            continue
        if "role" in obj and isinstance(obj.get("content"), str):
            inner = parse_text(obj["content"])
            last_decision_offsetted: RawItem | None = None
            for item in inner.items:
                item.line_start = item.line_end = lineno
                result.items.append(item)
                if item.record_type == "decision":
                    last_decision_offsetted = item
            del last_decision_offsetted
            for om in inner.omissions:
                om["lines"] = str(lineno)
                om["detail"] += f" (inside message at line {lineno})"
                result.omissions.append(om)
            result.warnings.extend(inner.warnings)
            continue
        # Unknown object shape: preserved as an UNVERIFIED record.
        result.items.append(RawItem(
            record_type="unstructured",
            content=json.dumps(obj, sort_keys=True, ensure_ascii=False),
            line_start=lineno,
            line_end=lineno,
            status="UNVERIFIED",
            exactness="EXACT",
        ))
        result.warnings.append(
            f"line {lineno}: unrecognized JSONL object preserved as an "
            "UNVERIFIED record (not reinterpreted)")
    return result


def parse_transcript(text: str, fmt: str) -> ParseResult:
    if fmt == "text":
        return parse_text(text)
    if fmt == "jsonl":
        return parse_jsonl(text)
    raise ParseError(f"unknown transcript format: {fmt!r} (text|jsonl)")


def detect_format(path: str) -> str:
    return "jsonl" if str(path).lower().endswith((".jsonl", ".ndjson")) else "text"
