# Architecture

How Fable Think is put together, and why every seam exists.

## The one-paragraph version

Fable Think separates an AI task into distinct operations — understand, plan,
execute, inspect, classify, repair, verify, deliver — connected by a bounded
lifecycle and backed by persistent, inspectable state. Two layers implement
this: **portable Agent Skills** (plain text, run anywhere) and an **optional
runtime** (the `fable-think` CLI, which adds state, adaptivity, and
measurement). The runtime depends on nothing external; models attach through
declared adapters with recorded provenance.

## The lifecycle

```
user goal
  → recover actual intent
  → bounded cognitive program
  → execute
  → inspect observable result
  → identify failure layer
  → smallest justified repair
  → verify
  → preserve evidence + state
  → next action or stop
```

Two properties make this a lifecycle rather than a pipeline:

1. **It is bounded.** Repair cycles have budgets. A loop that can't converge
   stops and says so instead of burning tokens.
2. **It can end early, honestly.** Inspection may return `NO REPAIR NEEDED`;
   verification may return a verdict the rest of the system dislikes.
   Abstention and failure are recorded outcomes, not exceptions.

## The cognitive core

Eleven operations, each with a defined input, output, and failure mode:

| Operation | Consumes | Produces |
|---|---|---|
| `recover_objective` | raw goal | stated vs. actual objective |
| `identify_constraints` | objective + context | explicit constraint list |
| `decompose_problem` | objective + constraints | verifiable units |
| `locate_load_bearing_uncertainty` | decomposition | the unknown that invalidates the most downstream work |
| `select_cheapest_discriminating_test` | uncertainty | the cheapest check that can falsify it |
| `execute` | cognitive program | candidate result |
| `inspect_result` | observable output only | findings, each tagged with a layer |
| `classify_failure` | findings | failure layer assignment (objective / plan / numeric / routing / delivery / …) |
| `apply_targeted_repair` | classified failure | smallest justified change |
| `verify` | repaired result | independent re-derivation + verdict |
| `deliver` | verified result | output with evidence trail, or explicit abstention |

Design rules baked into the core:

- **Inspection sees only observable output** — never intentions, never the
  chain of thought that produced it. What can't be observed can't be graded.
- **Repair follows classification.** No fix is applied to an unclassified
  failure; "rewrite it all" is what happens when you skip this step.
- **Verification is independent.** It re-derives numbers and claims rather
  than re-reading the draft (re-reading re-runs the same blind spots).

## Layer 1: portable Agent Skills

Skills are plain instruction files with a required structure: observable
trigger, counterindications, bounded procedure, expected output, verification,
stop condition. They work in any agent that reads skill files — or pasted
manually into any chat. They carry no code, and the loader treats them as
inert text ([skill-security.md](skill-security.md)).

This layer is the portability guarantee: if the runtime disappeared tomorrow,
the skills would still work everywhere.

## Layer 2: the runtime

The CLI (`fable-think`, alias `fablethink`) adds what plain text cannot:

- **State** — programs, findings, verdicts, and evidence persist in
  `.fable-think/` and survive the context window (Manifesto, principle 7).
- **Bounded loops** — `loop` tracks budgets (repair cycles, steps) and
  reports used/remaining; exhausted budgets stop the loop visibly (a
  measured failure, NR-7, is why counters are surfaced).
- **Provenance** — every run records which model produced what;
  unavailability is a hard stop, never a silent substitution
  ([model-provenance.md](model-provenance.md)).
- **Measurement** — evidence hooks feed the evaluation harness in `evals/`.

### CLI modes → core operations

| Mode | Wraps |
|---|---|
| `think` | recover_objective → identify_constraints → decompose → locate uncertainty → select test → execute |
| `inspect` | inspect_result → classify_failure |
| `repair` | apply_targeted_repair |
| `verify` | verify |
| `loop` | the full lifecycle under a budget, resumable from state |
| `skill` | manage the skills layer: list, add, `scan`, remove |

## State layout

```
.fable-think/
  programs/     # cognitive programs, one file per task
  findings/     # inspection findings, layer-tagged
  evidence/     # verification records, provenance, verdicts
  loop.state    # budgets: used / remaining, surfaced in `loop` output
```

Everything is plain text, diff-able, and owned by the user. No hidden
persistence anywhere else on the machine ([SECURITY.md](../SECURITY.md)).

## Adapters

An adapter is the only place network can happen, and only when explicitly
configured. Each adapter declares: endpoint, model identity reporting, and
credential source (environment/keychain — never state files). The generic
command adapter pipes any CLI-invocable model through stdin/stdout for fully
offline or exotic setups.

## What the architecture refuses to include

- A generic "execute what the model said" path (tool escalation, T7)
- Code execution from skill text (T2)
- Silent model fallback (T9 / NR-6)
- Telemetry of any kind

These absences are architecture too — the load-bearing kind.
