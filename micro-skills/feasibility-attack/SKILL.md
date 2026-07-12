---
name: feasibility-attack
description: "Attack a proposal's feasibility before endorsing it: extract its binding requirements — resources, limits, permissions, dependencies, deadlines — and test each against known constraints. One hard infeasibility ends the endorsement."
license: MIT
---

# feasibility-attack

**Trigger (observable):** A novel proposal, plan, or idea is being evaluated or about to be endorsed, and it carries no cost, resource, or constraint check — enthusiasm and mechanism are present, arithmetic is not.

**When NOT to activate:** The proposal already includes a constraint-by-constraint feasibility case (then verify that case instead of rebuilding it); pure ideation where feasibility filtering was explicitly deferred; proposals already killed on other grounds.

## Procedure
1. Extract the proposal's binding requirements: budget, compute, headcount-time, API/rate limits, permissions, physical constraints, hard deadlines, and dependencies on parties who haven't agreed.
2. For each requirement, test it against a known constraint with arithmetic or a citation — 'needs 40 req/s; the vendor caps at 10/s' — not vibes.
3. Distinguish hard infeasibility (violates a limit that cannot move) from soft (expensive but purchasable). One hard hit ends the endorsement.
4. For soft hits, state the price of relief (time, money, negotiation) so the proposer decides with the bill visible.
5. Close constructively: the cheapest modification that restores feasibility, or a clean kill with the binding constraint named — never a defect list with no verdict.

## Required output
A requirement-by-constraint table with pass / soft-hit (priced) / hard-hit (killing) results, ending in an explicit feasible / feasible-at-cost / infeasible verdict.

## Verification
- Every hard kill cites a named constraint with arithmetic or a source; assumed constraints cannot carry hard kills.
- The output ends in an explicit feasible / feasible-at-cost / infeasible verdict that follows mechanically from the table.
- Net effect: every binding requirement is tested against a named constraint, and the verdict follows from the hits.

**Known risk:** Killing ideas on assumed constraints that were never checked ('the API probably caps at...'). Mitigation: each constraint must be cited or computed, or it's labeled assumed and can't carry a hard kill.

**Max intended cost:** ≤350 added output tokens; a few lookups to confirm claimed limits.

**Evidence status:** DESIGNED — specified from documented reasoning-failure modes; not yet executed as a packaged skill.

**Lineage:** Derived from a documented reasoning-failure mode — endorsing novel ideas on mechanism and enthusiasm without feasibility arithmetic — combined with two evidence-backed principles: close with an explicit verdict rather than an unranked defect list, and recognize when a constraint space is exhausted rather than continuing to search it.
