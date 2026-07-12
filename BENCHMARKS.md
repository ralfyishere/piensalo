# Benchmarks

Two pre-registered controlled runs stand behind the current evidence map
([EVIDENCE.md](EVIDENCE.md)). Both are internal-lab runs; the public
reproduction harness lives in [evals/](evals/) and reproducing (or
refuting) these numbers on your own models is a first-class contribution
([evals/results/](evals/results/)).

## Design shared by both runs

| Property | Value |
|---|---|
| Cells | 8 sealed tasks × 3 reps × 5 conditions = 120 |
| Execution model | `claude-haiku-4-5` (requested + resolved recorded per cell) |
| Conditions | bare · monolithic skill · adaptive repair · oracle repair · output-contract guardian |
| Graders | deterministic, layered (cognition / delivery / rendering / routing / verification), frozen before any cell |
| Gates | pre-registered, frozen before any cell, never re-scoped |
| Stub policy | infra failures = NOT RUN, never FAIL |
| Budget | equal across conditions (bounded turns, bounded prompt prefix) |

n = 8 tasks per run. Everything below is directional, not powered. We
publish it anyway, with the confounds attached.

## Run 1 — weak-baseline task set

The bare model failed most procedural tasks (procedural mean 37.5/100).

| Finding | Number | Confound |
|---|---|---|
| Oracle targeted repair, procedural lift | **+18.8pp** | task-concentrated: +66.7 on the best task, **−20 on the worst** (a repair pass destroyed a delivered answer); one task grader-blind |
| Output-contract guardian, delivery-failure reduction | **30% relative** (0.417 → 0.292) | part of the apparent cognition movement was measurement visibility (absent output is ungradeable) |
| Guardian paired cognition harm | **zero** | — |
| Adaptive router fires | **0 / 24** | two deterministic implementation defects (threshold arithmetic; contract-schema mismatch) — found by forensics, fixed, and re-tested in run 2 |
| Grader artifacts discovered | 3 classes | fixed in the run-2 grading library; both directions (false credit AND false blame) |

## Run 2 — saturated task set (the harm measurement)

The fresh set turned out too easy: bare cognition rate **1.0** (verified
against answer keys). No lift was measurable — so harm became cleanly
measurable instead.

| Finding | Number | Note |
|---|---|---|
| Forced repair on correct drafts (oracle) | **−20pp procedural, 7/24 paired regressions ≥ 40pp** | every regression was DELIVERY damage (prose wrapped around contract-exact output) |
| Cognition flips from forced repair | **0 / 48 cells** | re-prompting is a delivery risk, not a reasoning risk |
| Adaptive router (after both fixes) | fires 8/24, precision **0.375** on correct drafts | third defect class: correctness-blind detection; abstention on easy classes was perfect (12/12) |
| Monolithic skill on knowledge-floor tasks | **60 vs 100**, 2 induced wrong answers | artifact-free graders this time; +1109 median tokens |
| Guardian on contract-clean drafts | 0 fires, **0 harm** (24/24 correct abstention) | its improvement gate was unexercised — no delivery failures to fix |
| Abstaining paths, total harm | **zero** | the core product thesis, measured |

## What these runs do NOT show

- No cross-model generality: one small-model family executed the cells.
- No statistical certainty: n = 8 tasks per run.
- No end-to-end product benchmark yet: these are mechanism isolation runs.
- Run 2's saturation means the repair-lift hypothesis still rests on run 1
  alone. The next kill test is a difficulty-calibrated fresh set (pilot
  gate: bare procedural cognition ≤ 0.7 before sealing).

## Reproduce

```
make benchmark          # grader self-test battery + 2-task smoke, no API needed
uv run fable-think-eval # full harness (bring your own adapter/model)
```

Task sets in `evals/public-tasks/` are labeled `DEMO` or `DEVELOPMENT`.
Internal unconsumed held-out reserves are never published; consumed sets
are ported here after their runs close.
