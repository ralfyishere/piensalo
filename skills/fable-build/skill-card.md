# Skill card: fable-build

## What it does
Drives debugging and careful implementation to a confirmed root cause, a minimal in-scope fix, and quoted regression evidence. Shell / test-runner access is strongly recommended - the reproduction and regression steps quote real output. Fully local: reads only its own bundled files and the user's task, sends nothing anywhere.

## Trigger
'fix this bug', 'tests are failing', 'why is this crashing', 'implement X without breaking Y'.

## Counterindications
- Code that cannot be run or tested - pure code-reading tasks lose the reproduction and regression steps, which carry most of the skill's value.
- Trivial one-line changes with an obvious cause and no regression surface - the full loop adds latency for no gain.
- Greenfield exploration where nothing is broken yet.

## Negative-transfer risk
- Larger prompts can harm already-strong models: a model that already debugs systematically may lose more to attention dilution than it gains from the scaffold.
- The evidence-table and quoted-output requirements can push a model toward performative compliance (producing table-shaped output without a real discriminating test) - grade substance, not shape.

## Evidence level
DESIGNED - see BENCHMARK.md. The micro-skills this domain skill composes carry their own evidence levels; the composed skill has not been executed as a packaged unit.
