# disqualifier-scan — skill card

## What it does
At ship time, it sweeps the deliverable for conditions that void the whole answer regardless of quality — missing mandatory elements, violated format rules, prohibited content or resources, broken eligibility criteria — each traced to the task or spec text. Any hit is repaired before shipping, or the verdict flips to "does not qualify"; a disclosed violation is never treated as a resolved one.

## Trigger
- The task defines a spec, rubric, acceptance criteria, or submission rules the answer can fail outright.
- Explicit pass/fail or rejection conditions are present ('disqualified', 'invalid', 'must include', 'will not be accepted').
- A required element from the spec has no counterpart in the draft.
- The draft discloses a spec violation as a caveat instead of fixing it.

## Counterindications
- No external spec or rule set exists — the scan would invent rules.
- Early drafting where the structure is still moving; sweep at ship time instead.
- The same scan already ran on this draft version.

## Negative-transfer risk
Distraction risk: low. The failure mode is sweeping invented disqualifiers the spec never stated, burning tokens on phantom rules. The skill requires every listed item to trace to the task text, which keeps the sweep anchored.

## Evidence level
EXPERIMENTALLY_TESTED — repair content lifted a weak model on procedural tasks in controlled runs; the effect is task-concentrated, and automatic router selection is a separate, unproven layer.
