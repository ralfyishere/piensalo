# Skill card: piensalo

## What it does
Runs any hard task through a minimal deep-reasoning loop - objective recovery, constraint/contradiction extraction, distinct mechanisms, cheapest discriminating test, adversarial verification - and returns a calibrated answer with residual uncertainty. No required tools; a code/calculation tool improves the adversarial-verification step when claims are numeric. Fully local: reads only its own bundled files and the user's task, sends nothing anywhere.

## Trigger
'think this through', 'get this right', 'hard problem', or any multi-constraint ask where being confidently wrong is expensive.

## Counterindications
- Trivial tasks whose answer is deterministic and checkable in one step - the loop adds latency for no gain.
- Tasks with a single obvious mechanism and no real uncertainty - the multi-candidate and discriminating-test steps become ceremony.
- Time-critical single-fact lookups.

## Negative-transfer risk
- Larger prompts can harm already-strong models: the extra scaffolding competes for attention with the task itself and can dilute an otherwise good direct answer.
- On small tasks the output contract (confidence per component, residual uncertainty) can read as hedging and reduce answer usability.
- Observed gains are entangled with model capability: the same prompt that lifts a mid-capability model can be neutral or negative on a stronger one.

## Evidence level
NARROW - see BENCHMARK.md. Highest mean in one controlled run, but the result is run-specific and confounded; no general win is claimed.
