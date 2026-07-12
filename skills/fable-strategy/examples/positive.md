# Positive example: the skill fires on a build-vs-buy decision

**Task:** "Should we build our own task queue or adopt a managed one?"

A real decision under uncertainty with irreversibility on one branch: exactly the trigger for fable-strategy. The skill fires and works the pipeline:

1. Real objective: reliable background processing within 2 engineers' maintenance budget - not "have our own queue".
2. Constraints incl. traps: data-residency clause in two enterprise contracts (jobs carry customer payloads); managed-vendor migration is reversible, a bespoke queue is organizationally sticky (irreversibility asymmetry noted).
3. Distinct options: (a) managed vendor, (b) build on existing Postgres (SKIP LOCKED), (c) full bespoke broker. (c) differs from (b) in principle, not just size.
4. Scenario scoring across load x team-size futures: (b) wins low/medium scenarios; (a) wins high-load; (c) wins none it isn't dominated in.
5. Attack the leader (b): worst case = queue table bloat at 50x load; probe with synthetic insert test -> degrades at ~30x current load, above the 3-year forecast.
6. Recommendation: (b) now, with a pre-registered kill condition - if sustained load exceeds 10x current OR queue-related pages exceed 2/month for a quarter, migrate to (a). Residual uncertainty: enterprise residency review of vendor (a) not yet done; it only matters if the kill condition fires.

Why this is the skill working: the leader was attacked with a real probe, not rhetoric; reversibility drove the ranking; and the recommendation ships with the condition under which it flips.
