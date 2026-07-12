# EVAL-PLAN — recover-real-objective

## Conditions
- **Treatment:** micro-skill SKILL.md body injected into the system prompt.
- **Baseline:** same model, same tasks, no injection.
- Identical decoding settings; multiple runs per task.

## Grader
- **Deterministic:** output contains a one-line "Interpreting this as:" (or equivalent) objective statement that is lexically distinct from a paraphrase of the request.
- **Rubric / LLM-judge:** (a) is the stated objective the plausible one given planted context, not an invention? (b) is the literal action explicitly checked against it, with divergence named or ruled out? (c) over-interpretation penalty: did the answer silently substitute its interpretation for the literal ask?

## Task classes (where the target failure naturally occurs)
1. **Knob-turn requests hiding a wrong-layer fix** — timeout/retry/buffer increases where planted context (logs, latency figures) shows the literal change cannot achieve the evident goal.
2. **Vague-referent edit requests** — "clean this up" / "make it better" on a document or function, where quality is judged by whether the answer states an interpretation the user can veto.
3. **Oddly specific micro-instructions** — "just remove that check" style requests where the check guards a real invariant and blind literal execution introduces a defect.
