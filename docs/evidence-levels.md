# Evidence Levels

Every capability claim in Fable Think carries one of seven levels. The level
states how the claim could be wrong, and what has been done to find out. A
doc PR cannot change a level; only an experiment can.

## The levels

### DESIGNED
Engineered from failure analysis and first principles; **no empirical test
yet**. The mechanism has a rationale and an evaluation plan, and that is all
it has. New mechanisms and new skills start here, and saying so is required.

### SMOKE_TESTED
Run end-to-end at least once in a realistic setting; it functions and does
not obviously break. No controlled comparison — smoke tests establish "it
runs", never "it helps".

### EXPERIMENTALLY_TESTED
Measured in a controlled comparison (with vs. without, on defined tasks, with
a defined grader) in **one** experimental setting. Effect direction and size
are on record, with sample size stated.

### REPLICATED
The experimental effect held in at least one **independent** re-run: fresh
tasks, a different session, ideally a different operator. Replication is what
separates a result from an anecdote — a level we enforce because we have
watched our own single-run "wins" dissolve on re-test.

### PROMOTED
Passed all six promotion gates (below). Only PROMOTED mechanisms may be
described in public materials without an explicit evidence-level qualifier.

### NARROW
Real, replicated effect — but only in a bounded niche (one model family, one
task type, one configuration). Honest and shippable, with the boundary stated
wherever the capability is mentioned.

### REJECTED
Tested and found not to work, or to cause harm. Rejected mechanisms are
removed from the default path and their results preserved in
[NEGATIVE-RESULTS.md](../NEGATIVE-RESULTS.md). REJECTED is a result, not a
disgrace — a system that never rejects anything isn't measuring.

## Promotion gates

To move from REPLICATED to PROMOTED, a mechanism must pass **all six**:

| Gate | Question it answers |
|---|---|
| 1. Dev validation | Does it work in the environment where it was built, measured cleanly? |
| 2. Fresh held-out test | Does it work on tasks it has never seen, created after the mechanism was frozen? |
| 3. Regression | Does everything that worked before still work with it enabled? |
| 4. Cost | Is the improvement worth the tokens/latency/attention it consumes? Measured, not estimated. |
| 5. Negative transfer | Does it make anything *worse* — especially easy tasks and strong models? (Our most frequent real failure; see NR-1, NR-2.) |
| 6. Paired no-harm | In a paired comparison on already-correct work, does it abstain rather than damage? (NR-8 is why this gate exists.) |

A gate failure sends the mechanism back with the failure published. Gates are
evaluated on fresh data — re-using the data that motivated the mechanism
counts as gate 1, never gates 2–6.

## Demotion

Levels go down as well as up. A failed replication, a negative-transfer
report confirmed in the wild, or a grader defect discovered after the fact
demotes the claim, and the demotion is published with the same prominence as
the promotion. See the correction policy in [LAUNCH.md](../LAUNCH.md).

## How to read a claim

When a Fable Think document says a capability "works", the honest reading is
determined entirely by its level:

- DESIGNED — "we have a reasoned bet"
- SMOKE_TESTED — "it runs"
- EXPERIMENTALLY_TESTED — "it helped once, under these conditions"
- REPLICATED — "it helped more than once"
- PROMOTED — "it survived every way we know to attack it"
- NARROW — "it works *here*, and we've drawn the border"
- REJECTED — "it doesn't, and we've said so"

Current level assignments and their receipts: [EVIDENCE.md](../EVIDENCE.md).
