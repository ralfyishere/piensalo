# Positive example: the skill firing on "add caching"

**Task:** "Our API is slow; add caching." A multi-constraint ask with a tempting proxy - exactly the profile fable-think exists for.

1. Real objective: cut p95 latency for repeated reads, not "add a cache" (the proxy).
2. Proxy check: cache hit-rate is the attractive proxy; it diverges - a 95% hit rate on cold-path-irrelevant keys leaves p95 unchanged.
3. Constraints/contradictions: 512MB budget; writes must never serve stale >5s; the given trace shows 80% of reads hit 5% of keys BUT the slow requests are the other 20% - a contradiction that reframes the task.
4. Load-bearing uncertainty: are slow reads cacheable at all (unique keys?). Cheapest reduction: count distinct keys among p95-worst requests in the existing log.
5. Representation: table of request classes x (share, cacheability, latency source).
6. Distinct mechanisms: (a) LRU on hot keys, (b) precompute the 20% analytic queries, (c) fix the N+1 query causing slowness without any cache.
7. Discriminating test: test = replay top-100 slowest requests against a dry-run cache; threshold = >30% would have hit; kills_which = (a) if below threshold.
8. Result of test on the log: 4% would have hit -> (a) killed. (c) wins: the slowness is an N+1 join, cache would have masked nothing.
9. Adversarial check: boundary - does the join fix hold at 10x data? Ran EXPLAIN with synthetic rows: yes, index scan stays flat.
10. Calibrated answer: fix the N+1 (verified on replay); caching deferred - confidence high on diagnosis, medium on 10x projection (synthetic data). Residual uncertainty: production write-skew not replayed.

Why this is a hit: the literal ask ("add caching") would have shipped a cache that changed nothing; the loop surfaced the contradiction, killed the proxy solution with a cheap pre-registered test, and delivered a calibrated verdict.
