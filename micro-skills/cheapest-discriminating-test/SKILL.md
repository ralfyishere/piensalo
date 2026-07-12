---
name: cheapest-discriminating-test
description: "With multiple live hypotheses and a limited test budget, design the cheapest single test whose possible outcomes separate the hypotheses — with a results-to-verdict table committed before running anything. Activate when two or more competing hypotheses are on the table and the next step is choosing what test, experiment, or probe to run."
license: MIT
---

# cheapest-discriminating-test

**Trigger (observable):** Two or more competing hypotheses are on the table (bug causes, channel explanations, design options) and the next step is choosing what test, experiment, or probe to run.

**When NOT to activate:** Only one hypothesis exists (generate alternatives first); testing is free and instant, so running everything beats designing; the decision doesn't depend on which hypothesis is true.

## Procedure
1. Write each hypothesis's distinct observable fingerprint: what it predicts that the others do not.
2. Search for the manipulation under which the hypotheses predict DIFFERENT outcomes; prefer one manipulation that separates two or more at once (the unifying discriminant).
3. Pre-commit a discrimination table before running: every possible result row → which hypotheses it kills, confirms, or leaves untouched — including the 'no clear signal' row.
4. Reject any candidate test whose every outcome leaves the hypothesis set unchanged — 'add logging' and 'increase coverage' are gestures, not discriminators.
5. Among surviving tests, run the cheapest; score the actual result against the pre-committed table, not against post-hoc interpretation.

## Required output
The discrimination table (result row → verdict per hypothesis) written before execution, plus the chosen test with its cost rationale.

## Verification
- The results-to-verdict table is committed before the test executes, and it includes the no-signal row.
- At least one outcome of the chosen test kills at least one hypothesis.

**Known risk:** Analysis paralysis designing the perfect discriminant while a cheap sequential test would have settled it. Mitigation: if any single test is near-free, run it first and design after.

**Max intended cost:** ≤350 added output tokens for the table; the test itself is chosen for minimal cost.

**Evidence status:** DESIGNED — specified from documented reasoning-failure modes; not yet executed as a packaged skill.

**Lineage:** Derived from an evidence-backed unifying-discriminant repair pattern (one manipulation that separates multiple hypotheses at once) and a documented reasoning-failure mode: running tests whose every outcome is compatible with every live hypothesis.
