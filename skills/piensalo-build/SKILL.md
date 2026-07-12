---
name: piensalo-build
description: "Software build-and-debug workflow: symptom capture, minimal reproduction, ranked hypotheses, discriminating tests, minimal in-scope fix, regression proof with quoted output. Use when code is broken, failing, or behaving unexpectedly, or when implementing a change that must not regress anything. Trigger phrases: 'fix this bug', 'tests are failing', 'why is this crashing', 'implement X without breaking Y'."
license: MIT
---

# piensalo-build

The build-and-debug workflow of Fable Think (domain: software build & debugging). Work the numbered steps in order; each step's output feeds the next. Do not skip steps silently - if one does not apply, say so in one line.

## Primary workflow
1. **Recover real objective** - Per intent-clarity: decode what the requester actually needs before optimizing anything. Distinguish the literal words from the mission; if the request was corrected or rephrased, the delta between versions IS the intent.
2. **Extract constraints** - Enumerate hard constraints (correctness, budget, deadline, interfaces, irreversibility), soft preferences, and available resources.
3. **Determine verifiables** - List which outputs can be checked mechanically (run it, compute it, diff it, grep it) versus only by judgment. Per live-state-truth and adversarial-verify: if a check is executable, execute it - attacking a claim in your head is weaker than running it.
4. **Capture symptom** - Per debugging-playbook: capture the symptom verbatim - full error text, exact command, exact input, environment. 'Something about a timeout' is not a symptom.
5. **Reproduce** - Per debugging-playbook: find the smallest, fastest, most deterministic reproduction - every minute here is repaid at every hypothesis test.
6. **Symptom vs cause** - Separate the observed symptom from the causal layer beneath it. Per debugging-playbook and intent-clarity's symptom-fix rule: 'increase the timeout' treats the symptom; ask what produces the slowness.
7. **Generate hypotheses** - Per debugging-playbook: generate 2-4 ranked hypotheses, ranked by likelihood x cheapness-to-test. Sources: the error itself (read ALL of it), the diff since it last worked, known failure-mode catalogs, and where this class of bug usually lives.
8. **Hypothesis discrimination** - Per debugging-playbook: design a discriminating test per hypothesis - one with DIFFERENT predicted outcomes depending on truth; otherwise it is an activity, not a test. Write the prediction BEFORE running.
9. **Minimal fix** - Fix the confirmed cause with the smallest change that removes it. Per scope-fence: fix what was asked, flag what was found - the module's other bugs go to the flag list, not the diff.
10. **Regression test** - Per debugging-playbook: prove the fix by prediction - the reproduction that failed must now pass, and the previously-passing suite must still pass. Add a regression test that encodes the bug so it cannot silently return.
11. **Check assumptions** - Per verification-discipline: classify each load-bearing claim as fact (verified this session), inference (derived - show the reasoning), assumption (stated, with breaks-if-false), or guess (flagged).
12. **Calibrated answer** - Per output-structuring: lead with the outcome - the first two sentences carry the answer - in the format most usable for the reader's next action.

## Conditional moves
- When all hypotheses are eliminated: return to **Generate hypotheses** and rework from there.
- When the fix did not remove the symptom or caused a regression: return to **Hypothesis discrimination** and rework from there.
- When the reproduction contradicts the recorded symptom: return to **Capture symptom** and rework from there.

## Output contract
A confirmed root cause with its evidence table (hypothesis | test | prediction | result | verdict), a minimal in-scope fix diff, quoted regression-test output proving repro-now-passes and suite-still-green, an out-of-scope flag list, and explicitly labeled residual assumptions.

## Delivery notes (small-model packets)
If delegating steps to a smaller model: one bounded objective per packet, all inputs named explicitly, facts separated from instructions, uncertainty marked 'UNCERTAIN: ...' rather than invented away.

## Before answering
Check the draft against references/failure-checks.md (the failure-mode catalog) and references/verification.md (domain verifier criteria). Repair procedures live in references/contracts.md.
