# Eval plan — hidden-constraint-scan (stub)

## Conditions
- **Treatment:** micro-skill text injected into the system prompt.
- **Baseline:** identical model, identical tasks, no injection.
- Same decoding settings and run count per arm; grade blind to arm.

## Grader
- **Deterministic checks** where the verification conditions allow: (a) each planted constraint from the task appears in the output's constraint table as a verbatim quote (string match against the task text); (b) the deliverable actually satisfies each planted hard constraint (length counts, forbidden-term absence, format compliance) — checkable by script.
- **Rubric/LLM-judge** for the judgment-typed condition: whether each satisfied-status is genuinely tied to a specific supporting location in the work, and whether hard/soft classification matches the task's wording.

## Task classes (where the failure mode naturally occurs)
1. **Long briefs with mid-paragraph constraints** — 200+ word writing or analysis tasks with 3-5 planted restrictions (word caps, source exclusions, forbidden topics) buried away from the opening lines.
2. **Coding tasks with scope exclusions** — 'do not modify file X', 'no new dependencies', 'keep the public API unchanged', where the natural solution violates one.
3. **Data/reporting tasks with format and resource limits** — 'at most 10 rows', 'exclude internal accounts', 'output CSV only', where baselines satisfy the main ask but drop one limit.
