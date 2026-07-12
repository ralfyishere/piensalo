---
name: objective-vs-proxy
description: "When a metric, KPI, or threshold drives a decision, check that the number measures the real objective before optimizing or killing anything against it. Diagnose the ruler first. Activate when a decision (fix, kill, ship, prioritize) is justified by a named metric, percentage, or threshold presented as ground truth."
license: MIT
---

# objective-vs-proxy

**Trigger (observable):** A decision (fix, kill, ship, prioritize) is justified by a named metric, KPI, percentage, or threshold presented as ground truth ('40% abandonment', 'CAC > 4x LTV', 'conversion dropped').

**When NOT to activate:** The number was directly recomputed from raw data this session; the decision does not depend on the number; pure reporting tasks where no action hangs on the metric.

## Procedure
1. List every number the decision rests on (metric, denominator, threshold, window).
2. For each, write one measurement-artifact hypothesis: 'this number is wrong because <censoring / benign-case miscounting / denominator drift / stale input / attribution bug>'.
3. Design the cheapest check of the instrument itself (histogram against the cutoff, smoke-test the benign case, recompute the denominator) — and sequence it BEFORE any fix to the measured system.
4. Ask the flip test: if the metric were 30% off, would the proposed action change? If yes, the instrument check is mandatory, not optional.
5. If the instrument is broken, publish the corrected number before trusting any downstream decision built on it.

## Required output
A numbered list: each load-bearing number, its artifact hypothesis, and its cheap instrument probe — sequenced before remediation.

## Verification
- The output names at least one hypothesis in which the metric itself is wrong (censoring, denominator drift, benign-case miscounting) (deterministic check).
- A cheap instrument probe is sequenced before any remediation of the measured system (deterministic check).

**Known risk:** Instrument paranoia: auditing rulers on decisions too small to warrant it, stalling obvious fixes. Mitigation: the flip test in step 4 gates the depth.

**Max intended cost:** ≤300 added output tokens; at most one cheap probe designed (not necessarily run).

**Evidence status:** DESIGNED — specified from documented reasoning-failure modes; not yet executed as a packaged skill.

**Lineage:** Distilled from instrument-check-first sequencing — an evidence-backed repair pattern in which the measurement is diagnosed before the measured system is touched — and from a documented reasoning-failure mode: optimizing or acting on a proxy number while the real objective slips.
