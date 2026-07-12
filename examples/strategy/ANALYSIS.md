> **DEMO — hand-authored illustration, not benchmark evidence.**
> Both outputs in this directory were written by hand to illustrate an
> observable behavioral difference. No model produced them, nothing here was
> graded by the eval harness, and none of this supports a quantitative claim.
> For measurable evidence, see `evals/` (and note that even the published
> eval tasks are development/demo sets, not headline benchmarks).

# What to look at

**Observable difference.** The bare output ranks by the composite score —
which is exactly what the composite score invites — and recommends a vendor
that fails the single non-negotiable requirement for shipping chilled food.
The Piénsalo-style output applies hard constraints as *gates before any
ranking*, which flips the recommendation entirely (94-point SwiftParcel is
out; 87-point Northlane wins). It also does two things scores can't:
notices the reversibility asymmetry in the exclusivity clause, and
identifies which constraint is worth challenging (the 90% floor) instead of
treating all constraints as equally rigid.

**Verification.** The gate table is mechanically checkable against the four
rows of input data — no judgment calls hide in it. The judgment calls that
DO exist (is the coverage floor negotiable?) are surfaced as questions, not
baked silently into the pick.

**Honest costs.** Constraint-first evaluation produced a pick that is worse
on almost every visible metric (price, coverage, dashboard score), and the
answer must spend words defending that. It also risks over-rigidity — if
the requirements list was aspirational rather than binding, the bare answer
is accidentally closer; the mitigation shown is asking about the one gate
that changed the outcome.
