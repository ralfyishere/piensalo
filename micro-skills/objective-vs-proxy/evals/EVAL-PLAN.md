# EVAL-PLAN — objective-vs-proxy

## Conditions
- **Treatment:** micro-skill SKILL.md body injected into the system prompt.
- **Baseline:** same model, same tasks, no injection.
- Identical decoding settings; multiple runs per task.

## Grader
- **Deterministic:** (a) output contains at least one explicit measurement-artifact hypothesis (the metric itself could be wrong); (b) an instrument probe appears in the plan ordered before any remediation step of the measured system.
- **Rubric / LLM-judge:** whether the artifact hypothesis is plausible for the scenario (not a boilerplate disclaimer) and whether the probe would actually discriminate a broken instrument from a real problem.

## Task classes (where the target failure naturally occurs)
1. **Fix-the-funnel tasks with a planted measurement bug** — e.g. an abandonment or churn metric inflated by an instrumentation gap; baseline models typically redesign the product instead of checking the event pipeline.
2. **Kill/ship decisions on a threshold** — a feature or campaign to be cut because a KPI crossed a cutoff, where the denominator drifted.
3. **Performance-regression triage** — "p95 latency doubled" scenarios where the monitoring window or aggregation changed, not the system.
