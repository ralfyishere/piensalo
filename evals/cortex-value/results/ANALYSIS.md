# Cortex-Value Evaluation — Results & Analysis

**Preregistration:** frozen at `df4c819` before any outcome-producing call.
**Model:** `qwen2.5:7b` (Q4_K_M, Ollama, temperature=0, seed=42).
**Raw data:** `run.json` (per-call ledgers) · `summary.json` (aggregates + gate).

## HYPOTHESIS → MEASURED RESULT

Hypothesis: PIÉNSALO's shipping THINK/CONTEXT/CHECK mechanisms produce
measurable net value on a real local 7B versus the same model alone.

**Measured result: the gate FAILED (criteria 1 and 7 of 8).** On these 12
frozen tasks this model is largely competent alone (10/12 direct), the
cortex's *safety* mechanisms worked exactly as designed, one mechanism
produced a genuine improvement, and two mechanisms caused measurable harm with
precisely identified root causes. optimize-safe is **not earned** by this run.

## Scoreboard (critical-pass per condition)

| Condition | Pass | Verdicts vs direct | Token overhead | Wall |
|---|---|---|---|---|
| A direct | **10/12** | — | — | 58 s |
| B CONTEXT | 9/12 | 1 IMPROVED · 8 MAINTAINED · **2 REGRESSION** · 1 SAFE FALLBACK | +701 | 53 s |
| C THINK+CONTEXT | 7/12 | 4 MAINTAINED · **5 REGRESSION** · 3 SAFE FALLBACK | +19,730 | 303 s |
| D FULL CORTEX | 9/12* | 6 MAINTAINED · 1 CORRECT ABSTENTION · 2 SAFE FALLBACK · (…) | +5,268 | 208 s |

\* incl. one grader artifact (12-D, below) and one CHECK-damaged draft (11-D).

## Findings

**F1 — The Context Optimizer regressed both real long-context tasks (B: 05,
06), and the root cause is value-blind verification.** Selection dropped or
distracted from needed facts; the model emitted template placeholders
(`DATE: YYYY-MM-DD`, `DB: <name>`) or superseded values (`VERSION: 2.4.0`,
`REGION: us-east-1`); the runtime's **presence-only** contract saw every
required line present, verified "pass", triggered **zero** expansion rounds,
and accepted wrong answers. Presence-only verification cannot make context
optimization safe on value-exact tasks. (The `expectations` mechanism exists
in the runtime but was not wired with expected values — by design in this
eval, because a deployed optimizer does not know the answers in advance. The
fix must come from selection/expansion policy, not from oracle values.)

**F2 — Generic THINK scaffolding harmed a competent model at scale (C: 5
critical regressions).** The ~1.2k-token cognitive program wrapped around
exact-format tasks (haiku, JSON-only, anchored fields, code-only) made the
model annotate, fence, or reorganize its output — breaking formats it handles
perfectly when asked directly. On the two genuinely hard planning tasks the
direct model already passed, so THINK added 35–70 s and thousands of tokens
for zero lift. This replicates the repo's prior negative-transfer law on a
second model family, live.

**F3 — CHECK damaged already-correct work through a misaligned acceptance
signal (D: task 11).** The deterministic scanner fired a false positive
(`ignored-disqualifier`, 0.55) on a fully compliant draft; the repair call
produced output that kept all four values intact but wrapped them in a code
fence and echoed repair instructions; the acceptance rule ("fewer scanner
defects") saw improvement where the contract saw delivery damage. The
one-layer harm law reproduced: **values intact, delivery broken.** Direct
also damaged the draft (appended commentary) — the failure class is real; the
guard's alignment is the defect.

**F4 — The one genuine IMPROVED came from the contract envelope (B: task
11).** The runtime's REQUIRED SUBMISSION FORMAT block ("nothing after the
final required line") made the model deliver the draft byte-clean, fixing the
delivery damage the direct model caused. Deterministic, cheap (+166 tokens),
and it addressed the exact failure the direct arm exhibited.

**F5 — The safety layer worked everywhere it was engaged.** Task 12: B and C
refused optimization (mandatory 659 est tokens > 120 budget) and fell back to
full context, answering correctly — zero silent truncation. Task 07-D: CHECK
inspected a correct JSON answer and **abstained**. Router in D: all three
pass-through tasks passed through untouched (0% unnecessary intervention);
simple tasks were never complicated.

**F6 — No condition rescued absent capability (09).** The model cannot write
`parse_duration` to spec under any arm; repair didn't fix cognition. Where
the capability floor is the binding constraint, scaffolding has nothing to
amplify on this task shape.

## Frozen gate

| Criterion | Verdict |
|---|---|
| 1. 0 accepted critical regressions | **FAIL** (B: 05, 06) |
| 2. ≥75% router eligibility | PASS (11/12, 92%, computed at freeze) |
| 3. ≤15% unnecessary intervention on pass-through | PASS (0%) |
| 4. ≥1 genuine improvement | PASS (11-B) |
| 5. no median requirement reduction | PASS (medians 1.0 across) |
| 6. safe fallback on the unsafe task | PASS (B, C; D never optimized — documented router miss) |
| 7. already-correct not damaged by CHECK | **FAIL** (11-D delivery damage) |
| 8. all costs reported | PASS |

**GATE: FAIL → optimize-safe is not merged, not released.**

## Grader artifact (documented, raw numbers unchanged)

12-D: `spec_values` imposes optimizer-refusal criteria on every cortex arm;
D's router (documented freeze-time miss) routed CHECK, never optimized, and
answered **correctly from full context** — no truncation occurred. The raw
cell records `critical_pass=False`; this artifact is noted here and in
`summary.json` rather than regraded.

## Limitations

One model, one machine, n=1 per cell (deterministic settings), 12 tasks,
single frozen router policy, presence-only contracts in the runtime arm.
Direct baseline near ceiling (10/12) — this set cannot show large lifts, but
it measures harm and safety cleanly (which is what it caught).

## Smallest next experiments (one per failed mechanism)

1. **F1:** selection-integrity probe — when the task's contract fields cannot
   be traced to a selected chunk (value provenance), force expansion or
   refuse; rerun 05/06. No oracle values needed.
2. **F3:** repair-acceptance alignment — accept a repair only if it does not
   *increase* contract violations (delivery-layer guard), not on scanner
   defect count; rerun 11.
3. **F2:** THINK gating — never attach the full cognitive program to tasks
   with an exact output contract; test a 3-line objective/constraint recap
   instead.
