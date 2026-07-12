---
name: counterexample-search
description: "Before asserting a universal claim — always, never, all, none, guaranteed, impossible — spend one bounded search for a counterexample, starting at the edges of the quantifier's domain."
license: MIT
---

# counterexample-search

**Trigger (observable):** The draft contains a universal quantifier or impossibility claim ('this always terminates', 'no user can reach this state', 'works for all inputs'), or the task asks whether a property holds in general.

**When NOT to activate:** Claims already scoped to observations ('in the 30 cases tested...'); definitional truths (tautologies, type guarantees enforced by a compiler); casual prose where the quantifier is rhetorical and nothing depends on it.

## Procedure
1. Extract each universal claim from the draft verbatim.
2. For each, describe the domain the quantifier ranges over, and go to its edges: empty, zero, one, duplicates, maximum, negative, concurrent, malformed, adversarial.
3. Construct the single most promising counterexample candidate — the edge case with the best chance of breaking the claim — and actually test or trace it, not just contemplate it.
4. If a counterexample is found: weaken the claim to its true scope ('holds for non-empty inputs') or fix the artifact so the claim holds.
5. If none is found after the bounded attempt: keep the claim but note the strongest case tried, so the search is auditable.

## Required output
Per universal claim: the strongest counterexample candidate, the result of actually testing it, and the claim kept / weakened / withdrawn accordingly.

## Verification
- For each universal claim, a specific counterexample candidate is named and actually executed or traced — not just contemplated.
- Claims broken by the search are weakened or withdrawn in the final text.
- Net effect: every universal claim in the final answer either survived a named, executed counterexample attempt or was weakened to observed scope.

**Known risk:** Unbounded hunting — burning the session on exotic cases for low-stakes claims. Mitigation: one strongest candidate per claim, actually tested, then move on.

**Max intended cost:** ≤200 added output tokens plus at most one execution/trace per universal claim.

**Evidence status:** DESIGNED — specified from documented reasoning-failure modes; not yet executed as a packaged skill.

**Lineage:** Derived from a documented reasoning-failure mode — reaching a plausible answer and stopping without probing it — combined with an adversarial-probe verification pattern from the broader Fable Think skill family.
