# boundary-case-check — skill card

## What it does
For any rule-like deliverable, mechanically enumerates the boundary inputs (empty, zero, one, duplicates, max size, negative, odd encodings, wrong type, hostile), ranks them by breakage likelihood, and actually executes the top three — quoting real output — before the artifact ships.

## Trigger
- The deliverable is executable or rule-like: a function, regex, parser, query, validator, formula, filter, allowlist/denylist, matcher, sanitizer, or threshold policy.
- The artifact will face inputs the author didn't type.
- Post-draft signal: a rule-like artifact is about to ship with no boundary input actually executed.

## Counterindications
- A named, executed test suite already exercises the edges.
- The deliverable has no input domain (pure prose or analysis).
- Throwaway one-off commands already run against their only real input.

## Negative-transfer risk
Low distraction risk. Main failure mode: false confidence from exercising three convenient edges rather than the three most breakable ones — mitigated by the ranking step and a mandatory hostile case for guards. Do not spend executions on artifacts with no input domain.

## Evidence level
EXPERIMENTALLY_TESTED
