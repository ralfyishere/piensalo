---
name: complete-the-delivery
description: "Enumerate every deliverable the request actually asked for and map each one to the work produced, so nothing asked-for is silently dropped, stubbed, or rounded up to done. Activate when a request contains multiple parts — an enumerated list, several 'and'/'also' clauses, or a spec with more than one required artifact — or before delivering a draft against such a request."
license: MIT
---

# complete-the-delivery

**Trigger (observable):** The request contains multiple parts — an enumerated list, several 'and'/'also' clauses, or a spec with more than one required artifact — or a draft is about to be delivered against such a request.

**When NOT to activate:** Single-deliverable requests with no sub-parts; exploratory conversation where nothing is being delivered; requests explicitly scoped down by the user mid-task (the latest instruction wins).

## Procedure
1. Extract every requested deliverable from the request verbatim into a checklist — including parts embedded mid-sentence ('...and update the index'), format directives, and counts ('3 examples each').
2. Map each checklist item to the specific place in the produced work that satisfies it (file, section, line).
3. For any unmapped item: either complete it now, or declare it explicitly undone with the reason — never let a summary claim ('done', 'all set') span it.
4. Partition the final claim: delivered-and-verified / delivered-unverified / not delivered. 'Unverified' is its own category, never merged into either neighbor.
5. Re-read the original request once, end to end, after the mapping — requests drift out of working memory during long tasks.
6. Blocked-capability rule: if delivering requires a capability unavailable in this session (file-write permission, a tool, network), do not stop at a permission request — deliver the complete artifact inline in the answer and state the substitution in one line.

## Required output
A deliverable checklist with a mapping (item → location) and an explicit status per item; the completion claim quantified ('4 of 5 delivered; #5 undone because X'). Place the checklist BEFORE the deliverable; never append anything after a task-mandated final line.

## Verification
- Every deliverable extractable from the request appears in the checklist with a mapped location or an explicit undone-with-reason status.
- No 'done'/'complete' claim spans an item marked unverified or undone.

**Known risk:** Checklist theater on trivial two-part requests. Mitigation: below 3 parts, the mapping is one line, not a table.

**Max intended cost:** ≤250 added output tokens; one re-read of the request.

**Evidence status:** EXPERIMENTALLY_TESTED — micro-skill repair content lifted a weak model on procedural tasks in controlled runs; the effect is task-concentrated, and automatic router selection of micro-skills is a separate, unproven layer.

**Lineage:** Grounded in an evidence-backed completion-integrity repair pattern (completion claims scoped to what was actually delivered and verified) and a documented reasoning-failure mode: confidence presented at a level the evidence does not support.
