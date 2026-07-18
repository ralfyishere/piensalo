# Integrity-Repair Rerun — Original vs Repaired (frozen evaluation unchanged)

**Confirmation of the frozen protocol:** identical 12 tasks, graders, budgets,
model (`qwen2.5:7b`, Q4_K_M), settings (temperature=0, seed=42), four
conditions, and gate — preregistration `df4c819` untouched. The only changes
are the three repaired mechanisms (commit history on `cortex-integrity-repair`):
selection integrity (NR-9), contract-gated repair acceptance (NR-10), and
EXACT_DELIVERY_CONTRACT THINK suppression (NR-11). Original run preserved
unchanged at `../run.json`; this rerun lives here.

## Headline

| Condition | Original | Repaired | Tokens (orig→new) | Wall (orig→new) |
|---|---|---|---|---|
| A DIRECT | 10/12 | 10/12 | 4,345 → 4,345 | 58 → 49 s |
| B CONTEXT | 9/12 | **11/12** | 5,046 → 5,620 | 53 → 48 s |
| C THINK+CONTEXT | 7/12 | **11/12** | 24,075 → **6,801 (−72%)** | 303 → **30 s (−90%)** |
| D FULL CORTEX | 9/12 | **10/12** | 14,146 → **4,651 (−67%)** | 209 → **22 s (−90%)** |

(Direct wall difference is environmental — warm KV cache on the rerun; token
counts are identical, as determinism requires.)

**FROZEN GATE: PASS (8/8).** Original run failed criteria 1 and 7; both now
pass, and no other criterion regressed.

## Each prior regression, individually (the kill tests)

| Task / arm | Original | Root cause | Repaired behavior | Flipped? | Tokens Δ | New effects |
|---|---|---|---|---|---|---|
| 05-B | REGRESSION (VERSION 2.4.0, DATE placeholder accepted) | value-blind presence-only verification | integrity pre-flight found un-grounded fields → expanded the missing paragraphs → **correct values, OPTIMIZED ACCEPTED** | ✅ | +501 vs orig-B | none |
| 06-B | REGRESSION (`DB: <name>`, us-east-1) | same | `DB` has no lexical candidate → UNMEASURED → **SAFE FALLBACK (full context), correct values** | ✅ | +73 | none |
| 01-C | REGRESSION (verbose) | THINK program on trivial task | THINK abstained (EXACT_DELIVERY) → MAINTAINED | ✅ | −1,551 | none |
| 02-C | REGRESSION (haiku broken) | same | abstained → MAINTAINED | ✅ | −1,168 | none |
| 07-C | REGRESSION (JSON w/ prose) | same | abstained → MAINTAINED | ✅ | −2,414 | none |
| 08-C | REGRESSION (fields broken) | same | abstained → MAINTAINED | ✅ | −1,466 | none |
| 09-C | REGRESSION (worse than direct) | same | abstained → MAINTAINED (capability floor stands: fails in **all** arms) | ✅ | −2,035 | none |
| 11-D | draft delivery-damaged by accepted repair | detector judged its own repair | contract probe → **CORRECT ABSTENTION, 0 model calls, draft byte-for-byte** | ✅ | −1,127 | none |

**New regressions: none.** 12-D remains the one pre-existing, documented
grader artifact (refusal criteria applied to an arm that never optimized; its
answer values are correct, from full context — unchanged from the original
run, not a new effect).

## Safety re-verification (unchanged behavior required)

- **Unsafe task 12:** B and C still refuse and fall back correctly ✅
- **Pass-through:** 01/02/10 still `PASS_THROUGH`, untouched, 0% unnecessary
  intervention ✅
- **Abstentions in D:** 03, 04, 07, 08, 11 — all correct, no wasted repair
  calls (08-D dropped from 2 calls to 1) ✅

## Router differences vs the frozen original (scored under original rules)

The repaired router suppresses THINK on exact-delivery contracts. Changes:
03/04 `THINK`→`CHECK` (counted as **misses**), 05/06
`THINK_AND_CONTEXT`→`CONTEXT` (still eligible). Repaired eligibility:
**9/12 = 75%** — a boundary pass of the frozen ≥75% criterion, down from the
original 11/12. The frozen expected decisions were **not** edited.

## What the evidence now supports (bounded)

- **Earned, positive value:** the contract envelope + CHECK abstention on
  draft-review/exact-contract tasks — improved twice (11-B, 11-C) and
  preserved a correct draft at literally zero token cost (11-D).
- **Earned, safety only:** integrity-gated context optimization — zero wrong-
  value acceptances, correct fallbacks; but **no net token savings
  demonstrated on these tasks** (B costs +1,275 tokens vs direct here). Its
  value claim is *safety under optimization*, not efficiency, until a
  savings-showing task class is measured.
- **Earned, harm avoidance:** THINK suppression on exact-delivery tasks
  (−72% condition-C tokens, all five regressions gone). THINK's *positive*
  case remains unproven on this model (planning tasks pass direct).

## Limitations

Same as the original run: one model, one machine, n=1 per cell, near-ceiling
direct baseline. The rerun proves the exact failures are eliminated; it does
not prove uplift beyond the one improved class.
