---
name: disqualifier-scan
description: "Before shipping, sweep for conditions that void the entire answer regardless of its quality — violated mandatory rules, missing required elements, forbidden resources, wrong output form. A hit is fixed, never caveated."
license: MIT
---

# disqualifier-scan

**Trigger (observable):** The task defines pass/fail conditions, mandatory requirements, or a required format — or any deliverable is about to be declared finished against a spec, rubric, or submission rule set.

**When NOT to activate:** No external spec or rule set exists to disqualify against; early drafting where the structure is still moving; the same scan already ran on this draft version.

## Procedure
1. List every condition that would make the answer worth zero regardless of its other qualities: mandatory elements, format requirements, prohibited content or resources, scope rules, eligibility criteria. Take them from the task/spec, not from imagination.
2. Check the draft against each disqualifier one at a time; quote the evidence for any hit.
3. Any hit is repaired before shipping — a disclosed disqualifier is still a disqualifier; writing it down does not resolve it.
4. If a disqualifier cannot be repaired, the verdict is 'does not qualify', stated first — not a polished delivery with a caveat.
5. Record which disqualifiers were checked, so the final claim is scoped to what was actually swept.

## Required output
A disqualifier list with per-item check results (pass / HIT with quoted evidence / not-checkable), placed before the completion claim.

## Verification
- Every listed disqualifier traces to an explicit condition in the task/spec text.
- No disqualifier hit survives into the shipped version — each hit is fixed, or the verdict is changed to does-not-qualify. Disclosure alone never clears a hit.
- Net effect: every mandatory condition stated in the task/spec appears in the list, and no hit ships undeclared or merely caveated.

**Known risk:** Sweeping invented disqualifiers that the spec never stated, burning tokens on phantom rules. Mitigation: step 1 requires each item to trace to the task text.

**Max intended cost:** ≤250 added output tokens; re-read of the spec's requirement clauses.

**Evidence status:** EXPERIMENTALLY_TESTED — this repair content lifted a weak model on procedural tasks in controlled runs; the effect is task-concentrated, and automatic router selection of micro-skills is a separate, unproven layer.

**Lineage:** Grounded in an evidence-backed completion-integrity principle (a deliverable is not done while a voiding condition stands) and in a documented reasoning-failure mode — verifying surface form while missing the semantic requirements; applies the disqualifier-sweep pattern from the broader Fable Think skill family.
