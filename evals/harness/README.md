# Eval harness

Deterministic, reproducible condition-runner for the tasks in
`evals/public-tasks/`. One command, no API key, verifies the whole pipeline:

```
cd evals && make benchmark
```

That runs (1) the grader self-test battery (`grader_selftest.py`, must exit 0
— a battery that is not green is not evidence) and (2) a 2-task smoke run of
`runner.py --smoke` using the **manual adapter** with answers auto-populated
from probe files. The smoke run exercises workspace isolation, prompt
construction, second-pass pairing, the stub policy, grading, the consumption
ledger and analysis — it is a **plumbing test, not a benchmark**.

## Conditions

Each condition is a prompt-construction function in `runner.py`. First-pass
conditions build the whole prompt; second-pass conditions are paired on the
**same trial's `bare` draft** so deltas are paired, not cross-sectional.

| Condition | Pass | What it does |
|---|---|---|
| `bare` | 1 | task.md only — the baseline everything is paired against |
| `portable-skill` | 1 | prepends the portable skill (`assets.portable_skill`) |
| `minimal-core` | 1 | prepends the minimal core rules (`assets.minimal_core`) |
| `full-program` | 1 | prepends the full program (`assets.full_program`) |
| `output-guardian` | 2 | contract-only repair: fix format, change no values |
| `oracle-repair` | 2 | applies the task's `oracle_repairs` (from hidden-grader/meta.json) — the upper bound a perfect router could reach; abstains (reuses draft) when the oracle list is empty |
| `adaptive-repair` | 2 | the model self-routes: pick at most ONE repair from the micro-skill menu, or none |
| `verify-only` | 2 | independent re-derivation, no repair content |
| `no-repair-control` | 2 | placebo second pass ("restate your answer") — controls for the second-pass effect itself |

Interpretation guardrails: `oracle-repair` minus `adaptive-repair` is the
routing gap; any second-pass condition minus `no-repair-control` is the
effect beyond merely getting a second pass; harm on `competent-baseline`
tasks is negative transfer and must be reported per class, never averaged
away.

## Adapters

`adapter` in the config: `auto` tries, in order:

1. `piensalo` — `piensalo.adapters` if the package is installed;
2. `claude_cli` — `claude -p --output-format json --model <requested>`;
3. `manual` — prompts are written to `<run>/pending-prompts/<cell>.prompt.md`;
   you produce `<cell>.md` answers in an answers dir and re-run with
   `--answers-dir ... --run-id <same id>`. Works with any model or a human.

## Honesty mechanics

- **Model pinning**: the requested model id is recorded per cell, and the
  resolved model (when the backend reports one) alongside it. With
  `model.assert_resolved: true`, a mismatch marks the cell `MODEL_MISMATCH`
  and excludes it from statistics.
- **Stub policy**: provider/API-error/quota text is `NOT_RUN`, never a
  failure. Grading a stub as a wrong answer poisons every comparison.
- **Frozen graders**: SHA-256 digests of every grader and of
  `layered_common.py` go into `manifest.json` before the first cell runs.
- **Workspace isolation**: a task workspace contains ONLY `task.md` +
  `public-context/`. Graders, keys, probes and metadata never enter it.
- **Consumption ledger**: every run appends to
  `evals/results/consumption-ledger.json`. A task exposed to a model is
  consumed for that model family; DEVELOPMENT/DEMO tasks are additionally
  contaminated by publication itself (see `public-tasks/README.md`).
- **Repeated trials**: `trials` in the config; analysis reports paired
  deltas, within-task ranges, pass@k and pass^k (pass = score 100).

## A real run

```
cp harness/config.example.json harness/config.json   # edit model/conditions
python3 harness/runner.py                             # runs + grades + analyzes
python3 harness/analyze.py --run evals/results/runs/<id>   # re-analyze anytime
```

Outputs per run: `manifest.json`, `cells/*.md` (raw answers, retained),
`grades/*.json`, `meter.tsv`, `statuses.json`, `ANALYSIS.json`.
