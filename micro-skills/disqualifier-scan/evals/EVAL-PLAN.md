# Eval plan — disqualifier-scan (stub)

## Conditions
- **Treatment:** micro-skill text injected into the system prompt.
- **Baseline:** identical model, identical tasks, no injection.
- Same decoding settings and run count per arm; grade blind to arm.

## Grader
- **Deterministic checks** (the verification conditions allow it): (a) every planted mandatory condition from the task spec appears in the output's disqualifier list; (b) no planted violation survives into the shipped deliverable un-fixed; (c) no output ships a violation as a caveat ("note that the required X is missing") instead of a repair or a does-not-qualify verdict.
- **Rubric/LLM-judge** only for whether listed disqualifiers trace to real spec clauses versus invented rules.

## Task classes (where the failure mode naturally occurs)
1. **Submission-rule deliverables** — applications, RFP responses, or contest entries with explicit "will not be accepted unless..." clauses and one planted violation.
2. **Code delivery against acceptance criteria** — a small feature with a rubric ("must not add dependencies", "must include a test") where the natural solution breaks one criterion.
3. **Structured reports with mandatory fields** — a report template with required sections where drafts tend to drop one section and disclose it as a limitation.
