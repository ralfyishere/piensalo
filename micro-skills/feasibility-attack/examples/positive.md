# Positive example — evaluating a real-time personalization proposal

**Task:** "Proposal: personalize our homepage in real time by calling the recommendation API on every page view. Should we endorse this for next quarter?"

**Trigger appears:** A novel proposal about to be evaluated, with mechanism and enthusiasm present but no cost or limit arithmetic anywhere in it.

**Procedure applied:**
1. Binding requirements extracted: (a) API throughput for every page view; (b) added latency budget on the homepage; (c) engineering time before quarter end; (d) legal sign-off on using behavioral data.
2. Each tested against a known constraint:
   - (a) Site traffic averages 45 req/s at peak (analytics dashboard); the recommendation vendor's contract caps at 10 req/s — arithmetic: 4.5x over the cap.
   - (b) Vendor p95 latency is 180 ms (vendor SLA doc); homepage performance budget allows +100 ms.
   - (c) Estimated 6 engineer-weeks; 8 are available this quarter.
   - (d) Sign-off process exists and takes ~2 weeks.
3. Hard vs soft: (a) is soft — a higher-tier contract exists at a stated price; (b) is soft — a cache layer absorbs it; (c) and (d) pass.

**Required output produced:**

| Requirement | Constraint (source) | Result |
|---|---|---|
| 45 req/s to vendor API | Contract cap 10 req/s (contract) | soft-hit: tier upgrade ~$3k/mo, or cache cuts calls ~80% |
| +180 ms p95 | +100 ms perf budget (SLA + perf doc) | soft-hit: edge cache restores budget |
| 6 eng-weeks by quarter end | 8 available (capacity plan) | pass |
| Behavioral-data sign-off | 2-week process (policy) | pass |

**Verdict: feasible-at-cost** — cheapest feasibility-restoring modification: cache recommendations per segment (cuts API calls below the cap and absorbs latency), keeping the current contract tier.
