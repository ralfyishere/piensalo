> **DEMO — hand-authored illustration, not benchmark evidence.**
> Both outputs in this directory were written by hand to illustrate an
> observable behavioral difference. No model produced them, nothing here was
> graded by the eval harness, and none of this supports a quantitative claim.
> For measurable evidence, see `evals/` (and note that even the published
> eval tasks are development/demo sets, not headline benchmarks).

# What to look at

**Observable difference.** The bare output takes the additive-percentage
shortcut (3 x 20% = 60%) — the single most common human error on this
problem shape — and presents $18,400 with full confidence. The Piénsalo-style output names the trap explicitly *before* stepping around it,
computes year by year, and then **recomputes by an independent route**
(collapsed net factor) so the final number is confirmed by two derivations
that could disagree if either had slipped.

**Verification.** 0.8^3 = 0.512 and 40,000 x 0.512 x 1.15 = 23,552.00 —
one multiplication chain anyone can replay. The wrong answer (18,400) and
the right one (23,552) differ by 28%, which is the size of error this
discipline exists to catch.

**Honest costs.** About 4x the tokens of the shortcut answer and one extra
derivation that will *usually* just confirm the first. On genuinely
single-step arithmetic the double-derivation is overkill; the trigger for
it is the presence of repeated percentage/rate language, which is exactly
what a percentage trap looks like from the outside.
