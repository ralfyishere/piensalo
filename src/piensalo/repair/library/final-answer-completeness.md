---
name: final-answer-completeness
description: "Post-draft check that every explicit question and sub-request in the task is answered in the response, in the form the task asked for — nothing dropped, deflected, or answered in the wrong shape."
---

# final-answer-completeness

**Trigger (observable):** The task contains more than one question or directive (multiple question marks, numbered questions, embedded format instructions), and a draft response exists and is about to be sent.

**When NOT to activate:** Single-question tasks whose draft visibly answers it; mid-drafting (run at send time, not while composing); the user rescoped the questions mid-session (latest instruction wins).

## Procedure
1. Extract every interrogative and directive from the task verbatim — including question two inside a paragraph, 'also tell me...', and shape directives ('as a table', 'in 3 lines', 'yes or no first').
2. Map each to the exact location in the draft that answers it.
3. Unmapped items: answer them now, or state explicitly that they are unanswered and why — a response that silently answers 2 of 3 questions reads as evasion.
4. Check shape compliance: a 'yes or no?' answered with an essay, or '3 bullets' answered with 5 paragraphs, fails even when the content is right.
5. Exact-format rule: when the task specifies output lines "exactly" / "of the form" or says they are parsed by a script or machine, emit those lines VERBATIM at column 0 in plain text — no bold, italics, indentation, bullets, or code-fence prefix on the line itself — and place NOTHING after a line the task designates as last.
6. Check the first two sentences carry the primary answer, not preamble.

## Required output
The corrected draft, plus (for 3+ question tasks) a one-line-per-question mapping showing where each is answered.

## Verification
Every question extractable from the task maps to a specific answer location in the sent response, and each shape directive is honored or explicitly declined.

**Known risk:** Mapping tables appended to short answers, bloating a two-question reply. Mitigation: below 3 questions the check is silent — fix the draft, skip the table.

**Max intended cost:** ≤150 added output tokens beyond the answers themselves; one re-read of the task.

**Evidence status:** designed — procedure derived from a documented completion-integrity failure mode; sibling of complete-the-delivery (artifacts) — this one covers the response text; this micro-skill itself has no direct experimental test yet.
