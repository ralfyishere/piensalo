# Eval plan: fable-build

Stub for public evaluation of this skill. No results are recorded here; see BENCHMARK.md for the current evidence level.

## Conditions
- **skill-on:** the model runs each task with SKILL.md (and its references) loaded.
- **no-skill baseline:** the same model runs the same tasks with no skill loaded.
- Same model, same tasks, same decoding settings across both conditions; grade blind to condition.

## Grader type
Behavior-signal rubric scored by an LLM judge (with human spot-checks), plus deterministic checks where possible (regression test fails on pre-fix code; quoted test output present; diff scope matches the task). Signals are graded on substance, not on whether the output mimics the skill's vocabulary.

## Task classes
1. **Intermittent-failure diagnosis** - e.g. "This function intermittently returns wrong totals in CI but never locally (code attached). Find and fix it." Signals: captures the symptom verbatim and builds a reproduction before hypothesizing; ranks 2+ hypotheses and designs tests that discriminate between them; fix is minimal and in-scope with adjacent issues flagged not fixed; quotes actual test output and adds a regression test that fails pre-fix.
2. **Non-breaking feature addition** - e.g. "Add retry-with-backoff to our HTTP client without changing its public API. The existing suite must stay green." Signals: enumerates the public interface and verifies compatibility; runs and quotes the pre-existing suite before and after; labels any unverified assumption about server idempotency.
