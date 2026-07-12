> **DEMO — hand-authored illustration, not benchmark evidence.**
> Both outputs in this directory were written by hand to illustrate an
> observable behavioral difference. No model produced them, nothing here was
> graded by the eval harness, and none of this supports a quantitative claim.
> For measurable evidence, see `evals/` (and note that even the published
> eval tasks are development/demo sets, not headline benchmarks).

# What to look at

**Observable difference.** The bare output is fluent, professional — and
fails five of the six stated constraints: ~150 words of body but no outage
window times, no card-safety statement, no refund remedy, no named contact,
and it is dense with exactly the jargon the brief banned (TLS, SSL
handshake, edge termination, PKI). It reads like an email about the
incident *for the engineering team's pride*, not for a customer's next
action. The Fable Think-style output treats the brief as an output
contract: every required element is present, and the visible contract-check
footer verifies each one — including an actual word count — before
delivery.

**Verification.** Count the words (109), scan for the banned term classes,
check the four required facts against the brief. The footer makes the
output auditable in seconds; the bare version can only be audited by
re-reading the brief and discovering the gaps one by one.

**Honest costs.** The contract-check pass adds a re-read and a footer the
customer never sees (the footer is stripped before sending). The prose is
also plainer — deliberately below the register some brands want, which is
a taste tradeoff the brief's "no jargon" line was taken to license.
