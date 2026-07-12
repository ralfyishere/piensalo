---
name: hidden-constraint-scan
description: "Extract every constraint buried in the task text — limits, exclusions, format rules, 'must/only/never' clauses — into an explicit list, and check the plan or draft against each one."
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
Every restrictive clause present in the task text appears in the table, and no hard constraint is marked satisfied without a specific supporting location in the work.

**Known risk:** Inflating preferences into hard constraints and over-constraining the solution. Mitigation: the hard/soft classification step forces the distinction.

**Max intended cost:** ≤300 added output tokens; one full re-read of the task text.

**Evidence status:** designed — procedure derived from documented boundary-ignoring and first-representation-acceptance failure modes; this micro-skill itself has no direct experimental test yet.
