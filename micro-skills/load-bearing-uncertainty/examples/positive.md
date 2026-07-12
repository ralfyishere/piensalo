# Positive example — skill fires and repairs the output

**Task:** "Should we migrate the analytics service from Postgres to ClickHouse? Give me a recommendation."

**Trigger appears:** A go/no-go recommendation is being produced, and two of its inputs are unverified: the quoted 40 GB/day ingest volume comes from a six-month-old capacity doc, and the claim that "our ORM supports ClickHouse" is from memory, not checked against the current codebase.

**Procedure applied:**
1. Assumptions listed: (a) ingest volume ≈ 40 GB/day, (b) ORM has a maintained ClickHouse driver, (c) the team prefers SQL-compatible tooling, (d) queries are aggregation-heavy.
2. Flip test: (a) flips the answer — at 4 GB/day Postgres with partitioning is simpler and wins; (b) flips it — no driver means a rewrite of the data layer; (c) and (d) are decorative — the recommendation survives either way.
3. Cheapest checks: (a) one query against the ingest log table for the last 7 days; (b) one lookup of the ORM's current adapter list. The ORM check is cheap and was run: a community driver exists but is marked beta.

**Required output produced:**

> **Recommendation: migrate, behind a 2-week dual-write trial.**
>
> Rests on:
> - Ingest volume is still ~40 GB/day — **unverified** (source doc is six months old). Cheapest check: 7-day sum from the ingest log. If actual volume is under ~5 GB/day, the answer inverts: stay on Postgres.
> - ORM ClickHouse support — **verified this session**: beta community driver exists; budget for raw-SQL fallback on two hot paths.
