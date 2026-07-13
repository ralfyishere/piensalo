"""Adapter-assisted consequence extraction with deterministic validation.

An explicitly configured model may PROPOSE candidate consequences and
relevance labels from ordinary prose. Proposals are never truth: every
candidate is validated deterministically — its source span must exist,
its quoted content must appear verbatim inside that span, its schema
fields must be legal — or it is rejected with a recorded reason. Exact
critical text is taken from the source span, never from the model's
paraphrase.

Hybrid mode runs deterministic extraction first and consults the model
only for chunks that remained semantically unclassified (plain blocks).
"""
from __future__ import annotations

import json

from piensalo.context import schema
from piensalo.context.select import Chunk

PROPOSAL_PROMPT = """\
You classify context chunks for a task. For each chunk below, decide if it
contains a consequence a future session must keep: a decision, constraint,
invariant, stop_condition, failed_approach, open_question, open_action,
completed item, or artifact identifier.

Reply with ONE JSON array only. Each element:
{{"chunk_id": "<id>", "record_type": "<type>", "content": "<EXACT quote from
the chunk — copy bytes, do not paraphrase>", "confidence": 0.0-1.0,
"exactness": "EXACT|SEMANTIC|REGENERABLE|DISPOSABLE",
"status": "ACTIVE|CONTESTED|TEMPORARY|UNVERIFIED",
"reason": "<why this matters for the task>"}}
Skip chunks with no consequence. Do not invent content.

TASK:
{task}

CHUNKS:
{chunks}
"""

_ALLOWED_TYPES = {"decision", "constraint", "invariant", "stop_condition",
                  "failed_approach", "open_question", "open_action",
                  "completed", "artifact"}


def validate_proposals(raw_text: str, chunks_by_id: dict[str, Chunk],
                       *, model_provenance: str) -> tuple[list[dict], list[dict]]:
    """Deterministically validate model proposals.

    Returns (accepted, rejected). Every rejection carries a specific
    reason; nothing is silently dropped or silently trusted.
    """
    accepted: list[dict] = []
    rejected: list[dict] = []
    try:
        start = raw_text.index("[")
        end = raw_text.rindex("]") + 1
        proposals = json.loads(raw_text[start:end])
    except (ValueError, json.JSONDecodeError) as e:
        return [], [{"proposal": raw_text[:200],
                     "reason": f"unparseable proposal payload: {e}"}]
    if not isinstance(proposals, list):
        return [], [{"proposal": str(proposals)[:200],
                     "reason": "proposal payload is not a JSON array"}]
    for p in proposals:
        if not isinstance(p, dict):
            rejected.append({"proposal": str(p)[:200],
                             "reason": "proposal is not an object"})
            continue
        cid = p.get("chunk_id")
        chunk = chunks_by_id.get(cid)
        reason = None
        if chunk is None:
            reason = f"unknown chunk_id {cid!r} (invented source span)"
        elif p.get("record_type") not in _ALLOWED_TYPES:
            reason = f"illegal record_type {p.get('record_type')!r}"
        elif not isinstance(p.get("content"), str) or not p["content"]:
            reason = "missing content"
        elif p["content"] not in chunk.content:
            reason = ("content is not a verbatim quote of the source span — "
                      "paraphrase rejected; exact text must come from source")
        elif p.get("exactness") not in schema.EXACTNESS_CLASSES:
            reason = f"illegal exactness {p.get('exactness')!r}"
        elif p.get("status", "ACTIVE") not in ("ACTIVE", "CONTESTED",
                                               "TEMPORARY", "UNVERIFIED"):
            reason = f"illegal proposed status {p.get('status')!r}"
        elif not isinstance(p.get("confidence"), (int, float)) \
                or not 0 <= p["confidence"] <= 1:
            reason = "confidence must be a number in [0, 1]"
        if reason:
            rejected.append({"proposal": {k: p.get(k) for k in
                                          ("chunk_id", "record_type")},
                             "reason": reason})
            continue
        accepted.append({
            "chunk_id": cid,
            "record_type": p["record_type"],
            "content": p["content"],           # verbatim, verified above
            "source": chunk.source,            # hash-anchored span
            "confidence": float(p["confidence"]),
            "exactness": p["exactness"],
            "status": p.get("status", "ACTIVE"),
            "reason": p.get("reason", ""),
            "model_provenance": model_provenance,
        })
    return accepted, rejected


def propose_and_validate(adapter, chunks: list[Chunk], *, task_text: str,
                         hybrid: bool) -> list[Chunk]:
    """Upgrade plain prose chunks using validated model proposals.

    In hybrid mode only unclassified blocks are sent; in adapter-assisted
    mode every block is eligible. Marker records are never overwritten —
    deterministic structure always wins.
    """
    candidates = [c for c in chunks if c.kind in ("block", "artifact_block")]
    if not candidates:
        return chunks
    listing = "\n\n".join(f"[{c.id}]\n{c.content}" for c in candidates)
    response = adapter.complete(
        PROPOSAL_PROMPT.format(task=task_text.strip(), chunks=listing))
    accepted, rejected = validate_proposals(
        response.text, {c.id: c for c in candidates},
        model_provenance=response.resolved_model)
    by_id = {c.id: c for c in chunks}
    for prop in accepted:
        chunk = by_id[prop["chunk_id"]]
        if chunk.kind == "marker_record":
            continue  # deterministic classification is never overwritten
        chunk.record_type = prop["record_type"]
        chunk.kind = "marker_record"
        chunk.status = prop["status"] if prop["confidence"] >= 0.5 \
            else "UNVERIFIED"
        chunk.exactness = prop["exactness"]
        chunk.content = prop["content"]        # exact verified quote
        chunk.tokens = max(1, (len(prop["content"]) + 3) // 4)
        chunk.reason = (f"adapter-assisted ({prop['model_provenance']}, "
                        f"confidence {prop['confidence']}): {prop['reason']}")
    # Rejections are surfaced on the untouched chunks for the manifest.
    for rej in rejected:
        cid = rej.get("proposal", {}).get("chunk_id") \
            if isinstance(rej.get("proposal"), dict) else None
        if cid and cid in by_id and not by_id[cid].reason:
            by_id[cid].reason = f"model proposal rejected: {rej['reason']}"
    del hybrid  # both modes share this path; markers already win in hybrid
    return chunks
