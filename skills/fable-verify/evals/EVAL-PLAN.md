# Eval plan: fable-verify

Stub for public evaluation of this skill. No results are recorded here; see BENCHMARK.md for the current evidence level.

## Conditions
- **skill-on:** the model runs each task with SKILL.md (and its references) loaded.
- **no-skill baseline:** the same model runs the same tasks with no skill loaded.
- Same model, same tasks, same decoding settings across both conditions; grade blind to condition.

## Grader type
Behavior-signal rubric scored by an LLM judge (with human spot-checks), plus deterministic checks on the review artifact itself (verdict table present with one row per criterion; disqualifier hits quoted verbatim; unchecked criteria explicitly listed). Planted-defect variants allow a fully deterministic grade: did the review catch the known defect?

## Task classes
1. **Claim verification with hidden defect** - e.g. "Here is a task description and a candidate solution that claims 'all edge cases handled and tests pass'. Verify the claim." Signals: refuses to accept unquoted test claims (runs them or marks NOT-RUNNABLE-HERE); constructs boundary/hostile probes with predictions before execution; produces a per-criterion verdict table; disqualifiers checked first and quoted verbatim on hit.
2. **Research-memo grading** - e.g. "Grade this research memo (attached) against your research verification criteria." Signals: applies domain-appropriate criteria rather than generic vibes; separates deterministic, adversarial, and evidence-level findings; states explicitly what could not be checked and why.
