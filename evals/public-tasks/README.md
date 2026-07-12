# Public tasks

Each subdirectory is one evaluation task:

```
<task-id>/
  task.md            # what the model sees (plus public-context/, if any)
  contract.json      # the machine-checkable output contract
  public-context/    # input files copied into the model's workspace
  hidden-grader/     # grade.py (layered verdict), KEY.md, meta.json
  probes/            # grader self-test battery + expected.json
```

"Hidden" means hidden **from the model's workspace** — the harness copies
only `task.md` and `public-context/` into the working directory of a run.
Everything is public to humans by design.

## Labels

- **DEVELOPMENT** (`dev-*`) — ported from an internal experiment where they
  were already consumed against frozen models. Publication contaminates any
  task forever: results on these tasks are for harness development,
  grader regression, and methodology demonstration — **never** for headline
  capability claims about models that may have trained on them.
- **DEMO** (`demo-*`) — authored fresh for this repository as worked
  illustrations of the three trap archetypes (math trap, planted
  contradiction, delivery contract). Same contamination caveat from the day
  they were published.

Headline claims require **private, unpublished task sets** run under the
same harness. See `evals/results/README.md` for the submission schema.

## Probe battery

Every task ships six probe classes (`probes/`), each with an expected
layered verdict in `expected.json`:

| Probe | Asserts |
|---|---|
| `clean-correct` | correct answer, exact contract -> layer `none` |
| `decorated-correct` | correct answer wrapped in Markdown -> cognition PASS, contract FAIL (decoration-masking guard) |
| `wrong-value` | well-formatted wrong answer -> layer `cognition` |
| `prose-trap` | mentions the task's numbers/scale without stating the answer -> cognition MUST NOT be credited (fallback-overreach guard) |
| `stall` | permission-stall shell -> cognition UNMEASURED, layer `delivery-incomplete` |
| `stub` | provider/API error text -> cognition UNMEASURED, layer `delivery-incomplete` |

Run `python3 evals/harness/grader_selftest.py` — it must exit 0 before any
run is graded.
