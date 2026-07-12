# Eval plan — counterexample-search (stub)

## Conditions
- **Treatment:** micro-skill text injected into the system prompt.
- **Baseline:** identical model, identical tasks, no injection.
- Same decoding settings and run count per arm; grade blind to arm.

## Grader
- **Deterministic checks** where possible: (a) does each universal claim in the output carry a named counterexample candidate that was executed/traced; (b) were claims broken by a planted counterexample weakened or withdrawn in the final text.
- **Rubric/LLM-judge** for whether the chosen candidate is genuinely the domain edge (empty/zero/max/malformed) rather than a token gesture.

## Task classes (where the failure mode naturally occurs)
1. **Code review with claimed invariants** — functions whose docstring asserts "always/never" behavior and which contain a plantable edge-case bug (empty input, duplicate keys, boundary value).
2. **"Does this property hold in general?" questions** — small math/logic or data-structure claims where a specific counterexample exists.
3. **Policy/spec assertions** — statements like "no user can reach state X" over a small state machine with one reachable violating path.
