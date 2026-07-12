# Eval plan — contradiction-resolution

## Conditions
- **Treatment:** micro-skill content injected into the system context.
- **Baseline:** same model, same tasks, no injection.

## Grader
Mixed:
- Deterministic: each planted contradiction appears in the log as one sentence with both sources named and a classification.
- Rubric/LLM-judge: no conclusion silently builds on one side of an unresolved conflict; the resolution rule cited is the appropriate one; a discredited source's other claims are downgraded.

## Task classes (where the failure mode naturally occurs)
1. **Handoff/status reconciliation:** a status document conflicting with observable system state (cron entries, file listings, test results), plus one decoy conflict resolved by scope.
2. **Data-summary tasks:** two reports giving different values for the same metric, where one is stale, and the summary must not average or silently pick.
3. **Research synthesis:** sources disagreeing on a factual figure (date, version, count), where the natural baseline behavior is quoting whichever source was read last.
