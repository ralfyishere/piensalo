---
name: hidden-constraint-scan
description: "Extract every constraint buried in the task text — limits, exclusions, format rules, 'must/only/never' clauses — into an explicit list, and check the plan or draft against each one."
license: MIT
---

# hidden-constraint-scan

**Trigger (observable):** The task text contains restrictive language (must, only, never, without, except, at most, do not) or is long enough (>~150 words) that mid-prompt constraints are likely to fall out of working memory.

**When NOT to activate:** Short requests (<~50 words) already restated in full; constraints already extracted into a checklist this session; brainstorming where no deliverable is being checked.

## Procedure
1. Re-scan the full task text and extract every constraint verbatim — restrictive clauses, format directives, scope exclusions, resource limits, ordering requirements. Quote, don't paraphrase.
2. Classify each as hard (violating it voids the work) or soft (preference).
3. Check the current plan or draft against each hard constraint; mark satisfied / violated / not-yet-applicable.
4. Fix violations before delivery; a soft-constraint trade-off is stated, not silently taken.
5. Keep the constraint list visible in the work so later steps in a long task re-check against it.

## Required output
A constraint table: verbatim quote | hard/soft | status. Violations named before the deliverable is presented.

## Verification
- The constraint table quotes the task text verbatim rather than paraphrasing.
- Every hard constraint carries a satisfied/violated status tied to a specific location in the work; none is marked satisfied without that supporting location.
- Net effect: every restrictive clause present in the task text appears in the table.

**Known risk:** Inflating preferences into hard constraints and over-constraining the solution. Mitigation: the hard/soft classification step forces the distinction.

**Max intended cost:** ≤300 added output tokens; one full re-read of the task text.

**Evidence status:** EXPERIMENTALLY_TESTED — this repair content lifted a weak model on procedural tasks in controlled runs; the effect is task-concentrated, and automatic router selection of micro-skills is a separate, unproven layer.

**Lineage:** Derived from two documented reasoning-failure modes — ignoring stated boundaries mid-task, and locking onto the first mental representation of a task while later clauses go unread — combined with an evidence-backed completion-integrity principle of partitioning the request into checkable parts.
