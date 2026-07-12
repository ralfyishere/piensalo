# Eval plan — distinct-mechanism-generation (stub)

## Conditions
- **Treatment:** micro-skill text injected into the system prompt.
- **Baseline:** identical model, identical tasks, no injection.
- Same decoding settings and run count per arm; grade blind to arm.

## Grader
- **Rubric/LLM-judge** (the verification conditions are judgment-typed): (a) pairwise distinctness — do any two candidates share a causal path; (b) presence of at least one candidate with no lexical overlap with the task's wording; (c) whether the true planted cause appears in the list at all (guards against exotic padding crowding out the mundane).
- A cheap **deterministic proxy** can pre-screen: n-gram overlap between each candidate and the task text flags paraphrase-heavy lists for judge review.

## Task classes (where the failure mode naturally occurs)
1. **Incident root-cause brainstorms** — an outage or regression description whose true cause is off-vocabulary (broken metric, common cause, adjacent existing fix).
2. **Business-metric diagnosis** — a KPI drop where the input wording anchors heavily on one surface ("checkout", "sign-up") and paraphrase lists score zero.
3. **Open ideation with a hidden duplicate trap** — "give me 6 approaches" tasks where naive lists contain 6 wordings of 2 mechanisms.
