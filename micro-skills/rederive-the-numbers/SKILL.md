---
name: rederive-the-numbers
description: "Independently recompute every derived quantity in the work — sums, percentages, ratios, deltas, projections — from stated inputs, by a different route than the one that produced it, before asserting it. Activate when the draft or its inputs contain computed numbers that the answer asserts or builds a decision on."
license: MIT
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
- Every load-bearing number is tagged quoted (with source) or derived (with visible computation) (deterministic check).
- Derived numbers were recomputed independently from stated inputs — by code where non-trivial — and every mismatch found was investigated and resolved rather than suppressed (deterministic check).

**Known risk:** Recomputation of throwaway figures nobody acts on. Mitigation: only load-bearing numbers (those a decision or claim rests on) get the treatment.

**Max intended cost:** ≤200 added output tokens; actual code execution for any computation beyond mental arithmetic.

**Evidence status:** EXPERIMENTALLY_TESTED — micro-skill repair content lifted a weak model on procedural tasks in controlled runs; the effect is task-concentrated, and automatic router selection of micro-skills is a separate, unproven layer.

**Lineage:** Derived from a documented reasoning-failure mode — asserting computed figures with confidence the underlying evidence does not support — combined with instrument-check-first sequencing, an evidence-backed repair pattern.
