---
name: fable-invent
description: "Invention and mechanism-design program: extract the physics-level requirements, search prior art, generate mechanism candidates that differ in operating principle, attack feasibility with numbers, and converge on a buildable design. Use for 'design a device/mechanism/protocol that does X', novelty-sensitive proposals, and feasibility reviews of inventive claims. Trigger phrases: 'invent', 'design a mechanism', 'is this feasible', 'novel approach'."
license: MIT
---

# fable-invent

A structured reasoning program for invention and novel design, distilled from curated expert reasoning traces. Work the numbered steps in order; each step's output feeds the next. Do not skip steps silently - if one does not apply, say so in one line.

## Primary workflow
1. **Recover real objective** - Per intent-clarity: decode what the requester actually needs before optimizing anything. Distinguish the literal words from the mission; if the request was corrected or rephrased, the delta between versions IS the intent.
2. **Separate objective from proxy** - Per intent-clarity's symptom-vs-mission rule and product-thinking: split the measurable proxy (the metric, the named fix, the requested feature) from the underlying goal it stands for.
3. **Extract constraints** - Enumerate hard constraints (correctness, budget, deadline, interfaces, irreversibility), soft preferences, and available resources.
4. **Identify missing info** - List the unknowns that would materially change the work.
5. **Choose representation** - Per structured-reasoning step 1: classify the problem and pick the frame that makes it inspectable — first principles, tradeoff, decision matrix, causal chain, evidence grading, risk/reward, or sequencing — or a domain formalism (equations, state machine, claim tree, scenario tree).
6. **Functional decomposition** - Decompose the invention target into FUNCTIONS (what must be accomplished), not components (how it is done today) — 'move heat away from X' rather than 'a better fan'.
7. **Constraint inversion** - Per divergent-ideation's inversion axis: for each accepted constraint ask 'what if this were false?' — which are laws of physics, and which are habits, legacy interfaces, or unexamined defaults? Per structured-reasoning's first-principles frame: keep only constraints derivable from the actual requirements.
8. **Analogy transfer** - Per divergent-ideation's steal-across-domains axis: for each core function, ask how biology, games, logistics, markets, materials science, or other industries achieve the SAME function under different constraints, and transfer the mechanism, not the surface.
9. **Mechanism search** - Search for concrete realizable mechanisms per function: known physical effects, algorithms, materials, components, protocols.
10. **Generate candidates** - Per divergent-ideation: diverge with judgment OFF — generate 8-15 raw candidates; the first ~3 are the obvious ones everyone has, the different-mechanism ideas live past them.
11. **Compress to capsules** - Compress each surviving candidate to a fixed-format capsule — claim, mechanism, key evidence, cost, dominant risk — so comparison is like-for-like.
12. **Prior art check** - Before claiming novelty, search for prior art per candidate: patents, products, papers, open-source projects.
13. **Feasibility attack** - Per adversarial-verify and failure-mode-awareness, attack each candidate's feasibility BEFORE falling in love with it: energy/material/information budgets, scaling behavior at 10x, failure modes, manufacturing or implementation cost, the strongest domain-expert objection, and the wrongness probe ('what would have to be true for this to be impossible?').
14. **Novelty preserving synthesis** - Synthesize the final design WITHOUT regressing to the nearest familiar solution: for each element, record what it does that prior art does not, and resolve feasibility attacks by adapting the mechanism rather than swapping in the conventional component (the divergent-ideation warning: the unusual candidate dies during 'refinement', one reasonable compromise at a time).
15. **Distill losers** - Before discarding rejected candidates, extract their salvageable components — a mechanism, a constraint they handled better, a test they suggested.
16. **Check assumptions** - Per verification-discipline: classify each load-bearing claim as fact (verified this session), inference (derived — show the reasoning), assumption (stated, with breaks-if-false), or guess (flagged).
17. **Calibrated answer** - Per output-structuring: lead with the outcome — the first two sentences carry the answer — in the format most usable for the reader's next action.

## Conditional moves
- When all candidates fail physics-level attacks: return to **Mechanism search** and rework from there.
- When prior art blankets the current candidate region: return to **Generate candidates** and rework from there.
- When synthesis introduced an untested mechanism combination: return to **Feasibility attack** and rework from there.

## Output contract
A design dossier: function tree, questioned-constraints ledger, mechanism pool with maturity tags, prior-art report with auditable search coverage, per-candidate feasibility attack outcomes, a final design with an explicit novelty delta per element, the discard log, and novelty claims stated strictly at their evidence level.

## Delivery notes (small-model packets)
If delegating steps to a smaller model, follow the small-model packet rules: one bounded objective per packet, all inputs named explicitly, facts separated from instructions, uncertainty marked 'UNCERTAIN: ...' rather than invented away.

## Before answering
Check the draft against references/failure-checks.md (the failure-mode catalog) and references/verification.md (domain verification criteria). Repair procedures live in references/contracts.md.
