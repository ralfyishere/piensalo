---
name: rederive-the-numbers
description: "Independently recompute every derived quantity in the work — sums, percentages, ratios, deltas, projections — from stated inputs, by a different route than the one that produced it, before asserting it."
---

# rederive-the-numbers

**Trigger (observable):** The draft or its inputs contain computed numbers (totals, percentages, growth rates, unit conversions, cost estimates) that the answer asserts or builds a decision on.

**When NOT to activate:** Numbers that are direct quotations from a source (label them as quoted instead); no number is load-bearing for the answer; the same figure was already recomputed this session with the result recorded.

## Procedure
1. Mark every number in the draft as either quoted (traceable to a source verbatim) or derived (computed from other numbers).
2. For each derived number, recompute it independently from the stated inputs — via a different route where possible (recompute the denominator, re-sum in the other order, run actual code for anything beyond trivial arithmetic).
3. On mismatch: stop and locate the divergence (wrong input, wrong formula, stale intermediate) before shipping either figure; never average the two or keep the prettier one.
4. Check units and denominators explicitly — most silent errors are denominator drift or unit mismatch, not arithmetic slips.
5. Label the result: quoted numbers cite their source; derived numbers show enough of the computation to be re-checked.

## Required output
Each load-bearing number tagged quoted/derived; derived ones carry a visible recomputation (inputs → result); mismatches resolved or the number removed.

## Verification
No derived number appears in the final answer without an independent recomputation, and every mismatch found was resolved rather than suppressed.

**Known risk:** Recomputation of throwaway figures nobody acts on. Mitigation: only load-bearing numbers (those a decision or claim rests on) get the treatment.

**Max intended cost:** ≤200 added output tokens; actual code execution for any computation beyond mental arithmetic.

**Evidence status:** designed — procedure derived from a documented confidence-vs-evidence failure mode; this micro-skill itself has no direct experimental test yet.
