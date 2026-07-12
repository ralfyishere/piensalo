# Eval plan: fable-research

Status: stub. No eval has been run against the packaged skill (see BENCHMARK.md — current status DESIGNED).

## Conditions
- **skill-on:** the model runs the task with fable-research loaded.
- **no-skill baseline:** the same model runs the same task with no skill loaded.
- Same model, same tasks, same tool access in both conditions; outputs graded blind to condition.

## Grader
Behavior-signal rubric scored by an LLM judge, plus deterministic checks where a signal is mechanically checkable (e.g. "an evidence table with as-of dates is present", "coverage limits section exists"). No grader keys ship with the skill.

## Task classes
1. **Conflicting-figures reconciliation** — e.g. "Two attached reports give different figures for the same product's market share (11% and 19%). Reconcile them and state the number the exec team should use."
   Signals: investigates definitional differences (denominator, window, segment) before declaring either wrong; grades each source and verifies load-bearing claims at claim level; verdict includes explicit coverage limits.
2. **Bounded evidence synthesis** — e.g. "What do we actually know about whether four-day work weeks change productivity? Use only the three attached studies."
   Signals: builds a contradiction map across the studies; distinguishes what the studies measured from what the question asks; does not average incompatible effect sizes; states residual uncertainty.
