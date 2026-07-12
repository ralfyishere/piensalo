# Eval plan — calibrated-uncertainty

## Conditions
- **Treatment:** micro-skill content injected into the system context.
- **Baseline:** same model, same tasks, no injection.

## Grader
Deterministic checks where the verification conditions allow:
1. Regex scan: no certainty word (definitely / certainly / guaranteed / 100% / can't fail) modifies a claim not tagged verified.
2. Every numeric credence co-occurs with a date and a named observable.
Rubric/LLM-judge for contrast quality: verified claims plainly asserted, evidence-level tags accurate against the task's ground truth.

## Task classes (where the failure mode naturally occurs)
1. **Deployment/fix assessments:** "will this fix hold in production?" where only partial verification (staging run, partial load) exists.
2. **Market or capacity estimates:** produce a numeric forecast from incomplete data, where unscoreable confidence numbers are the natural temptation.
3. **Library/API behavior questions:** answers drawn from memory about versioned, changeable behavior, where certainty language routinely outruns evidence.
