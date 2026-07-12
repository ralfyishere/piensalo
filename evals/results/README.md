# Results

This directory holds run outputs (`runs/<run-id>/`, created by the harness),
the task-consumption ledger (`consumption-ledger.json`, appended by every
run), and community-submitted result files.

## What a submitted result must contain

A submission is a **pull request adding one JSON file** under
`results/submitted/`, named `<date>-<model>-<label>.json`, that validates
against `results-schema.json`. Required content, per the schema:

- **environment** — OS, harness git commit, adapter used, date.
- **model ids, requested AND resolved** — what you asked for and every model
  id the backend reported actually serving. "not_visible" is acceptable and
  is itself information.
- **task set + label** — `DEVELOPMENT`, `DEMO`, or `PRIVATE`. Published
  tasks (DEVELOPMENT/DEMO) are contaminated by publication: results on them
  are methodology/regression evidence only. **Only PRIVATE (unpublished)
  task sets run under this harness are eligible for headline claims**, and
  they must ship grader SHA-256 digests plus `grader_selftest_pass: true`.
- **per-cell rows** — task, condition, trial, status, layered outcome.
  NOT_RUN/PENDING/MODEL_MISMATCH cells stay in the file; they are excluded
  from stats but their count is part of the result.
- **raw retention policy** — where the per-cell raw model outputs live
  (`retained-private`, `retained-public-link`, or `not-retained`).
  Not-retained submissions are accepted but flagged unverifiable.
- **variance** — number of trials and within-task ranges. At small n,
  report direction, not certainty.

Validate before opening the PR:

```
python3 -c "import json, jsonschema; jsonschema.validate(
    json.load(open('your-result.json')),
    json.load(open('evals/results/results-schema.json')))"
```

(`pip install jsonschema` if needed.)

## What gets a submission rejected

- Grading performed with a battery whose `grader_selftest.py` was not green.
- Stubs/API errors counted as model failures.
- Headline claims from DEVELOPMENT or DEMO tasks.
- Cross-sectional comparisons where paired ones were possible (second-pass
  conditions must be paired against the same trial's bare draft).
- Aggregates without the per-cell rows that produced them.
