# PIÉNSALO

## Give any AI a better way to think.

**The open artificial cortex for AI.**

PIÉNSALO is a model-independent cognitive operating system that helps AI
models and agents understand the real objective, structure difficult work,
inspect their output, repair specific failures, verify the result, know when
not to intervene, preserve evidence, and continue across sessions.

Created by [Rafael “Ralph” Peña](https://github.com/ralfyishere).
Piénsalo — "think it through." Pronounced: pee-EN-sa-lo.

> **Status: public alpha.** The runtime, portable skills, packaging,
> evaluation harness, and core verification workflows are tested. Current
> live experimental evidence is primarily from the Claude model family;
> cross-model validation, independent reproduction, and real-world case
> studies are expanding in public.

**The wedge, in one sentence:** give PIÉNSALO a task and an AI's draft — it
finds what was actually missed, leaves correct work alone, emits the
smallest justified repair when one is warranted, verifies what can honestly
be verified, and says **NO REPAIR NEEDED** when intervention would only
cause harm.

## 60 seconds, for real

Every line below is real output from the shipped CLI — the transcript is
committed at [examples/flagship/TRANSCRIPT.md](examples/flagship/TRANSCRIPT.md)
and a CI test re-runs the demo and fails if this ever drifts.

A quote task applies two sequential discounts (20%, then 15%). The AI draft
added them (35% off → $221.00) instead of compounding (→ $231.20):

```text
$ piensalo inspect --task examples/flagship/task.md \
    --draft examples/flagship/draft-broken.md \
    --contract examples/flagship/contract.json
selected repair(s): rederive-the-numbers
  evidence: asserts a figure with no visible derivation on a multi-rate task

$ piensalo verify --task examples/flagship/task.md \
    --draft examples/flagship/draft-broken.md \
    --contract examples/flagship/contract.json
FAILED
  QUOTE_USD: 221.00 != expected 231.20
[exit: 1]
```

`piensalo repair` then emits a **repair packet** — the complete, ready-to-run
prompt for your model, honestly labeled: *"instructions for a model; nothing
has been applied."* (With `--adapter`, it runs the packet through a model you
explicitly choose, writes the repaired draft to a **new** file with a
provenance sidecar, and re-inspects the result — it never claims success just
because a model returned text.)

And on a draft that is already right:

```text
$ piensalo inspect --task examples/flagship/task.md \
    --draft examples/flagship/draft-correct.md \
    --contract examples/flagship/contract.json
NO REPAIR NEEDED — no observable defect cleared the activation threshold.

$ piensalo verify --task examples/flagship/task.md \
    --draft examples/flagship/draft-correct.md \
    --contract examples/flagship/contract.json
DETERMINISTICALLY VERIFIED
  QUOTE_USD: 231.20 == expected
CONTRACT VERIFIED
UNMEASURED
  cognition: UNMEASURED (no verifier configured — this is not a pass)
```

Run the whole thing yourself: `bash examples/flagship/demo.sh`

## Install

```bash
# From PyPI
uvx piensalo doctor
pipx install piensalo

# Directly from GitHub
uvx --from git+https://github.com/ralfyishere/piensalo piensalo doctor

# From a clone (development)
git clone https://github.com/ralfyishere/piensalo.git && cd piensalo
uv sync && uv run piensalo doctor

# Portable Agent Skills only (no runtime needed)
npx skills add ralfyishere/piensalo
```

`doctor` verifies your environment and confirms the core runs fully offline
— no telemetry, no network, nothing leaves your machine. Python ≥ 3.10;
tested in CI on Linux and macOS, Python 3.10–3.13 (Windows unsupported for
now).

## How the workflow behaves

```
TASK → DRAFT → INSPECT → ABSTAIN or TARGETED REPAIR → VERIFY → FINAL ARTIFACT
```

- **inspect** detects observable defects with evidence lines — never vibes.
- **repair** has two honest modes: offline (emit the packet) or
  adapter-backed (`--adapter claude-cli|openai|ollama|manual`, `--model`,
  `--output`) — original draft preserved, provenance recorded, result
  re-inspected.
- **verify** reports in five strict buckets — `DETERMINISTICALLY VERIFIED`,
  `CONTRACT VERIFIED`, `MODEL-ASSISTED CHECK`, `UNMEASURED`, `FAILED` — and
  UNMEASURED never counts as a pass.
- **think** compiles a task (file or inline text) into a bounded cognitive
  program; **loop** keeps long-running work resumable with model provenance;
  **skill** manages the portable skill packages.
- Silent model fallback is prohibited by design: adapters record requested
  and resolved model and stop on mismatch.

## Use less context. Lose none of the intelligence.

`piensalo context` turns long transcripts and chatter-heavy project context
into the smallest task-specific packet that preserves decisions (with
supersession), constraints, failed approaches, exact identifiers, and stop
conditions — then verifies the model's response deterministically and
expands or falls back when verification fails.

```sh
# offline + deterministic: capsule / packet construction
piensalo context compile transcript.txt --goal "continue" --budget 3000 --output out/
piensalo context optimize --task task.md --context session.jsonl --budget 4000 --output opt/

# explicit-adapter execution with verification, bounded expansion, safe fallback
piensalo context run --task task.md --context session.jsonl --budget 4000 \
  --adapter claude-cli --model <model> --contract contract.json --output run/

# paired full-vs-optimized evidence run (benchmark cost ledgered separately)
piensalo context evaluate --task task.md --context session.jsonl \
  --adapter claude-cli --model <model> --budgets 2000,4000 --output eval/
```

Measured, not promised — on the pre-registered 8-task suite
([evals/context-optimizer/](evals/context-optimizer/), graders frozen
before any run, `claude-haiku-4-5-20251001`, single samples): median gross
context reduction **80.2%**, median runtime net input savings **76.9%**,
7/7 optimizable tasks **MAINTAINED** every deterministic requirement with
zero regressions, and the designed uncompressible task **refused
optimization and fell back safely**. A committed demo run
([examples/context-optimizer/](examples/context-optimizer/)) passes all
seven requirements from a packet 66% smaller than the full prompt
(**MAINTAINED**, single sample). Scope honestly: one model family,
deterministic graders, chatter-heavy contexts — broader behavioral
equivalence is UNMEASURED, and a task that needs full context gets full
context.

## Why trust it

**Every capability ships with receipts.** Two pre-registered 120-cell
controlled runs sit behind the defaults — including the finding that forced
repair on already-correct drafts *damages* delivery ~29% of the time while
never corrupting cognition. That is why abstention is the default posture.

- [EVIDENCE.md](EVIDENCE.md) — mechanism records with maturity levels
  (DESIGNED → … → PROMOTED, with NARROW and REJECTED as honest terminal
  states; nothing is PROMOTED yet)
- [BENCHMARKS.md](BENCHMARKS.md) — run designs and numbers, confounds attached
- [NEGATIVE-RESULTS.md](NEGATIVE-RESULTS.md) — the eight failures we keep public on purpose
- Reproduce: `make benchmark` (no API key needed) · full harness in [evals/](evals/)
- Current limits, honestly: one model family live-tested (Claude); n = 8
  tasks per run; OpenAI-compatible/Ollama adapters are unit-tested with live
  validation pending; no independent reproduction yet. Help change that:
  [docs/alpha/SUBMIT-RESULTS.md](docs/alpha/SUBMIT-RESULTS.md).

## Going deeper

- 27 portable skill packages: [skills/](skills/) (8 domain) +
  [micro-skills/](micro-skills/) (19 focused repairs) — each with triggers,
  counterindications, an evidence level, and a near-miss example; installable
  into any agent that speaks Agent Skills.
- The cognitive core (11 operations, human- and machine-readable):
  [src/piensalo/core/](src/piensalo/core/)
- Architecture, methodology, evidence levels: [docs/](docs/) · export
  provenance and hash manifest: [docs/provenance/](docs/provenance/)

## Security

Offline by default; no telemetry; no shell execution from untrusted skill
text; skill packages scannable with `piensalo skill scan`. Threat model:
[docs/THREAT-MODEL.md](docs/THREAT-MODEL.md). Sensitive reports: GitHub
Private Vulnerability Reporting ([SECURITY.md](SECURITY.md)).

## Contributing

Real-task results are the most valuable contribution — all five outcomes,
including "it correctly did nothing" and "it invented a problem":
[docs/alpha/SUBMIT-RESULTS.md](docs/alpha/SUBMIT-RESULTS.md). Code, skills,
verifiers, adapters: [CONTRIBUTING.md](CONTRIBUTING.md) — every contribution
meets the same evidence and security bar. Principles:
[MANIFESTO.md](MANIFESTO.md).

## Creator

PIÉNSALO was created by
[Rafael “Ralph” Peña](https://github.com/ralfyishere).

It began as an attempt to preserve and transfer powerful AI problem-solving
behavior. The experiments showed that larger prompts alone were not enough:
some interventions helped, while others overloaded weaker models, damaged
correct delivery, routed incorrectly, or created false confidence.

PIÉNSALO was built from the mechanisms that survived the evidence — the full
story is in [docs/origin-story.md](docs/origin-story.md).

*Think through hard work. Verify what matters. Know when to stop.*

Piénsalo is an independent open-source project. It is not affiliated with or
endorsed by Anthropic.
