---
name: causal-model-construction
description: "Before intervening in a system, write the explicit causal chain from the proposed action to the intended outcome — every arrow marked verified or assumed — and check the weakest assumed arrow first. Activate when an intervention (fix, optimization, policy change, growth action) is proposed on a system whose mechanism has not been written down."
license: MIT
---

# causal-model-construction

**Trigger (observable):** An intervention is proposed (fix, optimization, policy change, growth action) on a system whose mechanism has not been written down — the plan jumps from action to expected outcome with no stated path between.

**When NOT to activate:** The causal chain is already written and its arrows labeled this session; the action is trivially reversible and cheaper to try than to model; pure observation tasks with no intervention.

## Procedure
1. Write the chain explicitly: action → intermediate state(s) → intended outcome, as named nodes and arrows (X → Y → Z), not prose.
2. Mark each arrow verified (observed/measured this session) or assumed (from memory, analogy, or hope).
3. For each assumed arrow, name what else could produce the downstream node (confounders) and what else the action produces besides the intended effect (side paths).
4. Identify the weakest assumed arrow — the one that, if false, makes the intervention useless or harmful — and check it before committing the intervention (this is where a discriminating test belongs).
5. If the chain cannot be written, say so: an intervention with no articulable mechanism is a guess and gets labeled as one.

## Required output
The written chain with per-arrow verified/assumed labels, named confounders/side paths, and the weakest arrow plus its check.

## Verification
- The written chain exists and every arrow is labeled verified or assumed.
- The weakest assumed arrow is identified and checked (or its check is named and sequenced) before the intervention is endorsed.

**Known risk:** Modeling overhead on cheap reversible actions where trying is faster than theorizing. Mitigation: the not-when clause routes those to direct trial.

**Max intended cost:** ≤300 added output tokens; one check of the weakest arrow where feasible.

**Evidence status:** DESIGNED — specified from documented reasoning-failure modes; not yet executed as a packaged skill.

**Lineage:** Derived from a documented reasoning-failure mode — paraphrasing a system's behavior instead of stating its mechanism — with discriminating-test placement and instrument-distrust sequencing drawn from evidence-backed repair patterns.
