# Positive example — skill fires and repairs the output

**Task:** "Increase the API client timeout from 10s to 60s."

**Trigger appears:** The request names a knob (timeout value), not an outcome. No goal or acceptance criterion is stated.

**Procedure applied:**
1. Literal request: raise client timeout 10s → 60s.
2. Plausible objective: stop the nightly export job from failing with timeout errors.
3. Check: the export endpoint's p99 latency in the logs is 8 minutes on large accounts — a 60s timeout still fails them; the divergence is a symptom-fix at the wrong layer (the export should be async or paginated).
4. Divergence is not cheap (the job would keep failing for the biggest customers), so the interpretation and better-aimed option are stated before acting.

**Required output produced:**

> Interpreting this as: **make the nightly export stop failing on large accounts.**
> Divergence: raising the timeout to 60s won't achieve that — p99 for large exports is ~8 minutes, so they still time out. I've made the requested change (10s → 60s), and flagged the aimed fix: switch the export call to the async endpoint with polling. Say the word and I'll do that instead.
