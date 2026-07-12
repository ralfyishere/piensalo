# cheapest-discriminating-test — skill card

## What it does
When several hypotheses compete and tests cost something, designs the cheapest single test whose possible outcomes actually separate them — and pre-commits a results-to-verdict table (every outcome row, including "no clear signal") before anything runs, so results are scored against the table rather than post-hoc interpretation.

## Trigger
- Multiple live explanations named in the task: hypotheses, "could be A or B", "one of several candidates", possible causes/explanations.
- Two or more hypotheses are live and tests are not free.
- Post-draft signals: a proposed test whose every outcome is compatible with every hypothesis, or diligence gestures ("add more logging", "increase coverage", "monitor the situation", "gather more data") standing in for discriminators.

## Counterindications
- Only one live hypothesis exists — nothing to discriminate between yet; generate alternative mechanisms first.
- All tests are near-free — running everything is cheaper than designing; skip the table.
- The decision doesn't depend on which hypothesis is true.

## Negative-transfer risk
Medium distraction risk. Main failure mode: analysis paralysis — designing the perfect discriminant while a cheap sequential test would have settled it. If any single test is near-free, run it first and design after.

## Evidence level
DESIGNED
