# feasibility-attack — skill card

## What it does
Before a proposal gets endorsed, it extracts the proposal's binding requirements (budget, compute, rate limits, permissions, deadlines, third-party dependencies) and tests each against a known constraint using arithmetic or a citation. Hard infeasibilities (limits that cannot move) end the endorsement outright; soft hits get priced so the decision is made with the bill visible. It always closes with a verdict — feasible / feasible-at-cost / infeasible — plus either the cheapest feasibility-restoring modification or a clean kill naming the binding constraint.

## Trigger
- A novel proposal, plan, or idea is on the table for evaluation ('proposal', 'what if we', "let's build", 'roadmap item').
- The proposal names a mechanism but contains no resource or limit arithmetic.
- A draft endorses the proposal without testing any requirement against a constraint.

## Counterindications
- The proposal already argues feasibility constraint by constraint — verify that case instead of rebuilding it.
- The user explicitly deferred feasibility filtering ('just generate', 'wild ideas welcome', "don't evaluate yet").
- The proposal is already killed on other grounds.

## Negative-transfer risk
Distraction risk: medium. The failure mode is killing viable ideas on assumed constraints that were never checked ("the API probably caps at..."). The skill requires each constraint to be cited or computed; anything merely assumed is labeled as such and cannot carry a hard kill. Applied during ideation, it would also suppress divergence — hence the explicit ideation counterindication.

## Evidence level
DESIGNED — specified from documented reasoning-failure modes; not yet executed as a packaged skill.
