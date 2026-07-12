# Skill card: fable-research

## What it does
Assembles multi-source answers with per-claim verification, contradiction handling, and honest coverage limits. Output is a cited synthesis: claim-level evidence table, contradiction map with reconciliations, explicit coverage gaps, and a conclusion whose confidence never exceeds its graded evidence.

## Trigger
'research', 'reconcile these figures', 'what does the evidence say' — any answer that must be assembled from multiple sources, including reconciling conflicting numbers or reports and literature/market questions.

## Counterindications
- Single-fact lookups or questions answerable from one provided document — the full pipeline adds latency without adding accuracy.
- Without retrieval tools, quality is bounded by source access: the skill degrades to auditing the sources provided, and should say so.
- Not for deriving answers from first principles (use fable-strategy or fable-invent for decision/design questions).

## Negative-transfer risk
On trivial or single-source questions, the contradiction-map and evidence-table machinery produces ceremony instead of insight — a longer answer, later, with no extra correctness. Fixed-format capsules imposed on simple asks cut throughput without improving outcomes.

## Evidence level
DESIGNED — see BENCHMARK.md. The micro-skills this domain skill composes carry their own evidence levels (see the micro-skills layer); the composed domain skill itself has not been executed as a packaged unit.
