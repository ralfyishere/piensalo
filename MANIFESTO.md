# The Fable Think Manifesto

Nine principles. Every design decision in this project traces back to one of
them, and every one of them was paid for by a measured failure.

## 1. Thinking should be inspectable

If you cannot see how a conclusion was reached, you cannot repair it when it is
wrong. Fable Think externalizes the cognitive program — objective, constraints,
decomposition, tests — so failure has a location, not just a vibe.

## 2. More prompting is not always better

Instructions compete for attention, and a "good" addition can dilute a proven
effect. We measured a larger prompt making a competent model *worse* at easy
tasks; since then, every always-on instruction must pay rent in evidence.

## 3. Repair should follow evidence

Fixing what you assume broke is how correct work gets destroyed. Inspection
identifies the failure layer first; only then does the smallest justified
repair get applied — never a rewrite when an edit suffices.

## 4. Verification is a separate capability

Re-reading your own work is not verification; it re-runs the same blind spots.
Verification independently re-derives the numbers, re-checks the claims, and is
allowed to return a verdict the author dislikes.

## 5. Abstention is intelligence

Knowing when *not* to intervene is as valuable as any repair. `NO REPAIR
NEEDED` is a first-class result in Fable Think, because in our measurements,
abstention beat intervention on already-competent work.

## 6. Negative results belong in public

A field that only publishes wins teaches everyone to repeat the same losses.
Our failures — regressions, routing bugs, grader artifacts — live permanently
in [NEGATIVE-RESULTS.md](NEGATIVE-RESULTS.md), stated plainly enough to save
you the experiment.

## 7. State should outlive a context window

Real work spans sessions, and evidence that evaporates with the context was
never really evidence. Fable Think persists programs, verdicts, and provenance
so the next action starts from what was established, not from re-derivation.

## 8. Models are replaceable; cognitive systems are portable

Any system welded to one model dies with that model's deprecation notice. The
skills layer is plain text that travels anywhere, and the runtime treats models
as declared, swappable components — with provenance recorded on every run.

## 9. Autonomy requires stronger controls, not weaker ones

The more an agent can do without you, the more it must be bounded, logged, and
interruptible. Loops carry budgets, destructive actions require approval, and
silent model fallback is prohibited — autonomy without controls is just
unsupervised risk.
