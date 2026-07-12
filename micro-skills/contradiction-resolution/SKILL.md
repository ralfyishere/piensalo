---
name: contradiction-resolution
description: "When inputs contain conflicting facts, stop and resolve the conflict explicitly — classify it, pick a resolution rule, and log what stays unresolved — before building anything on either side. Activate when two sources give different values for the same quantity, a document's claim disagrees with observed state, or the text itself flags inconsistency."
license: MIT
---

# contradiction-resolution

**Trigger (observable):** Two sources in the task give different values for the same quantity, a document's claim disagrees with observed/live state, or the text itself flags inconsistency ('but the dashboard says', 'these numbers don't match').

**When NOT to activate:** Apparent conflicts already resolved by scope (different time windows, different populations) and the scoping is stated; deliberate counterfactuals or A/B arms meant to differ; pure opinion differences with no factual referent.

## Procedure
1. State the contradiction in one sentence naming both sides and their sources ('Doc says jobs 1–3 done; crontab shows job 3 never installed').
2. Classify it: transcription error / version skew / scope difference (different windows, units, populations) / one source stale / genuine conflict.
3. Pick the resolution rule and apply it: live observed state beats documents; recomputation beats quotation; fresher primary beats older secondary. Name which rule was used.
4. Once one claim from a source is proven wrong, downgrade that source's remaining claims to unverified — do not keep trusting its other markers.
5. Anything still unresolved is logged as an explicit caveat attached to every conclusion that depends on it — not dropped because it doesn't block the literal task.

## Required output
A contradiction log: one sentence per conflict, its classification, the resolution rule applied (or 'unresolved'), and which downstream claims carry the caveat.

## Verification
- Each detected contradiction is stated in one sentence with both sources named and a classification.
- Every conclusion depending on a conflicted fact either cites the applied resolution rule or carries the unresolved caveat — no silent side-taking.

**Known risk:** Contradiction-hunting in noisy data where trivial mismatches (rounding, timestamps) stall real work. Mitigation: the classification step routes trivia to one-line closure.

**Max intended cost:** ≤300 added output tokens; up to one live-state check per conflict where a command can settle it.

**Evidence status:** SMOKE_TESTED — executed end-to-end in live sessions and behaves as specified; no measured lift is claimed.

**Lineage:** Grounded in two evidence-backed repair patterns — evidence kills specific hypotheses rather than whole spaces, and live observed state beats plan markers — plus a documented reasoning-failure mode: building conclusions on one side of an unresolved contradiction.
