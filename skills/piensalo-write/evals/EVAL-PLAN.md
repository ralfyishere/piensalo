# Eval plan: piensalo-write

Status: stub. No eval has been run against the packaged skill (see BENCHMARK.md — current status DESIGNED).

## Conditions
- **skill-on:** the model runs the task with piensalo-write loaded.
- **no-skill baseline:** the same model runs the same task with no skill loaded.
- Same model, same tasks, same tool access in both conditions; outputs graded blind to condition.

## Grader
Behavior-signal rubric scored by an LLM judge, plus deterministic checks where a signal is mechanically checkable (word count vs. limit, presence of a claim ledger, every number traceable to the supplied source sheet). No grader keys ship with the skill.

## Task classes
1. **Sourced announcement under a hard length limit** — e.g. "Draft a 150-word customer email announcing a price increase, from the attached facts sheet. Every claim must be traceable to the sheet."
   Signals: builds a claim ledger from the facts sheet before drafting; runs separate accuracy and argument passes, not one merged 'review'; compression does not drop or mutate ledger claims; no unsourced claims appear.
2. **Commitment-preserving compression** — e.g. "Rewrite this 900-word design doc intro to 300 words without losing any commitments it makes."
   Signals: enumerates the commitments (ledger) first; verifies post-compression that every commitment survives; flags any ambiguity in the original rather than silently resolving it.
