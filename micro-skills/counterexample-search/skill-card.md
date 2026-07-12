# counterexample-search — skill card

## What it does
Before a universal or impossibility claim ships ('always', 'never', 'all inputs', 'cannot happen'), it forces one bounded, executed counterexample attempt at the edges of the quantifier's domain. Claims that break are weakened to their true scope or the artifact is fixed; claims that survive carry a named strongest-case-tried, so the check is auditable.

## Trigger
- The task asks whether a property holds universally ('for all', 'in general', 'prove that', 'does it always').
- A draft asserts a universal or impossibility claim ('always', 'never', 'every', 'guaranteed', 'impossible', 'cannot happen').

## Counterindications
- The claim is already scoped to observations ('in the 30 cases tested', 'so far', 'in our data') — nothing universal is asserted.
- The property is definitional or machine-enforced (tautology, compiler-checked type guarantee) — a counterexample search is vacuous.
- Casual prose where the quantifier is rhetorical and nothing depends on it.

## Negative-transfer risk
Distraction risk: low. The failure mode is unbounded hunting — burning the session on exotic edge cases for low-stakes claims. The skill caps itself at one strongest candidate per claim, actually tested, then moves on.

## Evidence level
DESIGNED — specified from documented reasoning-failure modes; not yet executed as a packaged skill.
