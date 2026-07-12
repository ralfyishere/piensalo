---
name: disqualifier-scan
description: "Before shipping, sweep for conditions that void the entire answer regardless of its quality — violated mandatory rules, missing required elements, forbidden resources, wrong output form. A hit is fixed, never caveated."
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
Every mandatory condition stated in the task/spec appears in the list, and no hit survives into the shipped version undeclared or merely caveated.

**Known risk:** Sweeping invented disqualifiers that the spec never stated, burning tokens on phantom rules. Mitigation: step 1 requires each item to trace to the task text.

**Max intended cost:** ≤250 added output tokens; re-read of the spec's requirement clauses.

**Evidence status:** experimentally supported (n=1, controlled transfer eval) — procedure grounded in a documented completion-integrity failure mode and a syntax-not-semantics verification failure mode.
