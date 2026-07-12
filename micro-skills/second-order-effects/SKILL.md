---
name: second-order-effects
description: "Before endorsing a change, project the effects of the effects: who or what adapts to the first-order outcome, and what that adaptation breaks — especially neighbors depending on current behavior. Activate when a change with downstream dependents is proposed (policy, pricing, migration, deprecation, incentive, default-change, quota, rollout) and the analysis so far lists only direct effects."
license: MIT
---

# second-order-effects

**Trigger (observable):** A change with downstream dependents is proposed — policy, pricing, migration, deprecation, incentive, default-change, quota, or rollout — and the analysis so far lists only its direct effects.

**When NOT to activate:** Fully local changes with no dependents or adapting agents (verified, not presumed); second-order analysis for this change already exists this session; pure information requests with no change proposed.

## Procedure
1. List the first-order effects the change is designed to produce.
2. For each, ask: who or what notices and adapts? (users, teams, scripts, markets, attackers, the metric itself). Adaptation is the second-order engine.
3. For each adaptation, name what it breaks or shifts — including load moved elsewhere, gamed metrics, and neighbors that depend on the old behavior continuing.
4. Check error-cost asymmetry: if the projection is wrong, which direction of surprise is cheaper? Order the rollout to fail in the cheap direction.
5. State at least one concrete second-order harm with its mitigation — or state that a real search found none, naming where you looked.

## Required output
A two-level effect list (first-order → adaptation → second-order consequence), one named harm with mitigation (or an explicit none-found-after-search), and a cheap-direction rollout note.

## Verification
- At least one adapting agent is named and its adaptation traced to a concrete consequence with its mechanism; dependents of the current behavior were enumerated, not assumed absent (judgment check).
- The rollout or change is ordered so that a wrong projection fails in the stated cheaper direction (judgment check).

**Known risk:** Speculative doom-chains — stacking third-order fears until nothing ships. Mitigation: two levels only, and each consequence must name its mechanism.

**Max intended cost:** ≤300 added output tokens; no tool calls beyond checking who depends on current behavior.

**Evidence status:** DESIGNED — specified from documented reasoning-failure modes; not yet executed as a packaged skill.

**Lineage:** Derived from a documented reasoning-failure mode — local optimization that harms the surrounding system — with trajectory projection and cheap-direction-of-error ordering drawn from evidence-backed repair patterns.
