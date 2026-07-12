# objective-vs-proxy — skill card

## What it does
Before any decision is made against a metric, KPI, or threshold, it interrogates the instrument: for each load-bearing number it writes one concrete hypothesis under which the number itself is wrong (censoring, denominator drift, benign-case miscounting, stale input, attribution bug), designs the cheapest probe of the measurement, and sequences that probe before any fix to the measured system.

## Trigger
- A named metric (conversion, churn, abandonment, CAC, LTV, error rate, win rate...) is presented as the ground truth for a decision.
- A quoted percentage is the stated basis for action.
- A threshold comparison ("below target", "exceeds the cutoff") drives a kill/ship/prioritize call.
- A draft proposes fixes to the measured system with no check of the measurement itself.

## Counterindications
- The number was independently recomputed from raw data this session.
- The metric is descriptive only — no action depends on it (pure reporting).

## Negative-transfer risk
Instrument paranoia: auditing every ruler on decisions too small to warrant it stalls obvious, cheap fixes behind measurement audits nobody needed. The flip test (would the action change if the metric were 30% off?) gates the depth; overall distraction risk is low, with a ~300-token ceiling and at most one probe designed.

## Evidence level
DESIGNED — specified from documented reasoning-failure modes; not yet executed as a packaged skill.
