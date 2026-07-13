"""Task-specific chunking, classification, and inspectable selection.

Every chunk receives a factor-by-factor score (never only an opaque
number) and a disposition explaining exactly why it was included, omitted,
or referenced. Mandatory context is preserved unconditionally; if the
mandatory set alone exceeds the budget, optimization is REFUSED rather
than truncated.

Deterministic: lexical relevance, explicit structure, recency, and
duplication only. No semantic invention — a chunk the scorer cannot
justify is omitted with a reason and remains recoverable by reference.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from piensalo.context import parser as marker_parser
from piensalo.context import schema
from piensalo.context.ingest import NormalizedItem
from piensalo.context.tokens import estimate_tokens

DISPOSITIONS = (
    "INCLUDED_MANDATORY",
    "INCLUDED_RELEVANT",
    "OMITTED_DUPLICATE",
    "OMITTED_SUPERSEDED",
    "OMITTED_LOW_RELEVANCE",
    "OMITTED_REGENERABLE",
    "REFERENCED_NOT_INLINE",
    "REQUIRES_EXPANSION",
)

# Marker record types that are mandatory whenever active: losing any of
# these changes behavior, not just wording.
_MANDATORY_TYPES = {
    "objective", "success_condition", "constraint", "invariant",
    "stop_condition", "next_action", "artifact", "decision",
}
_ACTIVE_STATUSES = ("ACTIVE", "CONTESTED", "TEMPORARY")

_CRITICALITY = {
    "constraint": 1.0, "invariant": 1.0, "stop_condition": 1.0,
    "decision": 0.9, "failed_approach": 0.85, "artifact": 0.8,
    "objective": 0.9, "success_condition": 0.85, "next_action": 0.9,
    "open_action": 0.6, "open_question": 0.5, "completed": 0.4,
    "unstructured": 0.3,
}
_EXACTNESS_WEIGHT = {"EXACT": 1.0, "SEMANTIC": 0.6, "REGENERABLE": 0.2,
                     "DISPOSABLE": 0.0}
_ROLE_WEIGHT = {"system": 0.9, "user": 0.7, "assistant": 0.5, "tool": 0.4,
                "artifact": 0.5, "text": 0.5}

_WORD_RE = re.compile(r"[a-z0-9_./\\-]{3,}")
_STOPWORDS = frozenset(
    "the and for with that this from are was were been being have has had "
    "not you your our they them then than into onto over under about after "
    "before because while where when what which who whom whose all any each "
    "few more most other some such only own same very can will just should "
    "could would does did doing its their there here also may might must "
    "shall let may".split())


def _words(text: str) -> set[str]:
    return {w for w in _WORD_RE.findall(text.lower()) if w not in _STOPWORDS}


@dataclass
class Chunk:
    id: str
    kind: str                     # marker_record | block | artifact_block
    content: str
    record_type: str | None
    status: str
    exactness: str
    tokens: int
    source: dict
    item_index: int
    role: str
    tool_name: str | None = None
    artifact_ref: str | None = None
    score_factors: dict = field(default_factory=dict)
    score: float = 0.0
    disposition: str = ""
    reason: str = ""
    supersedes: str | None = None
    superseded_by: str | None = None


def _chunk_id(kind: str, content: str) -> str:
    return f"{kind}-{schema.sha256_text(kind + chr(10) + content)[:12]}"


def _dedupe_ids(chunks: list[Chunk]) -> None:
    seen: dict[str, int] = {}
    for c in chunks:
        n = seen.get(c.id, 0) + 1
        seen[c.id] = n
        if n > 1:
            c.id = f"{c.id}-{n}"


_ARTIFACT_WINDOW = 40  # lines per artifact block


def _blocks(text: str) -> list[tuple[str, int, int]]:
    """Split prose into paragraph blocks -> (text, line_start, line_end)."""
    out: list[tuple[str, int, int]] = []
    start = None
    buf: list[str] = []
    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        if line.strip():
            if start is None:
                start = i
            buf.append(line)
        elif start is not None:
            out.append(("\n".join(buf), start, i - 1))
            start, buf = None, []
    if start is not None:
        out.append(("\n".join(buf), start, len(lines)))
    return out


def chunk_items(items: list[NormalizedItem]) -> list[Chunk]:
    """Chunk normalized items; marker structure is honored exactly once."""
    chunks: list[Chunk] = []
    for item in items:
        base_ref = item.source_reference()
        if item.role == "artifact":
            lines = item.content.split("\n")
            for w in range(0, len(lines), _ARTIFACT_WINDOW):
                part = "\n".join(lines[w:w + _ARTIFACT_WINDOW])
                if not part.strip():
                    continue
                end = min(w + _ARTIFACT_WINDOW, len(lines))
                loc = f"{item.source_location}:lines:{w + 1}-{end}"
                chunks.append(Chunk(
                    id=_chunk_id("artifact", part), kind="artifact_block",
                    content=part, record_type=None, status="ACTIVE",
                    exactness="EXACT", tokens=estimate_tokens(part),
                    source={**base_ref, "location": loc,
                            "content_hash": schema.sha256_text(part)},
                    item_index=item.index, role=item.role,
                    artifact_ref=item.artifact_ref))
            continue
        parsed = marker_parser.parse_text(item.content)
        directives = {id(raw): raw.supersedes_text for raw in parsed.items}
        raw_chunks: list[tuple[Chunk, str | None]] = []
        for raw in parsed.items:
            span = parsed.line_span_text(raw.line_start, raw.line_end)
            chunk = Chunk(
                id=_chunk_id(raw.record_type, raw.content),
                kind="marker_record", content=raw.content,
                record_type=raw.record_type, status=raw.status,
                exactness=raw.exactness or schema.default_exactness(
                    raw.record_type),
                tokens=estimate_tokens(raw.content),
                source={**base_ref,
                        "location": f"{item.source_location}"
                                    f"+lines:{raw.line_start}-{raw.line_end}",
                        "content_hash": schema.sha256_text(span)},
                item_index=item.index, role=item.role,
                tool_name=item.tool_name)
            raw_chunks.append((chunk, directives[id(raw)]))
        # Resolve supersession among marker chunks (nearest earlier match).
        for pos, (chunk, target_text) in enumerate(raw_chunks):
            if not target_text:
                continue
            for j in range(pos - 1, -1, -1):
                cand = raw_chunks[j][0]
                if cand.content == target_text or cand.id == target_text:
                    chunk.supersedes = cand.id
                    cand.superseded_by = chunk.id
                    if cand.status in _ACTIVE_STATUSES:
                        cand.status = "SUPERSEDED"
                    break
        chunks.extend(c for c, _ in raw_chunks)
        for om in parsed.omissions:  # unstructured spans -> prose blocks
            a, b = (int(x) for x in om["lines"].split("-")) \
                if "-" in om["lines"] else (int(om["lines"]),) * 2
            span = parsed.line_span_text(a, b)
            for text, ls, le in _blocks(span):
                chunks.append(Chunk(
                    id=_chunk_id("block", text), kind="block", content=text,
                    record_type=None, status="ACTIVE", exactness="SEMANTIC",
                    tokens=estimate_tokens(text),
                    source={**base_ref,
                            "location": f"{item.source_location}"
                                        f"+lines:{a + ls - 1}-{a + le - 1}",
                            "content_hash": schema.sha256_text(text)},
                    item_index=item.index, role=item.role,
                    tool_name=item.tool_name))
    _dedupe_ids(chunks)
    return chunks


def score_chunks(chunks: list[Chunk], task_text: str,
                 task_artifacts: tuple[str, ...] = ()) -> None:
    """Attach inspectable score factors to every chunk (in place)."""
    task_words = _words(task_text) | _words(" ".join(task_artifacts))
    total = max(1, len(chunks))
    for c in chunks:
        cw = _words(c.content)
        shared = sorted(task_words & cw)
        relevance = min(1.0, len(shared) / 6.0)
        criticality = _CRITICALITY.get(c.record_type or "", 0.0) \
            if c.kind == "marker_record" else \
            (_ROLE_WEIGHT.get(c.role, 0.4) * 0.5)
        exact_w = _EXACTNESS_WEIGHT[c.exactness]
        artifact_dep = 1.0 if c.artifact_ref and any(
            a in (c.artifact_ref or "") or (c.artifact_ref or "") in a
            for a in task_artifacts) else 0.0
        recency = (c.item_index + 1) / total if total > 1 else 0.5
        status_w = {"ACTIVE": 1.0, "CONTESTED": 0.8, "TEMPORARY": 0.8,
                    "UNVERIFIED": 0.4}.get(c.status, 0.0)
        score = (0.45 * relevance + 0.25 * criticality + 0.10 * exact_w
                 + 0.10 * artifact_dep + 0.05 * recency) * max(status_w, 0.1)
        c.score_factors = {
            "task_relevance": round(relevance, 4),
            "shared_terms": shared[:12],
            "criticality": criticality,
            "exactness_weight": exact_w,
            "artifact_dependency": artifact_dep,
            "recency": round(recency, 4),
            "status_weight": status_w,
            "token_cost": c.tokens,
        }
        c.score = round(score, 6)


@dataclass
class Selection:
    chunks: list[Chunk]
    refused: bool
    refusal_reason: str | None
    mandatory_tokens: int
    selected_tokens: int
    omitted_tokens: int
    expansion_queue: list[str]    # chunk ids, highest value first


def _is_mandatory(c: Chunk, task_words: set[str]) -> bool:
    if c.kind != "marker_record" or c.status not in _ACTIVE_STATUSES:
        return False
    if c.record_type == "failed_approach":
        return bool(task_words & _words(c.content))
    return c.record_type in _MANDATORY_TYPES


def select_chunks(chunks: list[Chunk], *, task_text: str, budget: int,
                  task_artifacts: tuple[str, ...] = (),
                  reserved_tokens: int = 0) -> Selection:
    """Assign a disposition to every chunk under the token budget.

    ``reserved_tokens`` covers the packet envelope (task text, headers)
    so the fit check reflects the real rendered size.
    """
    score_chunks(chunks, task_text, task_artifacts)
    task_words = _words(task_text)
    seen_hashes: dict[str, str] = {}
    available = budget - reserved_tokens

    mandatory: list[Chunk] = []
    optional: list[Chunk] = []
    for c in chunks:
        if c.status in ("SUPERSEDED", "EXPIRED"):
            c.disposition = "OMITTED_SUPERSEDED"
            c.reason = ("superseded/expired: historical truth, recoverable "
                        "by reference, never rendered as current")
            continue
        norm = " ".join(c.content.split())
        if norm in seen_hashes:
            c.disposition = "OMITTED_DUPLICATE"
            c.reason = f"duplicate of {seen_hashes[norm]}"
            continue
        seen_hashes[norm] = c.id
        if c.exactness == "DISPOSABLE":
            c.disposition = "OMITTED_REGENERABLE"
            c.reason = "DISPOSABLE content adds tokens without consequences"
            continue
        if _is_mandatory(c, task_words):
            c.disposition = "INCLUDED_MANDATORY"
            c.reason = (f"active {c.record_type}: omission changes behavior"
                        if c.record_type != "failed_approach" else
                        "failed approach lexically relevant to the task")
            mandatory.append(c)
        else:
            optional.append(c)

    mandatory_tokens = sum(c.tokens for c in mandatory)
    if mandatory_tokens > available:
        for c in optional:
            if not c.disposition:
                c.disposition = "REQUIRES_EXPANSION"
                c.reason = "not evaluated: optimization refused"
        return Selection(
            chunks=chunks, refused=True,
            refusal_reason=(
                f"mandatory context alone is {mandatory_tokens} tokens; "
                f"budget leaves {available} after the task envelope. "
                "Critical information is never truncated — raise the budget "
                "or narrow the task."),
            mandatory_tokens=mandatory_tokens, selected_tokens=0,
            omitted_tokens=sum(c.tokens for c in optional),
            expansion_queue=[])

    remaining = available - mandatory_tokens
    ranked = sorted(optional,
                    key=lambda c: (-c.score, c.tokens, c.id))
    selected_tokens = 0
    expansion_queue: list[str] = []
    low_relevance: list[Chunk] = []
    for c in ranked:
        prose = c.kind in ("block", "artifact_block")
        if c.score < 0.05 or (prose
                              and c.score_factors["task_relevance"] == 0.0
                              and c.score_factors["artifact_dependency"] == 0.0):
            # Prose with zero task connection is a distractor even when the
            # budget has room — task-specific means omitting it, not
            # carrying it because it fits. Recoverable via expansion.
            c.disposition = "OMITTED_LOW_RELEVANCE"
            c.reason = ("no lexical or structural connection to the task "
                        f"(score {c.score}, shared terms "
                        f"{c.score_factors['shared_terms']})")
            low_relevance.append(c)
            continue
        if c.kind == "artifact_block" and c.score_factors[
                "artifact_dependency"] == 0.0 and c.score_factors[
                "task_relevance"] < 0.3:
            c.disposition = "REFERENCED_NOT_INLINE"
            c.reason = ("artifact content not directly task-relevant; the "
                        "packet carries its reference and hash instead")
            expansion_queue.append(c.id)
            continue
        if c.tokens <= remaining:
            c.disposition = "INCLUDED_RELEVANT"
            c.reason = (f"score {c.score}: "
                        + ", ".join(f"{k}={v}" for k, v in
                                    c.score_factors.items()
                                    if k in ("task_relevance", "criticality",
                                             "artifact_dependency")))
            remaining -= c.tokens
            selected_tokens += c.tokens
        else:
            c.disposition = "REQUIRES_EXPANSION"
            c.reason = (f"relevant (score {c.score}) but over budget; "
                        "first in line for bounded expansion")
            expansion_queue.append(c.id)
    # Low-relevance prose joins the END of the expansion queue: bounded
    # expansion can still recover it if verification says something is
    # missing, but only after every genuinely relevant chunk.
    expansion_queue.extend(c.id for c in low_relevance)
    omitted_tokens = sum(c.tokens for c in chunks
                         if c.disposition.startswith("OMITTED")
                         or c.disposition in ("REQUIRES_EXPANSION",
                                              "REFERENCED_NOT_INLINE"))
    return Selection(chunks=chunks, refused=False, refusal_reason=None,
                     mandatory_tokens=mandatory_tokens,
                     selected_tokens=selected_tokens,
                     omitted_tokens=omitted_tokens,
                     expansion_queue=expansion_queue)


def manifest(selection: Selection) -> dict:
    """selection-manifest.json: every chunk, its factors, its fate."""
    return {
        "refused": selection.refused,
        "refusal_reason": selection.refusal_reason,
        "mandatory_tokens": selection.mandatory_tokens,
        "selected_tokens": selection.selected_tokens,
        "omitted_tokens": selection.omitted_tokens,
        "expansion_queue": selection.expansion_queue,
        "chunks": [{
            "id": c.id, "kind": c.kind, "record_type": c.record_type,
            "status": c.status, "exactness": c.exactness,
            "tokens": c.tokens, "disposition": c.disposition,
            "reason": c.reason, "score": c.score,
            "score_factors": c.score_factors, "source": c.source,
            "supersedes": c.supersedes, "superseded_by": c.superseded_by,
        } for c in selection.chunks],
    }
