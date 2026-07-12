# Eval plan: fable-think

Stub for public evaluation of this skill. No results are recorded here; see BENCHMARK.md for the current evidence level.

## Conditions
- **skill-on:** the model runs each task with SKILL.md (and its references) loaded.
- **no-skill baseline:** the same model runs the same tasks with no skill loaded.
- Same model, same tasks, same decoding settings across both conditions; grade blind to condition.

## Grader type
Behavior-signal rubric scored by an LLM judge (with human spot-checks), plus deterministic checks where a signal is mechanically checkable (e.g. presence of a pre-registered threshold). Signals are graded on substance, not on whether the output mimics the skill's vocabulary.

## Task classes
1. **Metric-drop triage** - e.g. "A teammate says: 'Our signup conversion dropped 20% after the redesign - roll it back.' You have access to the analytics event definitions and the deploy log. What do you do first, and what is your recommendation process?" Signals: questions whether the metric itself changed before accepting the drop as real; names real objective vs proxy; proposes a cheap discriminating test before recommending rollback; final answer carries confidence and residual uncertainty.
2. **Decision-process design** - e.g. "Design a plan to decide whether our team should adopt a monorepo. Do not decide yet - show how you would decide." Signals: extracts constraints and contradictions or asks for the load-bearing ones; generates genuinely different options, not paraphrases; pre-registers a discriminating test with a threshold; identifies the one uncertainty that most changes the answer.
3. **Conflicting-requirements synthesis** - e.g. "Here are three conflicting requirements from three stakeholders for the same dashboard. Produce a recommendation." Signals: treats the contradiction as load-bearing rather than averaging requirements; states an interpretation line for the real objective; delivers calibrated confidence per component.
