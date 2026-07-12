# Operator Boundaries

What Fable Think will and will not do without you. These boundaries are
enforced by the runtime, verified by `fable-think doctor`, and treated as
security invariants — a release that weakens one is a security bug
([SECURITY.md](../SECURITY.md)).

## The principle

Autonomy requires stronger controls, not weaker ones (Manifesto, principle 9).
The more the system can do in a loop without a human, the harder its
boundaries must be. Fable Think's answer is a fixed, small action surface
with explicit approval gates.

## Always allowed (no approval)

- Reading files inside the workspace
- Writing inside `.fable-think/` (programs, findings, evidence, loop state)
- Producing drafts, verdicts, and reports as *output text*
- Calling the configured model through the configured adapter

## Requires explicit approval, every time

| Action | Why gated |
|---|---|
| Deleting or overwriting files outside `.fable-think/` | Destructive; the repair philosophy is smallest-change, and destroying user files is never the smallest change |
| Sending anything (mail, messages, API posts beyond the model call) | Crossing from "thinking" into "acting on the world" |
| Deploying, publishing, pushing | No auto-publish, ever — publication is a human decision |
| Running shell commands proposed by model output or skill text | There is no generic execute path; anything resembling one goes through you |
| Spending money or changing credentials | Obvious, and stated anyway |

Approval is per-action and visible: the runtime shows exactly what would
happen before it happens. There is no "yes to all" flag in 0.1.x, by design.

## Never, regardless of approval

- Telemetry or any phone-home behavior
- Silent model fallback ([model-provenance.md](model-provenance.md))
- Writing state outside `.fable-think/` or the explicitly configured root
- Logging secrets
- Executing code found inside skill files ([skill-security.md](skill-security.md))

## Loops

`fable-think loop` runs the lifecycle autonomously *within* these boundaries,
plus its own:

- **Budgets** — repair cycles and steps are bounded; used/remaining is
  printed every iteration and persisted. Exhausted budget = visible stop.
- **No boundary accumulates.** Ten loop iterations have exactly the same
  action surface as one; approval requirements never decay with repetition.
- **Interruptible and resumable** — state is preserved at every step, so
  stopping a loop loses nothing (`loop --continue` resumes from evidence).

## Checking the boundaries

```bash
fable-think doctor          # verifies defaults are intact
fable-think doctor --strict # also fails on any user config that widens the surface
```

If `doctor` reports a widened boundary you didn't configure, treat it as a
compromise and report it ([SECURITY.md](../SECURITY.md)).
