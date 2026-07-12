---
name: piensalo-verify
description: "Independent verification of a candidate answer against domain verifier criteria: deterministic checks first, adversarial probes, evidence-level grading, disqualifier sweep, per-criterion verdict table. Use when asked to check, grade, review, or attack a finished answer or artifact - yours or another agent's - before it is trusted or shipped. Trigger phrases: 'verify this', 'is this answer right', 'review before we ship', 'grade this output'."
license: MIT
---

# piensalo-verify

The verification workflow of Piénsalo. Given a task and a candidate answer, grade the candidate - do not fix it. Verification is adversarial: your job is to find where it fails.

## Primary workflow
1. **Pick the domain verifier** - software, mathematics, research, strategy, invention, writing, or generic if none fits. Criteria for every domain are in references/verification.md.
2. **Disqualifier sweep first** - check the domain's disqualifiers; any hit ends the review with verdict FAIL and the quoted evidence.
3. **Run deterministic criteria** - execute or mechanically check everything checkable (run tests, recompute numbers, diff scope). Quote actual output; a prediction is not a result.
4. **Run adversarial criteria** - construct probes the author visibly did not try (empty/boundary/hostile inputs, counterexamples, contradicting sources); predict the outcome before executing each probe.
5. **Grade evidence criteria** - for judgment-level criteria, classify the candidate's support as verified fact, inference, assumption, or guess; unsupported load-bearing claims fail the criterion.
6. **Verdict table** - one row per criterion: criterion | kind | evidence | verdict. Overall verdict fails if any disqualifying criterion fails. State what could not be checked here and why.

## Conditional moves
- When a deterministic criterion needs tools you lack, mark it NOT-RUNNABLE-HERE - never infer a pass.
- When the candidate spans domains, apply generic criteria plus each touched domain's disqualifiers.

## Output contract
Per-criterion verdict table, disqualifier findings quoted verbatim, list of unchecked criteria with reasons, and an overall PASS/FAIL/NOT-FULLY-CHECKABLE verdict.

## Delivery notes (small-model packets)
If delegating steps to a smaller model: one bounded objective per packet, all inputs named explicitly, facts separated from instructions, uncertainty marked 'UNCERTAIN: ...' rather than invented away.

## Before answering
Check the draft against references/failure-checks.md (the failure-mode catalog) and references/verification.md (domain verifier criteria). Repair procedures live in references/contracts.md.
