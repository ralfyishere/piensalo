# complete-the-delivery — skill card

## What it does
Extracts every deliverable a multi-part request asked for into a checklist, maps each item to the exact place in the produced work that satisfies it, and partitions the completion claim into delivered-and-verified / delivered-unverified / not delivered — so nothing is silently dropped, stubbed, or rounded up to done.

## Trigger
- The request contains an enumerated or bulleted list of parts.
- Multiple deliverables chained in prose: "and also", "as well as", "both", "all of", "each of", "plus".
- The request specifies exact counts ("3 examples", "5 test cases", "2 variants").
- Post-draft signals: a part of the request has no corresponding element in the draft, or the draft defers requested work ("the rest as an exercise", "TODO", "follow-up") without the user asking.

## Counterindications
- The request has exactly one deliverable and no format/count directives.
- The user explicitly dropped parts mid-task — the latest instruction supersedes.
- Exploratory conversation where nothing is being delivered.

## Negative-transfer risk
Low distraction risk. Main failure mode: checklist theater on trivial two-part requests — mitigated by the rule that below 3 parts the mapping is one line, not a table. Do not resurrect parts the user explicitly rescoped away.

## Evidence level
EXPERIMENTALLY_TESTED
