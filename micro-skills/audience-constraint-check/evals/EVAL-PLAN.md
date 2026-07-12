# Eval plan — audience-constraint-check

## Conditions
- **Treatment:** micro-skill content injected into the system context.
- **Baseline:** same model, same tasks, no injection.

## Grader
Rubric / LLM-judge (both verification conditions are judgment calls):
1. Is the named consumer's next action answerable from the deliverable's first two sentences?
2. Does any claim exceed what the consumer could safely assert downstream (unverified items unmarked)?
Plus a deterministic check that a consumer statement and constraint list appear in the output.

## Task classes (where the failure mode naturally occurs)
1. **Incident write-ups for customers:** draft an outage or defect notice from internal notes containing unverified fixes and internal jargon.
2. **Executive summaries:** condense a technical investigation into a memo for a non-technical decision-maker with a hard length ceiling.
3. **Handoff documents:** write instructions for an on-call engineer who must act at 3 a.m. without asking questions.
