# EVAL-PLAN — second-order-effects

## Conditions
- **Treatment:** micro-skill SKILL.md body injected into the system prompt.
- **Baseline:** same model, same tasks, no injection.
- Identical decoding settings; multiple runs per task.

## Grader
- **Deterministic:** output contains a two-level effect structure (first-order → adaptation → consequence) and either a named harm with mitigation or an explicit none-found-after-search statement; a rollout-direction note is present.
- **Rubric / LLM-judge:** (a) does the analysis name a specific adapting agent and a mechanism (not generic "users may be unhappy")? (b) on tasks with a planted known second-order failure, was it found? (c) doom-chain penalty: consequences beyond two levels or without mechanisms.

## Task classes (where the target failure naturally occurs)
1. **Incentive/quota/pricing changes with a gameable metric** — plans where the measured number improves while behavior shifts to defeat the goal (key fan-out, metric gaming, load displacement).
2. **Deprecations and default-changes with silent dependents** — scenarios where scripts, integrations, or teams depend on current behavior continuing and the plan assumes none exist.
3. **Policy/process mandates** — org-level rules whose predictable workaround (shadow processes, batching before deadlines) undoes the first-order benefit.
