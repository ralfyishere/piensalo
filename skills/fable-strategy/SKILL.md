---
name: fable-strategy
description: "Strategy and decision program: recover the real objective, enumerate constraints including contractual and irreversibility traps, generate genuinely distinct options, scenario-score them, attack the leader, and recommend with explicit kill conditions. Use for 'should we do X', pricing/roadmap/build-vs-buy calls, responses to competitor moves, and any decision under uncertainty with real downside. Trigger phrases: 'recommend', 'should we', 'what's the right move'."
license: MIT
---

# fable-strategy

A structured reasoning program for strategy and decision-making, distilled from curated expert reasoning traces. Work the numbered steps in order; each step's output feeds the next. Do not skip steps silently - if one does not apply, say so in one line.

## Primary workflow
1. **Recover real objective** - Per intent-clarity: decode what the requester actually needs before optimizing anything. Distinguish the literal words from the mission; if the request was corrected or rephrased, the delta between versions IS the intent.
2. **Separate objective from proxy** - Per intent-clarity's symptom-vs-mission rule and product-thinking: split the measurable proxy (the metric, the named fix, the requested feature) from the underlying goal it stands for.
3. **Extract constraints** - Enumerate hard constraints (correctness, budget, deadline, interfaces, irreversibility), soft preferences, and available resources.
4. **Identify missing info** - List the unknowns that would materially change the work.
5. **Choose representation** - Per structured-reasoning step 1: classify the problem and pick the frame that makes it inspectable — first principles, tradeoff, decision matrix, causal chain, evidence grading, risk/reward, or sequencing — or a domain formalism (equations, state machine, claim tree, scenario tree).
6. **Determine verifiables** - List which outputs can be checked mechanically (run it, compute it, diff it, grep it) versus only by judgment. Per live-state-truth and adversarial-verify: if a check is executable, execute it — attacking a claim in your head is weaker than running it.
7. **Objective hierarchy** - Build the objective hierarchy: terminal goal at the root, instrumental objectives beneath, current initiatives as leaves.
8. **Causal model** - Sketch the causal graph from actions to the terminal goal: what drives what, with sign, rough strength, and lag. Per structured-reasoning's first-principles and causal-chain frames: state the mechanism, not the correlation.
9. **Find bottleneck** - Identify the binding constraint: the single node in the causal graph where added effort most changes the terminal goal. Per leverage-first: effort on non-bottlenecks is motion, not progress — improving an unconstrained step buys nothing.
10. **Scenario branches** - Branch the future on the biggest unknowns: 3-5 scenarios with explicit trigger conditions and rough probabilities.
11. **Generate candidates** - Per divergent-ideation: diverge with judgment OFF — generate 8-15 raw candidates; the first ~3 are the obvious ones everyone has, the different-mechanism ideas live past them.
12. **Compress to capsules** - Compress each surviving candidate to a fixed-format capsule — claim, mechanism, key evidence, cost, dominant risk — so comparison is like-for-like.
13. **Expected value comparison** - Per structured-reasoning's risk/reward frame: score each strategy option across the scenario branches — upside x probability vs downside x probability, PLUS reversibility as a first-class criterion (a cheap reversible bet beats a slightly better irreversible one under uncertainty).
14. **Cheapest discriminating test** - Before committing real resources, design the cheapest real-world test that discriminates between the top options or resolves the unknown the sensitivity note says the decision hinges on.
15. **Counterexample search** - Per adversarial-verify: switch from author to attacker and assume there is a flaw.
16. **Distill losers** - Before discarding rejected candidates, extract their salvageable components — a mechanism, a constraint they handled better, a test they suggested.
17. **Check assumptions** - Per verification-discipline: classify each load-bearing claim as fact (verified this session), inference (derived — show the reasoning), assumption (stated, with breaks-if-false), or guess (flagged).
18. **Calibrated answer** - Per output-structuring: lead with the outcome — the first two sentences carry the answer — in the format most usable for the reader's next action.

## Conditional moves
- When attack changed an option's scenario scores: return to **Expected value comparison** and rework from there.
- When no option's worst case is tolerable: return to **Generate candidates** and rework from there.
- When test design revealed an unmodeled scenario: return to **Scenario branches** and rework from there.

## Output contract
A decision memo: objective hierarchy, causal model with the argued bottleneck, scenario-weighted EV table with reversibility and a sensitivity note, the recommended option, the cheapest discriminating test with its pre-registered decision rule and kill criteria, the discard log, and labeled assumptions.

## Delivery notes (small-model packets)
If delegating steps to a smaller model, follow the small-model packet rules: one bounded objective per packet, all inputs named explicitly, facts separated from instructions, uncertainty marked 'UNCERTAIN: ...' rather than invented away.

## Before answering
Check the draft against references/failure-checks.md (the failure-mode catalog) and references/verification.md (domain verification criteria). Repair procedures live in references/contracts.md.
