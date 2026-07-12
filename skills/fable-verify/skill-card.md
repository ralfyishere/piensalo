# Skill card: fable-verify

## What it does
Applies domain-appropriate verifier criteria (software, mathematics, research, strategy, invention, writing, generic) to any candidate answer and returns a per-criterion verdict table with disqualifiers surfaced first. It grades; it does not fix. Shell access is needed to execute deterministic checks where a criterion demands running something. Fully local: reads only its own bundled files and the user's task, sends nothing anywhere.

## Trigger
'verify this', 'is this answer right', 'review before we ship', 'grade this output'.

## Counterindications
- Drafts explicitly requested as rough - adversarial grading of a sketch wastes effort and discourages iteration.
- Trivial answers whose correctness is checkable in one step - a verdict table for "2+2=4" is ceremony.
- Environments with no tool access AND candidates whose criteria are all deterministic-executable - most criteria degrade to NOT-RUNNABLE-HERE and the review adds little.

## Negative-transfer risk
- Larger prompts can harm already-strong models: a model with good verification instincts may lose more to scaffold overhead than it gains.
- The verdict-table format can invite syntax-not-semantics compliance - table-shaped output whose probes were never actually run. The criteria themselves warn against this; graders must too.
- Applied to every answer indiscriminately, it doubles latency and can train a workflow to distrust cheap, obviously correct results.

## Evidence level
DESIGNED - see BENCHMARK.md. The micro-skills this domain skill composes carry their own evidence levels; the composed skill has not been executed as a packaged unit.
