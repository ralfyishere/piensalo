# Positive example — skill fires and repairs the output

**Task:** "Review this plan: we'll add a 100-requests/minute rate limit to the public API to cut infrastructure costs. Direct effect: heavy callers throttled, ~30% load reduction."

**Trigger appears:** A quota change with downstream dependents is proposed, and the plan's analysis lists only the first-order effect (load reduction).

**Procedure applied:**
1. First-order effect: heavy callers slow down; load drops ~30%.
2. Who adapts? (a) High-volume integrators; (b) the retry logic inside popular client SDKs; (c) the cost metric itself.
3. What the adaptations break: (a) integrators fan out across multiple API keys — load returns but is now unattributable; (b) SDKs with naive retry-on-429 hammer the endpoint harder, converting a throttle into a retry storm; (c) the cost dashboard "improves" while total requests (including rejected ones) rise.
4. Error-cost asymmetry: over-limiting breaks paying integrations (expensive, trust-damaging); under-limiting merely delays savings (cheap). Roll out with a generous limit and tighten, not the reverse.

**Required output produced:**

> First-order: throttle heavy callers → ~30% load cut.
> → Adaptation: key fan-out by integrators → load returns, attribution lost. Mitigation: per-account (not per-key) limits.
> → Adaptation: naive SDK retries on 429 → retry storms. Mitigation: Retry-After headers + jitter guidance in the changelog before enforcement.
> Cheap-direction note: start at 300 rpm and ratchet down monthly; failing loose is cheap, failing tight breaks paying customers.
