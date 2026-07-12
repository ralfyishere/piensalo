---
name: complete-the-delivery
description: "Enumerate every deliverable the request actually asked for and map each one to the work produced. Nothing asked-for is silently dropped, stubbed, or rounded up to done."
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
Every part of the original request appears in the checklist, and no completion claim covers an unmapped or unchecked item.

**Known risk:** Checklist theater on trivial two-part requests. Mitigation: below 3 parts, the mapping is one line, not a table.

**Max intended cost:** ≤250 added output tokens; one re-read of the request.

**Evidence status:** experimentally supported (n=1, controlled transfer eval) — procedure grounded in a documented completion-integrity failure mode (evidence-backed) and a confidence-vs-evidence failure mode.
