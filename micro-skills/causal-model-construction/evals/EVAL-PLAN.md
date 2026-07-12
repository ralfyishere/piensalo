# Eval plan — causal-model-construction

## Conditions
- **Treatment:** micro-skill content injected into the system context.
- **Baseline:** same model, same tasks, no injection.

## Grader
Mixed:
- Deterministic: a written chain exists and every arrow carries a verified/assumed label.
- Rubric/LLM-judge: the weakest assumed arrow is correctly identified for the scenario's planted flaw, its check is named and sequenced before endorsement, and confounders/side paths are named rather than generic.

## Task classes (where the failure mode naturally occurs)
1. **Growth/retention proposals:** interventions (emails, discounts, notifications) where the planted ground truth is that the target metric is driven by a different mechanism.
2. **Performance fixes:** "add a cache / add an index" proposals where the actual bottleneck lies elsewhere in the chain.
3. **Policy/process changes:** "add a review step to reduce defects" scenarios where a confounder (e.g., deadline pressure) produces the defects.
