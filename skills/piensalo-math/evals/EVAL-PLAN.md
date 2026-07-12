# Eval plan: piensalo-math

Stub for public evaluation of this skill. No results are recorded here; see BENCHMARK.md for the current evidence level.

## Conditions
- **skill-on:** the model runs each task with SKILL.md (and its references) loaded.
- **no-skill baseline:** the same model runs the same tasks with no skill loaded.
- Same model, same tasks, same decoding settings across both conditions; grade blind to condition.

## Grader type
Deterministic checks where the answer is a known quantity (final value correct; small cases correct), plus a behavior-signal rubric scored by an LLM judge (with human spot-checks) for derivation quality. Signals are graded on substance - a genuinely different second route, not a paraphrase.

## Task classes
1. **Conjecture-and-prove** - e.g. "Let T(n) be the number of ways to tile a 2xn strip with dominoes. Compute T(1..6), conjecture a closed form or recurrence, and prove or refute it." Signals: computes small cases honestly (1,2,3,5,8,13); refuses pattern-extension as proof and gives an induction or bijection argument; labels proved vs computed claims; checks a boundary case (n=0 or n=1).
2. **Probability with independent verification** - e.g. "A test is 99% accurate and the condition affects 1 in 1000 people. Someone tests positive - how worried should they be? Show your reasoning and verify it a second independent way." Signals: applies Bayes correctly (~9% posterior for symmetric 99%); verifies via a second route (natural frequencies / population table); states assumptions about 'accurate' explicitly as assumptions.
