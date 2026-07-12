# Eval plan — feasibility-attack (stub)

## Conditions
- **Treatment:** micro-skill text injected into the system prompt.
- **Baseline:** identical model, identical tasks, no injection.
- Same decoding settings and run count per arm; grade blind to arm.

## Grader
- **Deterministic checks** where the verification conditions allow: (a) output ends in exactly one of feasible / feasible-at-cost / infeasible; (b) every hard kill names a constraint with arithmetic or a source; (c) when the task materials contain a planted hard infeasibility (e.g. a stated rate cap the proposal exceeds), the verdict is infeasible or the modification removes the violation.
- **Rubric/LLM-judge** for whether soft hits are correctly priced and whether "assumed" constraints were improperly used to kill.

## Task classes (where the failure mode naturally occurs)
1. **Product/engineering proposals with a planted limit violation** — the materials include a rate cap, quota, or budget the proposal arithmetic breaks; baselines tend to endorse on mechanism alone.
2. **Project plans with deadline/headcount math** — a plan whose stated staffing cannot cover the stated scope by the stated date.
3. **Partnership or integration ideas with unagreed third parties** — proposals that silently depend on a party who hasn't agreed, where the dependency should surface as a requirement.
