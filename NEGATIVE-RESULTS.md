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

## What qualifies for this file

A negative result is publishable here when it is (a) a real measured outcome,
(b) stated without private identifiers, and (c) actionable — someone reading it
should be able to avoid repeating the experiment. Wins go in
[EVIDENCE.md](EVIDENCE.md); this file is deliberately reserved for the other
kind.
