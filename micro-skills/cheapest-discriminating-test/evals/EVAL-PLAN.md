# Eval plan — cheapest-discriminating-test

## Conditions
- **Treatment:** micro-skill content injected into the system context.
- **Baseline:** same model, same tasks, no injection.

## Grader
Deterministic checks (both verification conditions allow it):
1. A results-to-verdict table appears in the transcript before any test execution, and it contains a no-signal row.
2. At least one row of the table kills at least one hypothesis.
A rubric judge additionally scores test economy: whether a cheaper test with equal discrimination existed in the scenario.

## Task classes (where the failure mode naturally occurs)
1. **Intermittent-bug triage:** 2–3 planted candidate causes where the natural baseline move is "add logging and wait".
2. **Metric-drop diagnosis:** a KPI fell and several channel/segment explanations fit the aggregate; only a slice-level probe separates them.
3. **Design/option selection:** two architecture options whose difference only matters under a specific load or failure condition that a targeted probe can simulate.
