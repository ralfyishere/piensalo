> **DEMO — hand-authored illustration, not benchmark evidence.**
> Both outputs in this directory were written by hand to illustrate an
> observable behavioral difference. No model produced them, nothing here was
> graded by the eval harness, and none of this supports a quantitative claim.
> For measurable evidence, see `evals/` (and note that even the published
> eval tasks are development/demo sets, not headline benchmarks).

# What to look at

**Observable difference.** The bare output answers the literal question
("one number") by grabbing the bigger, older, sales-sourced figure and
never mentions that a second provided source corrected it. The Piénsalo-style output (1) detects that the sources conflict, (2) explains the
*mechanism* of the discrepancy rather than just averaging or picking, (3)
identifies which document controls and why (later, explains the delta,
matches the product's actual constraint), and (4) refuses to launder the
growth rate from the old basis onto the new one — it flags 22% as now
unsupported, which the bare answer silently carried along.

**Verification.** Everything asserted is checkable against the two provided
briefs; the one thing that is NOT checkable (growth on the re-based
segment) is explicitly labeled as such instead of being presented as fact.

**Honest costs.** The disciplined answer does not deliver what was
literally asked for (one clean number) and is several times longer. That is
a real cost in an executive setting — the mitigation is the structure:
the recommended number is still on one line, with the caveats beneath it
rather than instead of it.
