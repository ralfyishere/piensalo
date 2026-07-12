# Eval plan — final-answer-completeness (stub)

## Conditions
- **Treatment:** micro-skill text injected into the system prompt.
- **Baseline:** identical model, identical tasks, no injection.
- Same decoding settings and run count per arm; grade blind to arm.

## Grader
- **Deterministic checks** (the verification conditions are deterministic): (a) for each planted question, does the response contain an answer or an explicit unanswered-because statement; (b) count/format directives satisfied (bullet counts, yes/no-first, table presence); (c) for exact-format tasks, regex match of the mandated lines verbatim at column 0 with no markup prefix and nothing after the designated last line.
- **Rubric/LLM-judge** only for borderline "is this an answer or a deflection" cases.

## Task classes (where the failure mode naturally occurs)
1. **Multi-question messages with a buried question** — 3-5 questions, one embedded mid-paragraph ('also tell me...'), where baselines routinely drop one.
2. **Shape-directive tasks** — 'yes or no first', 'exactly 3 bullets', 'as a table', where content is easy but shape compliance is the differentiator.
3. **Machine-parsed output tasks** — instructions like 'end with a line exactly of the form STATUS: <PASS|FAIL>' graded by a script, where bolding, indentation, or trailing text breaks the parse.
