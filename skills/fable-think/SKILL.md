---
name: fable-think
description: "Domain-general deep problem-solving loop distilled from curated expert reasoning traces: objective recovery, constraint and contradiction extraction, distinct mechanisms, cheapest discriminating test, adversarial verification, calibrated synthesis. Use when a task is non-trivial and a shallow first answer is risky - hard analysis, debugging, design, or any question where being confidently wrong is expensive. Trigger phrases: 'think this through', 'get this right', 'hard problem', or any multi-constraint ask."
license: MIT
---

# fable-think

The core reasoning loop of Fable Think (domain: any). Work the numbered steps in order; each step's output feeds the next. Do not skip steps silently - if one does not apply, say so in one line.

## Primary workflow
1. **Recover real objective** - State what the requester actually needs (not the stated ask); one interpretation line.
2. **Separate objective from proxy** - Name the attractive proxy the stated ask suggests; show it differs from the real objective or confirm they match.
3. **Extract constraints and contradictions** - List explicit+implicit constraints AND any contradictions in the given evidence; a contradiction is load-bearing until resolved.
4. **Load-bearing uncertainty** - Identify the ONE uncertainty that most changes the answer if wrong; say how it could be reduced cheaply.
5. **Representation and verification** - Choose the working representation (table/causal model/formal statement) and what can be DETERMINISTICALLY verified vs judged.
6. **Adversarial verify** - Attack the winner: counterexamples, boundary cases, arithmetic re-check with tools where cheap; use the criteria in references/verification.md.
7. **Calibrated answer** - Deliver the final result with confidence per component and the uncertainty that remains; never invent certainty.

## Conditional moves
- When the solution space is non-trivial, also: **Distinct mechanisms** - Generate 2-4 GENUINELY different mechanisms/answers (different algorithms, not paraphrases).
- When >1 candidate survives or a kill-gate is required, also: **Cheapest discriminating test** - Design the cheapest test whose outcomes DIFFER across surviving candidates; pre-register its threshold. OUTPUT KEYS VERBATIM: test, threshold, kills_which.
- When >1 candidate survives, also: **Compare and synthesize** - Compare candidates on decomposed criteria incl. constraint fit; keep the winner; harvest unique discoveries from losers (distill, do not replay).
- When falsifiable claims are present, also activate: counterexample search.
- When (and only when) it changes the answer, also activate: tool use.
- When the solution space is non-trivial, also activate: multi-candidate generation.
- When >1 candidate survives, also activate: loser distillation.
- When deciding under uncertainty, also activate: scenario analysis.
- For invention/novelty tasks, also activate: prior-art search.
- For math/quantitative tasks, also activate: independent derivation.

## Output contract
Calibrated final answer + residual uncertainty.

## Delivery notes (small-model packets)
If delegating steps to a smaller model: one bounded objective per packet, all inputs named explicitly, facts separated from instructions, uncertainty marked 'UNCERTAIN: ...' rather than invented away.

## Before answering
Check the draft against references/failure-checks.md (the failure-mode catalog) and references/verification.md (domain verifier criteria). Repair procedures live in references/contracts.md.
