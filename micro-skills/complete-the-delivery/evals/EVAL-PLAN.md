# Eval plan — complete-the-delivery

## Conditions
- **Treatment:** micro-skill content injected into the system context.
- **Baseline:** same model, same tasks, no injection.

## Grader
Deterministic checks (both verification conditions allow it):
1. Every deliverable extractable from the request appears in the output's checklist with a mapped location or an explicit undone-with-reason status.
2. No "done"/"complete" claim spans an item marked unverified or undone.
3. Count directives satisfied exactly (e.g., "3 examples" yields 3).

## Task classes (where the failure mode naturally occurs)
1. **Multi-part build requests:** 4–6 part specs with one part embedded mid-sentence, where baselines typically deliver the prominent parts and round up to "done".
2. **Count-directive tasks:** requests with exact counts ("5 test cases, 2 variants each") where partial delivery is the natural failure.
3. **Long-task drift:** a multi-part request followed by enough intermediate work that the tail parts fall out of working memory before delivery.
