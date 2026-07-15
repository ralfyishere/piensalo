<!-- GENERATED FILE — do not edit by hand.
     Regenerate: ./examples/context-optimizer/launch-demo.sh > capture,
     then wrap the capture in the fence below.
     Verified byte-for-byte by tests/test_launch_demo_parity.py. -->

# PIÉNSALO Context Optimizer — launch demo transcript

This is the exact terminal output of
[`launch-demo.sh`](launch-demo.sh), captured verbatim. The demo is
**offline** — no API key, no model call at run time.

Every line is labeled by provenance:

- **LIVE** steps (`[3]`, `[5]`, `[7]`) run the shipped deterministic
  optimizer on your machine and reproduce byte-for-byte.
- **RECORDED** steps (`[6]`, and the preregistered summary) replay the
  committed real model run
  (`claude-haiku-4-5-20251001`, single sample, recorded 2026-07-14) and
  are integrity-checked against the current inputs — never presented as
  freshly generated.

A parity test (`tests/test_launch_demo_parity.py`) re-runs the script and
fails CI if this transcript and the script ever diverge.

```console
$ ./examples/context-optimizer/launch-demo.sh
----------------------------------------------------------------------
PIENSALO CONTEXT OPTIMIZER
Use less context. Lose none of the intelligence.
(offline demo: LIVE steps run now, RECORDED steps replay a committed run)
----------------------------------------------------------------------

[1] THE TASK

    Fix the flaky CI failure in the widgets service. From the project context,
    report exactly which file and function must change, the exact command that
    reproduces the failure, and the exact staging deploy command — quote
    commands byte-for-byte. Answer with exactly these lines:
    
    FILE: <exact path>
    FUNCTION: <name>
    REPRO: <exact command>
    DEPLOY: <exact command>

[2] THE FULL CONTEXT AVAILABLE TO THE MODEL

    context.txt: 72 lines, ~1807 tokens (chars/4 estimate)
    A real engineering thread: decisions, constraints, exact commands,
    one superseded decision — buried in 26 paragraphs of office chatter.

[3] OPTIMIZE  — LIVE, deterministic, no model call

    wrote .launch-demo-out/optimize/optimized-context.md
    wrote .launch-demo-out/optimize/selection-manifest.json
    wrote .launch-demo-out/optimize/optimization-report.json
    wrote .launch-demo-out/optimize/capsule.json
    original tokens (est): 1807  optimized: 583  gross reduction: 68%
    mandatory: 120  selected: 79  omitted: 1551
    behavioral status: UNMEASURED (no model was run)

[4] WHAT WAS KEPT — AND WHAT WAS LEFT OUT (every chunk has a reason)

    INCLUDED_MANDATORY       9
    INCLUDED_RELEVANT        2
    OMITTED_LOW_RELEVANCE    26
    OMITTED_SUPERSEDED       1

    kept unconditionally (mandatory):
      - objective: active objective
      - success_condition: active success_condition
      - decision: active decision
      - constraint: active constraint
      - constraint: active constraint
      - artifact: active artifact
    superseded decision kept as history, never shown as current:
      - decision-60a3bd6ec1e3 (decision, superseded_by decision-65ccb27fdcb2)

[5] SIZE: FULL vs OPTIMIZED

    original context :  1807 tokens (est)
    optimized packet :   583 tokens (est)
    gross reduction  :    67.7%
    behavioral status: UNMEASURED (no model has run)

[6] DID THE ANSWER SURVIVE?  — RECORDED committed model run
    (claude-haiku-4-5-20251001 via claude-cli, single sample,
     recorded 2026-07-14; replayed here, NOT generated live)

    integrity: recorded run matches current context.txt (sha256 a1792ce388cfafcf...)
    full context     -> 9/9 deterministic requirements passed
    optimized packet -> 9/9 deterministic requirements passed
    verdict          : MAINTAINED
    prompt tokens    : 2007 full -> 687 optimized (65.8% input savings, est)
    expansions: 0   fallback: False

[7] THE UNSAFE CASE  — LIVE: optimization is REFUSED, never truncated

    40 binding rules, every one mandatory, budget 400 tokens:

    OPTIMIZATION REFUSED — FULL CONTEXT REQUIRED
    mandatory context alone is 858 tokens; budget leaves 215 after the task envelope. Critical information is never truncated — raise the budget or narrow the task.

    RECORDED evaluation outcome for this task: SAFE FALLBACK (OPTIMIZATION REJECTED — FULL CONTEXT REQUIRED)

----------------------------------------------------------------------
THE PREREGISTERED RESULT (8 paired tasks, committed under
evals/context-optimizer/results/ — one Claude-family model, single
samples, deterministic graders; replication pending):

    median context reduction         : 80.2%
    median runtime net input savings : 76.9%
    optimizable tasks maintained     : 7/7
    deterministic regressions        : 0
    designed unsafe case fell back   : yes

Run the model comparison LIVE against your own model:
  piensalo context evaluate --task task.md --context context.txt \
    --adapter claude-cli --model <model> --contract contract.json \
    --expected expected.json --budgets 1500 --output my-eval
----------------------------------------------------------------------
```
