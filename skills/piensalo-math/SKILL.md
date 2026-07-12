---
name: piensalo-math
description: "Mathematical and quantitative reasoning workflow: formalize the claim, compute small cases honestly, conjecture, then prove or refute via independent derivation routes and boundary probes. Use for proofs, counting, probability, closed forms, numeric estimates, or any task where a pattern-extension 'proof' would be tempting. Trigger phrases: 'prove', 'compute', 'closed form', 'what are the odds', 'derive'."
license: MIT
---

# piensalo-math

The mathematical and quantitative reasoning workflow of Fable Think (domain: mathematics & quantitative analysis). Work the numbered steps in order; each step's output feeds the next. Do not skip steps silently - if one does not apply, say so in one line.

## Primary workflow
1. **Recover real objective** - Per intent-clarity: decode what the requester actually needs before optimizing anything. Distinguish the literal words from the mission; if the request was corrected or rephrased, the delta between versions IS the intent.
2. **Separate objective from proxy** - Per intent-clarity's symptom-vs-mission rule and product-thinking: split the measurable proxy (the metric, the named fix, the requested feature) from the underlying goal it stands for.
3. **Extract constraints** - Enumerate hard constraints (correctness, budget, deadline, interfaces, irreversibility), soft preferences, and available resources.
4. **Identify missing info** - List the unknowns that would materially change the work.
5. **Determine verifiables** - List which outputs can be checked mechanically (run it, compute it, diff it, grep it) versus only by judgment. Per live-state-truth and adversarial-verify: if a check is executable, execute it - attacking a claim in your head is weaker than running it.
6. **Formal restatement** - Restate the problem formally: define every symbol, its type, its units, its domain (ranges, integrality, sign), and the exact quantity to be produced.
7. **Multiple derivations** - Produce at least TWO independent derivations by genuinely different routes (e.g., algebraic vs numerical simulation; direct computation vs limiting case; combinatorial argument vs generating function).
8. **Symbolic numeric check** - Execute the checks rather than trusting mental arithmetic: run the computation numerically (python3), verify symbolic steps mechanically where possible, and compare every derivation's result in an agreement matrix.
9. **Boundary probe** - Per adversarial-verify's edge-case attack, specialized to mathematics: evaluate the result at boundaries and degenerate cases - zero, one, negative, infinity/limits, empty set, n=1, symmetric inputs, extreme ratios - and check monotonicity/sign against physical or logical expectation.
10. **Unit validation** - Run dimensional analysis end-to-end: every equation must balance in units; every numeric answer carries its unit; every conversion is explicit.
11. **Counterexample search** - Per adversarial-verify: switch from author to attacker and assume there is a flaw.
12. **Check assumptions** - Per verification-discipline: classify each load-bearing claim as fact (verified this session), inference (derived - show the reasoning), assumption (stated, with breaks-if-false), or guess (flagged).
13. **Compare by criteria** - Per structured-reasoning: score candidates against named, weighted criteria derived from the true goal - decision matrix for 3+ options x 3+ criteria, tradeoff analysis for 2-3.
14. **Refine best** - Merge the winner with salvaged components and patch every 'fixed'-status attack from the counterexample search. Per change-control: one concern per change, match the local style, know the undo path.
15. **Independent final verification** - Verify the FINAL artifact, not the plan: execute every check method bound in **Determine verifiables** against the refined solution.
16. **Calibrated answer** - Per output-structuring: lead with the outcome - the first two sentences carry the answer - in the format most usable for the reader's next action.

## Conditional moves
- When derivation routes disagree after bisection: return to **Multiple derivations** and rework from there.
- When a boundary case refutes all routes: return to **Multiple derivations** and rework from there.
- When a dimensional inconsistency traces to the problem statement: return to **Formal restatement** and rework from there.
- When a counterexample was fixed locally: return to **Refine best** and rework from there.
- When the final recomputation disagrees with the accepted result: return to **Symbolic numeric check** and rework from there.

## Output contract
A formally stated problem with symbol/units tables; >=2 independent derivations with an executed agreement matrix; boundary-case and dimensional-analysis reports; a final answer with units, stated precision, and evidence-level labels on every load-bearing claim, including which checks were executed vs reasoned.

## Delivery notes (small-model packets)
If delegating steps to a smaller model: one bounded objective per packet, all inputs named explicitly, facts separated from instructions, uncertainty marked 'UNCERTAIN: ...' rather than invented away.

## Before answering
Check the draft against references/failure-checks.md (the failure-mode catalog) and references/verification.md (domain verifier criteria). Repair procedures live in references/contracts.md.
