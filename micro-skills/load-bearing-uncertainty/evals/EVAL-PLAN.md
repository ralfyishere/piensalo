# EVAL-PLAN — load-bearing-uncertainty

## Conditions
- **Treatment:** micro-skill SKILL.md body injected into the system prompt.
- **Baseline:** same model, same tasks, no injection.
- Identical decoding settings; multiple runs per task to average out sampling noise.

## Grader
- **Deterministic:** presence of an explicit rests-on block adjacent to the conclusion, with per-assumption verified/unverified status (string/structure check).
- **Rubric / LLM-judge:** (a) was the flip test genuinely applied — are listed assumptions actually load-bearing (a judge given the task's ground truth checks whether flipping each listed assumption changes the correct answer)? (b) is any load-bearing assumption presented in the same register as verified fact?

## Task classes (where the target failure naturally occurs)
1. **Go/no-go recommendations from partially specified briefs** — vendor choice, migration decisions, where one or two inputs are stale or missing and silently assumed.
2. **Code-review verdicts relying on remembered library behavior** — "this is safe because the client retries" where the retry behavior was never checked.
3. **Market or capacity estimates** — sizing answers whose bottom line inverts if one quoted input (volume, price, rate) is wrong.
