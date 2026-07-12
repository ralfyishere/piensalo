# EVAL-PLAN — rederive-the-numbers

## Conditions
- **Treatment:** micro-skill SKILL.md body injected into the system prompt.
- **Baseline:** same model, same tasks, no injection.
- Identical decoding settings; multiple runs per task.

## Grader
- **Deterministic:** (a) each load-bearing number in the answer carries a quoted/derived tag; (b) derived numbers show an inputs → result recomputation; (c) on tasks with a planted arithmetic error, the final answer contains the correct value (exact-match against ground truth).
- **Rubric / LLM-judge:** whether mismatches were investigated to a named cause (wrong input, wrong formula, denominator drift) rather than silently replaced or averaged.

## Task classes (where the target failure naturally occurs)
1. **Summarization with planted derived-number errors** — reports whose stated percentage or delta contradicts its own raw inputs (classic denominator drift); baselines tend to repeat the stated figure.
2. **Cost/estimate roll-ups** — multi-line budget or capacity estimates where one intermediate is stale, so the total is wrong by a checkable amount.
3. **Unit-conversion chains** — throughput, storage, or rate conversions across units where a silent unit mismatch flips the conclusion.
