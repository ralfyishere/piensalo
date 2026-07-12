> **DEMO — hand-authored illustration, not benchmark evidence.**
> Both outputs in this directory were written by hand to illustrate an
> observable behavioral difference. No model produced them, nothing here was
> graded by the eval harness, and none of this supports a quantitative claim.
> For measurable evidence, see `evals/` (and note that even the published
> eval tasks are development/demo sets, not headline benchmarks).

# What to look at

**Observable difference.** The bare output patches the symptom with a
`min()` that happens to satisfy the one failing test, and *claims* "this
should work now" without running anything. The clamp also silently encodes
the same wrong model (night portion measured from `night_start` regardless
of where the shift starts) — it survives these three tests by coincidence
of arithmetic, and nobody would notice until a new boundary case arrives.
The Piénsalo-style output (1) reproduces the failure first, (2) states
the root cause as a model error (missing interval intersection), (3)
replaces the model rather than clamping its output, (4) enumerates boundary
cases *derived from the corrected model* and adds them as regression tests,
and (5) reports what it did NOT verify (past-midnight wraps).

**Verification.** The table in the output is checkable by hand in under a
minute — every row is a one-line arithmetic evaluation. That is the point:
claims at the evidence level of "I ran it", not "it should".

**Honest costs.** The disciplined answer is roughly 3x longer, took the
equivalent of two extra reasoning passes (reproduce + boundary sweep), and
spends words on a caveat the happy path never needed. On a trivial one-line
fix that overhead can exceed the value; it pays off exactly when the bug is
a wrong model wearing a passing test.
