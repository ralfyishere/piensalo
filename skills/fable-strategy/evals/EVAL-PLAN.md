# Eval plan: fable-strategy

Status: stub. No eval has been run against the packaged skill (see BENCHMARK.md — current status DESIGNED).

## Conditions
- **skill-on:** the model runs the task with fable-strategy loaded.
- **no-skill baseline:** the same model runs the same task with no skill loaded.
- Same model, same tasks, same tool access in both conditions; outputs graded blind to condition.

## Grader
Behavior-signal rubric scored by an LLM judge, plus deterministic checks where a signal is mechanically checkable (e.g. "3+ options present", "kill conditions section exists"). No grader keys ship with the skill.

## Task classes
1. **Competitive response** — e.g. "Our largest competitor just cut prices 30%. Attached: our contract templates, margin model, and churn data. Recommend a response."
   Signals: reads the contracts for clauses that constrain the response before recommending; generates 3+ genuinely distinct options and scenario-scores them; attacks the leading option's worst case; recommendation includes pre-registered kill conditions.
2. **Sunset / commitment decision** — e.g. "Should we sunset our legacy API this year? Decide, given the attached usage and revenue data."
   Signals: separates the real objective from the stated ask; quantifies irreversibility and worst-case exposure per option; final recommendation is calibrated, with the load-bearing uncertainty named.
