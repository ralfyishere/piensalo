# hidden-constraint-scan — skill card

## What it does
It re-reads the full task text and pulls every constraint into an explicit table — restrictive clauses, format directives, scope exclusions, resource limits, ordering rules — quoted verbatim, classified hard or soft, and checked against the current plan or draft. Violations are fixed (hard) or explicitly traded off (soft) before delivery, and the table stays visible so later steps in a long task keep re-checking against it.

## Trigger
- The task text contains restrictive clauses in a genuine constraint context ('must', 'cannot', 'never', 'only', 'except', 'at most', 'not allowed').
- The task text is long enough (over ~150 words) that mid-prompt constraints drop out of attention.
- An explicit output-format or length directive is present ('in 200 words', 'JSON only', 'format: ...').
- A draft violates a constraint stated verbatim in the task text.

## Counterindications
- Short requests (under ~50 words) with no restrictive language — the scan adds pure overhead.
- Constraints already extracted into a checklist this session and being checked.
- Brainstorming where no deliverable is being checked.

## Negative-transfer risk
Distraction risk: low. The failure mode is inflating preferences into hard constraints and over-constraining the solution — treating "ideally under a page" like "must not exceed a page". The mandatory hard/soft classification step forces that distinction before any constraint can block delivery.

## Evidence level
EXPERIMENTALLY_TESTED — repair content lifted a weak model on procedural tasks in controlled runs; the effect is task-concentrated, and automatic router selection is a separate, unproven layer.
