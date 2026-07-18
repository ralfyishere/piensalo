# Negative Results

Things we tried that failed, hurt, or misled us — preserved in public because
principle 6 of the [Manifesto](MANIFESTO.md) says they belong here. Each entry
is stated generically (no private identifiers) but reflects a real, measured
outcome in our development history. Where a result shaped the design, the
design consequence is noted.

Reporting format for new entries: use the
[negative-transfer issue template](.github/ISSUE_TEMPLATE/negative-transfer.yml).

---

## NR-1 · Larger prompts harmed easy-task performance

In controlled runs, adding a substantial always-on instruction block made a
competent model **worse** on easy tasks it previously handled cleanly. The
instructions competed for attention with the task itself.

**Design consequence:** the always-on surface is kept minimal; everything else
is a skill that loads only on trigger. Any addition to a proven instruction set
requires a paired A/B, not a plausibility argument.

## NR-2 · Full knowledge graphs regressed a weak model

Supplying a complete reasoning graph as context — intended as scaffolding —
measurably regressed a weaker model's performance. The overhead of consuming
the structure exceeded its benefit.

**Design consequence:** cognitive programs are bounded and sized to the task;
structure is a budget, not a default maximum.

## NR-3 · A correct repair failed through bad routing

A repair that was verifiably correct in isolation produced no improvement
end-to-end, because routing defects (a miscalibrated threshold plus a schema
mismatch) sent it to the wrong place. The repair was fine; the plumbing erased
it.

**Design consequence:** routing is itself a failure layer in
`classify_failure`, and end-to-end verification is required — component-level
correctness is not accepted as an outcome claim.

## NR-4 · Correct reasoning failed through delivery formatting

A model reached the right answer and then destroyed it at the output stage —
formatting requirements mangled correct work into a failing deliverable.

**Design consequence:** `deliver` is a distinct operation with its own
inspection layer (`delivery`); reasoning quality and delivery quality are
graded separately.

## NR-5 · Graders created false findings in both directions

Automated grading produced errors both ways: correct work marked as failing
because it lacked expected decoration (under-credit), and failing work marked
as passing because plausible prose resembled the rubric (false credit via
prose fallback).

**Design consequence:** graders are treated as components under test, not
oracles. Grading targets observable, layer-specific criteria, and grader
disagreement is itself recorded as evidence.

## NR-6 · Silent model fallback corrupted attribution

A runtime silently substituted a different model when the configured one was
unavailable. Every measurement from those runs attributed one model's behavior
to another, corrupting the evidence base until detected.

**Design consequence:** silent model fallback is **prohibited**. Model identity
is declared, recorded per run, and a missing model is a hard stop — see
[docs/model-provenance.md](docs/model-provenance.md).

## NR-7 · A loop looked resumable but persisted counters blocked continuation

A loop's state appeared fully resumable — programs and evidence intact — yet
continuation silently failed because persisted internal counters had reached
their bounds and were never surfaced.

**Design consequence:** loop state is inspectable, budgets are reported in
`loop` output (used / remaining), and "resumable" is a verified property, not
an inferred one.

## NR-8 · Abstention beat intervention on already-competent work

When the underlying work was already correct, intervening — "improving",
reformatting, re-deriving — made outcomes worse more often than better.
Doing nothing was the winning move, and the system originally had no way to
choose it.

**Design consequence:** `NO REPAIR NEEDED` is a first-class verdict, graded as
a success when correct. Inspection must be able to end without a repair.

---

## NR-9 · Presence-only verification let optimized context ship wrong values

In the preregistered cortex-value run (qwen2.5:7b, 12 frozen tasks,
`evals/cortex-value/`), the Context Optimizer regressed both real
long-context tasks: selection dropped or diluted needed facts, the model
emitted template placeholders and superseded values, and the runtime's
presence-only contract verified "all required lines present" — so **zero
expansion rounds fired** and wrong answers were accepted. The same tasks
passed with full context.

**Design consequence:** presence-only verification cannot gate context
optimization on value-exact tasks. Expansion policy needs a
selection-integrity signal (can each required field be traced to a selected
chunk?), not just line presence.

**Repair verified (frozen rerun):** the selection-integrity layer
(`context/integrity.py`) eliminated both wrong-value regressions — one via
in-budget evidence expansion, one via full-context fallback — with zero new
regressions. Evidence: `evals/cortex-value/results/integrity-repair/`.

---

## NR-10 · A repair "improvement" signal disagreed with the contract — and won

Same run, the already-correct-draft task: the deterministic scanner fired a
false positive on a fully compliant draft, the repair kept every value intact
but wrapped the output in a code fence and echoed instruction text, and the
acceptance rule — "fewer scanner defects" — accepted it. The contract grader
correctly scored it as delivery damage. The one-layer harm law reproduced on
a second model family: cognition intact, delivery broken.

**Design consequence:** repair acceptance must be gated on the strongest
available deterministic check (the output contract), never on the detector's
own defect count. A repair that increases contract violations is a rejection,
whatever the scanner thinks.

**Repair verified (frozen rerun):** contract-gated acceptance
(`verify/acceptance.py`) preserved the compliant draft byte-for-byte with
zero repair calls (CORRECT_ABSTENTION). Evidence:
`evals/cortex-value/results/integrity-repair/`.

---

## NR-11 · A full cognitive program harmed a competent model's exact-format work

Same run: prepending the ~1.2k-token THINK program to exact-format tasks
(three-line poem, JSON-only, anchored fields, code-only) caused five critical
regressions — the model annotated, fenced, or reorganized output it formats
perfectly when asked directly. On the hard planning tasks the model already
passed direct, so the program added tokens and latency for zero lift.

**Design consequence:** THINK must be gated away from tasks with exact output
contracts on models that pass them directly; replicates NR-1/NR-8 on a second
model family, live, at scale.

**Repair verified (frozen rerun):** the EXACT_DELIVERY_CONTRACT router signal
suppressed full THINK on such tasks; all five regressions disappeared and
condition-C tokens fell 72%. Evidence:
`evals/cortex-value/results/integrity-repair/`.

---

## What qualifies for this file

A negative result is publishable here when it is (a) a real measured outcome,
(b) stated without private identifiers, and (c) actionable — someone reading it
should be able to avoid repeating the experiment. Wins go in
[EVIDENCE.md](EVIDENCE.md); this file is deliberately reserved for the other
kind.
