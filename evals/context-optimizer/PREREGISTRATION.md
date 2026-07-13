# Context Optimizer evaluation — pre-registration

Frozen BEFORE any model run. Task answers, graders, budgets, and gate
thresholds are not tuned after seeing optimized results. Generated tasks
(`make_tasks.py` → `tasks/`) are committed and then read-only for this
evaluation.

## Design

Eight paired tasks. Each runs full context vs optimized context with the
SAME task, target model, output contract, and deterministic grader:

| # | Task | Covers | Budget |
|---|------|--------|--------|
| 01 | exact-recall | exact fact + decision recall (deploy command, commit, active vs superseded decision) | 1600 |
| 02 | constraint-adherence | critical constraints quoted byte-for-byte in a plan | 1700 |
| 03 | quantitative | arithmetic over facts buried among numeric distractors | 1400 |
| 04 | structured-output | strict output contract (`no_extra_lines`) | 1300 |
| 05 | repo-coding | repository/coding context (file, function, repro command) | 1500 |
| 06 | failed-approach | failed-approach retention and avoidance | 1500 |
| 07 | distractor-heavy | needle in heavy distractor mass with decoy owners — improvement is possible, not just shorter input | 1200 |
| 08 | fallback-required | mandatory context (40 EXACT rules) exceeds a 400-token budget → OPTIMIZATION REFUSED → safe full-context fallback | 400 |

- Target model: `claude-haiku-4-5-20251001` via the `claude-cli` adapter
  (explicit; provenance asserted; adapter exposes no temperature/seed —
  single-sample comparison, recorded as such).
- Grader: deterministic contract + oracle (`expected.json`), identical for
  both arms. No model judge in the scored comparison.
- Expansion limit: 2. Fallback mode in evaluation: recommend (the
  benchmark baseline doubles as the full-context result).

## Success criteria (gate thresholds, from the operator directive)

1. Zero critical constraint regressions (a requirement full context
   passes that the accepted optimized response fails).
2. Median gross input-context reduction >= 50% (over tasks where an
   optimized packet was produced).
3. Median deployable runtime net token savings >= 30% (adapter-reported
   optimized-arm input tokens vs baseline input tokens).
4. At least 6 of 8 tasks safely use optimized context (verdict
   MAINTAINED or IMPROVED with outcome OPTIMIZED CONTEXT ACCEPTED).
5. Task 08 must refuse optimization and fall back safely (SAFE FALLBACK
   is the pre-registered CORRECT outcome for it, not a failure).
6. All costs, expansions, and fallbacks reported; benchmark baseline cost
   ledgered separately from deployable runtime cost.

Quality verdict per task: MAINTAINED / IMPROVED / REGRESSION / SAFE
FALLBACK, compared requirement-by-requirement. One critical regression
fails the merge gate regardless of medians. A failed gate is recorded
honestly; it is never permission to weaken this file.
