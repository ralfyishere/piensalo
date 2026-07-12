# final-answer-completeness — skill card

## What it does
At send time, it extracts every question and directive from the task — including buried mid-paragraph questions and shape instructions like "in 3 bullets" or "yes or no first" — and maps each to the exact location in the draft that answers it. Unmapped items get answered or explicitly declared unanswered with a reason. It also enforces shape compliance and a strict verbatim rule for machine-parsed output lines: exact text, column 0, plain formatting, nothing after a designated last line.

## Trigger
- The task contains two or more questions (multiple question marks, numbered question lists).
- The task dictates the answer's shape ('in 3 bullets', 'as a table', 'yes or no', 'one paragraph', 'JSON only').
- The task mandates verbatim, machine-parsed output lines ('lines exactly of the form...', 'parsed by a script').
- A draft exists and an explicit question in the task has no answer location in it.

## Counterindications
- Single-question tasks whose draft visibly answers the question — mapping is overhead.
- Mid-drafting: run at send time, not while composing.
- The user rescoped or withdrew questions mid-session — the latest instruction supersedes the original list.

## Negative-transfer risk
Distraction risk: low. The failure mode is bureaucratic bloat — mapping tables appended to short replies. The skill is silent below 3 questions: fix the draft, skip the table.

## Evidence level
EXPERIMENTALLY_TESTED — repair content lifted a weak model on procedural tasks in controlled runs; the effect is task-concentrated, and automatic router selection is a separate, unproven layer.
