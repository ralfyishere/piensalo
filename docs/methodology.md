# Methodology

How Piénsalo capabilities are built, measured, and allowed to make claims.
This is the process behind [evidence-levels.md](evidence-levels.md); the
current results live in [EVIDENCE.md](../EVIDENCE.md).

## The loop

1. **Start from an observed failure.** Mechanisms are motivated by real,
   recorded failures — not by plausible-sounding capability ideas. Each
   mechanism's origin failure is documented with it.
2. **Design the mechanism and its evaluation together.** A mechanism proposal
   without an evaluation plan is incomplete. The plan states the tasks, the
   comparison condition, the grader, and the pre-declared success criteria
   *before* any run.
3. **Pre-register, then run.** Conditions, sample sizes, and grading criteria
   are frozen before data collection. Changing the rubric after seeing
   outputs invalidates the run — we restart, we don't reinterpret.
4. **Grade in layers.** Outputs are graded per failure layer (objective,
   plan, numeric, routing, delivery), not with a single holistic score.
   Holistic scores hide exactly the information repair needs.
5. **Audit the grader.** Graders err in both directions — under-crediting
   correct-but-undecorated work and over-crediting fluent prose (NR-5).
   Grader spot-checks are part of every experiment, and grader defects are
   findings, not embarrassments.
6. **Publish both directions.** Wins go to EVIDENCE.md with their level;
   losses go to [NEGATIVE-RESULTS.md](../NEGATIVE-RESULTS.md). Both are
   permanent.

## Controls we always apply

- **Paired comparison.** "With mechanism" runs against "without mechanism"
  on the same tasks — never against memory of how it used to go.
- **Fresh sessions.** Evaluation runs start from clean state; a session that
  has seen the mechanism's development can't grade it fairly.
- **Provenance.** Every run records its model identity. Runs with provenance
  gaps are discarded, not patched (NR-6 is why).
- **Quota/infrastructure stubs are NOT-RUN, never FAIL.** An output that is
  an infrastructure error is excluded from both numerator and denominator.
- **Abstention is graded.** On already-correct inputs, the correct verdict is
  `NO REPAIR NEEDED`; intervening counts against the mechanism (NR-8).

## What we refuse to do

- Claim guaranteed improvement, anywhere, for anything.
- Compare against a strawman baseline (an unprompted model doing a task no
  one would give it that way).
- Report a favorable single run as an effect. Single runs are anecdotes
  until replicated — including ours.
- Tune on the held-out set. Held-out tasks are created after mechanism
  freeze and used once.

## Known methodological limits (current)

Stated here so no reader has to discover them:

- Sample sizes are small; most comparisons are underpowered for small
  effects. We report counts, not just percentages, so you can judge.
- One model family has the deepest test coverage; cross-family claims are
  correspondingly weaker.
- Task suites are authored by the same team that builds mechanisms —
  external task contributions ([CONTRIBUTING.md](../CONTRIBUTING.md), type 4)
  and the v0.3 public benchmark season are the corrective.
