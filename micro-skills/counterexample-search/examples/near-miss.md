# Near-miss example — claim already scoped to observations

**Task:** Summarize load-test results for a report.

**Draft:**
> In the 50 runs we executed, p99 latency never exceeded 120 ms.

This looks like a "never" claim, but it is already scoped to the 50 observed runs — a counterindication (claim scoped to observations). Nothing universal is asserted, so the skill must NOT fire.

**Why firing would hurt:** Hunting for a hypothetical 51st-run counterexample would burn tokens attacking a claim the author never made, and could pressure the text into hedging an accurate empirical statement.
