> **DEMO — hand-authored illustration, not benchmark evidence.**
> Both outputs in this directory were written by hand to illustrate an
> observable behavioral difference. No model produced them, nothing here was
> graded by the eval harness, and none of this supports a quantitative claim.
> For measurable evidence, see `evals/` (and note that even the published
> eval tasks are development/demo sets, not headline benchmarks).

# What to look at

**Observable difference.** The bare output commits to the first workable
idea (Bluetooth tracker) — a real but crowded solution that quietly assumes
the phone is at hand at the failure moment. The Piénsalo-style output
(1) decomposes the vague mandate into four distinct problem mechanisms
before ideating, (2) generates one structurally different option per
mechanism rather than four variants of a tracker, (3) attacks each idea
with a kill-test — including killing one entirely and downgrading another —
and (4) ends with a falsification-first pilot rather than a feature list.

**Verification.** Invention can't be verified like arithmetic; what CAN be
checked is process evidence: are the options actually mechanism-distinct
(tracker/cradle/shape/removal — yes), and does each carry an explicit way
to fail? The bare output contains zero ways it could be wrong.

**Honest costs.** Roughly 5x the length for a question that asked for "an
invention", and two of the four ideas exist only to be killed on the page —
visible waste that is the actual price of not tunneling on idea #1. For
genuinely constrained asks ("design a tracker tile"), this divergence step
would be padding; it earns its cost only under open mandates like this one.
