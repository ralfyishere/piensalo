# Layered grading

Every task in `evals/public-tasks/` is scored by a deterministic hidden grader
built on `layered_common.py`. The grader emits one JSON verdict that attributes
any failure to a **layer**, because "the model reasoned wrong" and "the model
reasoned right but shipped it wrong" are different findings, and collapsing
them into one pass/fail bit manufactures fake conclusions in both directions.

## The layers

| Layer | Meaning | Assigned by |
|---|---|---|
| `cognition` | The reasoning, value, or choice is wrong at its root. | grader |
| `delivery` | Reasoning is right, but the required output contract is violated (missing/renamed field, prose instead of the exact line). | grader |
| `rendering` | Answer present and correctly labeled but malformed at the token level (bold wrapping, thousands separator, wrong decimals) — a finer-grained delivery fault. | grader |
| `routing` | The wrong strategy/skill/condition was applied for the task. Reserved for the harness; graders never emit it. | harness |
| `verification` | The output claims a correctness it did not establish ("tested, passes" over a wrong result). | grader/harness |
| `delivery-incomplete` | No substantive output arrived: empty answer, permission stall, truncation. Cognition is UNMEASURED (`null`), never "failed". | grader |
| `harness` | The evaluation plumbing itself failed (unparseable grader output, missing cell). | harness |
| `provider` | The model backend failed (quota stub, API error, model mismatch). Cells are marked NOT-RUN and excluded — never graded as failures. | harness |

## Artifact classes this design prevents

These are real mis-grading patterns observed during internal development of
this battery; the library was hardened against each one during the public port,
and every task ships a probe battery (`probes/`) that regression-tests them.

1. **Decoration masking** — a correct answer wrapped in bold/backticks/bullets
   fails a naively anchored regex and gets scored as a *cognition* failure.
   Rule: strip decoration before any anchored parse; the decoration itself is a
   contract/rendering fault only. Probe class: `decorated-correct`.
2. **Fallback overreach** — a lenient prose fallback credits an answer the
   model never stated (e.g. inferring the value from a mention of the task's
   own numbers or board size). Rule: the fallback may only confirm an explicit
   "the answer is X" statement, explicit trap values veto, and it may only
   lower credit relative to the anchored parse. Probe class: `prose-trap`.
3. **Stub-graded-as-fail** — an API error or quota stub scored as a wrong
   answer, poisoning condition comparisons. Rule: stubs and stalls are
   `delivery-incomplete` with cognition `null`; the harness records NOT-RUN.
   Probe classes: `stub`, `stall`.
4. **Format/cognition conflation** — a right-value/wrong-format answer scored
   identically to a wrong-value answer. Rule: contract compliance is judged on
   the raw text, cognition on the decoration-stripped content, and the two are
   reported as separate layers with separate scores (60 vs 0).

## Verdict schema

The last line of grader stdout is:

```json
{
  "cognitive_correctness":    {"pass": true, "checks": {"...": true}},
  "task_contract_compliance": {"pass": false, "checks": {"...": false}},
  "deterministic_result":     {"pass": true, "checks": {"...": true}},
  "critical_failure":         false,
  "final_score":              60,
  "failure_layer":            "delivery"
}
```

`cognitive_correctness.pass` is `true`, `false`, or `null` (UNMEASURED).
Scores: 100 = clean pass; 60 = correct cognition, broken contract; 0 =
cognition failure or absent output.

## Verify the verifier

Graders are code and code has bugs. Before any run is graded, run the
self-test battery:

```
python3 evals/harness/grader_selftest.py
```

It executes every task's grader against that task's `probes/` (six required
probe classes) and compares the verdicts to `probes/expected.json`. A battery
that is not green is not evidence.
