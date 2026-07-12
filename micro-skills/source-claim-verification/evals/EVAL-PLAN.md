# EVAL-PLAN — source-claim-verification

## Conditions
- **Treatment:** micro-skill SKILL.md body injected into the system prompt.
- **Baseline:** same model, same tasks, no injection.
- Identical decoding settings; multiple runs per task; tasks provide an openable corpus (code + logs, or documents) so primary sources are reachable.

## Grader
- **Deterministic:** (a) on tasks with a planted misleading label, the final diagnosis matches the ground-truth cause, not the label; (b) each load-bearing claim carries a source citation (file:line / document section / observed output) or an explicit unverified tag; (c) an emitting-line trace appears for error-label claims.
- **Rubric / LLM-judge:** whether at least one co-occurrence check was genuinely performed against the provided evidence (not asserted), and whether contradictions between label and facts are stated.

## Task classes (where the target failure naturally occurs)
1. **Misleading-error debugging** — a hardcoded or catch-all error message names the wrong cause ("rate limited", "timeout") while the provided logs/code show a different failure; baselines typically fix the labeled cause.
2. **Secondhand-summary research tasks** — a brief includes "the docs say X" where the supplied primary document says otherwise; graded on whether the primary source was opened and quoted.
3. **Incident post-mortems with a change event** — steady-state explanations offered for failures whose onset aligns with a deploy or config change planted in the timeline.
