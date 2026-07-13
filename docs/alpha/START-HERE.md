# PIÉNSALO — Alpha Start Here

Welcome. You're testing **Piénsalo** — an open cognitive operating layer
that helps AI models recover the real objective, inspect their own output,
repair specific failures, verify results, and know when to leave good work
alone. Its signature behavior is honest restraint: **NO INTERVENTION
NEEDED** is a first-class result.

PIÉNSALO is a public alpha: https://github.com/ralfyishere/piensalo — share
the link freely; structured feedback is what we ask for in return.

## 1 — Install (5 minutes, offline)

Requires Python 3.10+. Then either:

```bash
# with uv (recommended)
uv sync
uv run piensalo doctor

# or plain pip, in a venv
python3 -m venv .venv && . .venv/bin/activate
pip install .
piensalo doctor
```

`doctor` checks your environment and confirms: no network is used, no
telemetry exists, nothing leaves your machine.

## 2 — Run the flagship demo (2 minutes)

```bash
uv run piensalo think examples/math/task.md
uv run piensalo inspect --task examples/math/task.md --draft examples/math/bare-output.md
```

The first command compiles a bounded "cognitive program" for the task. The
second inspects a flawed draft, names the observable defect, and selects
the smallest justified repair — or tells you no repair is needed.

## 3 — Test it on ONE real task of yours (15-30 minutes)

Pick something real: a calculation-heavy email, a spec with constraints, a
research summary, a piece of code review prose. Then:

1. Get a draft from any model you normally use (or write one).
2. `uv run piensalo inspect --task your-task.md --draft your-draft.md`
3. Judge for yourself: did the inspection find something real, invent a
   problem, or correctly abstain?

That judgment — helped / harmed / abstained-correctly / abstained-wrongly —
is exactly what we need. There are no wrong answers; **"it correctly did
nothing" is a success report**, and "it invented a problem" is one of the
most valuable reports you can file.

## 4 — Report (5 minutes)

Fill the structured form: `public-export/ALPHA-TESTER-INSTRUCTIONS.md`
walks you through it; the schema is `ALPHA-FEEDBACK-SCHEMA.json`. Send it
back through whatever private channel you received this repo from.

## What Piénsalo is not

Not a model. Not a guarantee of correctness. Not affiliated with or
endorsed by Anthropic. The evidence behind every mechanism — including the
negative results — is in [EVIDENCE.md](../../EVIDENCE.md) and
[NEGATIVE-RESULTS.md](../../NEGATIVE-RESULTS.md).
