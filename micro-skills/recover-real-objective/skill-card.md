# recover-real-objective — skill card

## What it does
When a request arrives solution-shaped ("increase the timeout") or vague ("fix it"), this skill recovers the objective behind it before executing literally: one line quoting the literal ask, one line stating the most plausible underlying objective, an explicit check of whether the literal action serves that objective, and a named divergence if it doesn't. The interpretation is always surfaced so the user can veto it.

## Trigger
- The request names a knob or parameter change instead of an outcome ("bump the retries", "double the buffer", "set workers to 8").
- A vague referent with no stated goal ("fix it", "improve this", "clean that up", "speed it up").
- An oddly specific micro-instruction with missing context ("just change X").
- A draft executes the literal request without stating what objective the change serves.

## Counterindications
- The request already carries its objective ("so that...", "because...", "the goal is...", explicit acceptance criteria) — decoding adds noise.
- Single-fact lookups with no optimization target.
- The literal action and the plausible objective are obviously identical.

## Negative-transfer risk
Over-interpretation: inventing an objective the user never had and drifting away from the literal ask — the failure this skill guards against, inverted. Mitigation built into the procedure: the literal request stays the default action, the interpretation is stated rather than silently substituted, and questions are asked only when a wrong guess is expensive. Distraction risk is low (≤150 added tokens, no tool calls).

## Evidence level
SMOKE_TESTED — executed end-to-end in live sessions and behaves as specified; no measured lift is claimed.
