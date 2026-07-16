# PIÉNSALO

## Give any AI a better way to think.

**The open artificial cortex for AI.** *Use less context. Lose none of the
intelligence.*

PIÉNSALO selects the smallest context required for the current task, runs
the AI model you choose, verifies whether the response still satisfies the
task, expands the context when information is missing, and safely falls
back to full context when optimization would be unsafe.

Created by [Rafael “Ralph” Peña](https://github.com/ralfyishere).
Piénsalo — "think it through." Pronounced: pee-EN-sa-lo.

> **Status: public alpha.** Tested runtime, packaging, and evaluation
> harness. Live experimental evidence is from one Claude-family model;
> independent replication and cross-model validation are pending — in
> public.

## What PIÉNSALO does

One cortex, three systems, all model-independent and offline-first:

- **CONTEXT** — cut context tokens, verify the answer, expand when needed,
  fall back safely. *(The sharpest wedge — start here.)*
- **THINK** — compile a hard task into a bounded cognitive program before
  any model runs.
- **CHECK** — inspect a draft for observable defects, repair only what is
  demonstrably wrong, verify what can honestly be verified, and abstain
  when intervention would cause harm.

## Measured, not promised

Initial preregistered evaluation — 8 paired full-context vs
optimized-context tasks, graders frozen before any model run
([evals/context-optimizer/](evals/context-optimizer/), results committed):

```
Median context reduction:          80.2%
Median runtime net input savings:  76.9%
Optimizable tasks maintained:      7/7
Deterministic regressions:         0
Unsafe compression cases:          1 (by design)
Correct safe fallbacks:            1/1
```

Scope of that claim, stated plainly: **one Claude-family model**
(`claude-haiku-4-5-20251001`) · **eight preregistered tasks** · **single
samples** · **deterministic task requirements** (output contract +
exact-content oracle) · **broader behavioral equivalence remains
unmeasured**. A smaller prompt is not automatically a better one — that is
why verification and fallback exist.

## Install

```bash
# Fastest first run (no install)
uvx piensalo doctor

# Persistent install
pipx install piensalo

# Straight from GitHub
uvx --from git+https://github.com/ralfyishere/piensalo piensalo doctor
```

`doctor` verifies your environment and confirms the core runs fully offline
— no telemetry, no network, nothing leaves your machine. Python ≥ 3.10;
tested in CI on Linux and macOS, Python 3.10–3.13 (Windows unsupported for
now).

<details>
<summary>Development clone and portable Agent Skills</summary>

```bash
# From a clone (development)
git clone https://github.com/ralfyishere/piensalo.git && cd piensalo
uv sync && uv run piensalo doctor

# Portable Agent Skills only (no runtime needed)
npx skills add ralfyishere/piensalo
```

</details>

## The 60-second Context Optimizer demo

```bash
git clone https://github.com/ralfyishere/piensalo.git && cd piensalo
./examples/context-optimizer/launch-demo.sh
```

Offline, no API key: it optimizes a real chatter-heavy engineering context
live (deterministic, reproduced on your machine), shows exactly what was
kept and omitted and why, then replays the committed recorded model
comparison — full context vs optimized context, same task, same grader —
ending in a **MAINTAINED** verdict at a fraction of the tokens, plus the
designed unsafe case being **refused** instead of truncated. Every line is
labeled as live-deterministic or recorded; the full captured output is
committed at
[examples/context-optimizer/LAUNCH-TRANSCRIPT.md](examples/context-optimizer/LAUNCH-TRANSCRIPT.md)
and an anti-drift test fails CI if the script and transcript ever diverge.

## How optimization works

```
TASK
  → FULL AVAILABLE CONTEXT      (text, JSONL, chat JSON, tool logs, files)
  → CHUNK + CLASSIFY            (explicit structure honored exactly once)
  → PRESERVE MANDATORY CONTEXT  (constraints, exact ids, stop conditions …)
  → RANK OPTIONAL CONTEXT       (inspectable per-chunk score, never opaque)
  → BUILD BUDGETED PACKET       (over-budget mandatory ⇒ REFUSED, not cut)
  → RUN THE TARGET MODEL        (explicit adapter only; provenance pinned)
  → VERIFY THE RESPONSE         (contract + exact-content oracle)
  → ACCEPT, EXPAND, OR FALL BACK
```

Every chunk gets a disposition with a reason in
`selection-manifest.json` — `INCLUDED_MANDATORY`, `INCLUDED_RELEVANT`,
`OMITTED_DUPLICATE`, `OMITTED_SUPERSEDED`, `OMITTED_LOW_RELEVANCE`,
`OMITTED_REGENERABLE`, `REFERENCED_NOT_INLINE`, `REQUIRES_EXPANSION` — so
you can audit exactly why anything was kept or left out. Context needed to
fix CI is not the context needed to write launch copy: packets are compiled
per task, not per project.

## Safe expansion and fallback

Verification failure is never silently returned as success:

1. optimized attempt → deterministic verification
2. failed? add the highest-value omitted chunks (bounded, default 2
   rounds, every added chunk recorded)
3. still failing? **SAFE FALLBACK** — run or recommend the full context,
   ledgered as a fallback, never counted as an optimized win
4. mandatory context alone over budget? **OPTIMIZATION REFUSED — FULL
   CONTEXT REQUIRED.** Critical information is never truncated.

The token ledger separates source, optimized, expansion, fallback, and
benchmark-only baseline costs — compression that costs more than it saves
is reported as exactly that.

## THINK — structure difficult work

`piensalo think` compiles a task (file or inline text) into a bounded
cognitive program before any model runs; `piensalo loop` keeps long-running
work resumable with model provenance; `piensalo skill` manages 27 portable
skill packages ([skills/](skills/) + [micro-skills/](micro-skills/)) that
install into any agent speaking Agent Skills.

## CHECK — inspect, repair, verify, abstain

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
- Silent model fallback is prohibited by design: adapters record requested
  and resolved model and stop on mismatch.

### 60 seconds of CHECK, for real

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

## CONTEXT — the full command surface

```sh
# offline + deterministic: capsule / packet construction
piensalo context compile transcript.txt --goal "continue" --budget 3000 --output out/
piensalo context optimize --task task.md --context session.jsonl --budget 4000 --output opt/

# inspect / verify / diff what was compiled
piensalo context inspect out/
piensalo context verify out/
piensalo context diff out-v1/ out-v2/

# explicit-adapter execution with verification, bounded expansion, safe fallback
piensalo context run --task task.md --context session.jsonl --budget 4000 \
  --adapter claude-cli --model <model> --contract contract.json --output run/

# paired full-vs-optimized evidence run (benchmark cost ledgered separately)
piensalo context evaluate --task task.md --context session.jsonl \
  --adapter claude-cli --model <model> --budgets 2000,4000 --output eval/
```

`compile` turns long transcripts into deterministic **Continuation
Capsules**: typed consequence records, active vs superseded decisions,
exactness classes, content-addressed source references, byte-stable
serialization, honest budget refusal — and behavioral equivalence reported
**UNMEASURED**, because structural verification does not prove a resumed
model behaves identically. Deterministic capsule demo:
[examples/context/](examples/context/).

## Cortex Gateway — observe mode (new, on `cortex-gateway`)

PIÉNSALO can sit **between the AI tools you already use and the model you
choose**. The first delivery mode is `observe`: it forwards your traffic
**unchanged**, runs the **Cortex Router** in *shadow* to record what THINK,
CHECK, or CONTEXT *would* do, and writes a local, redact-by-default event
ledger. It does **not** modify responses and makes **no** performance claim —
it is a pass-through + measurement surface.

```sh
# in front of any OpenAI-compatible upstream (local model, LM Studio, Ollama, OpenRouter, …)
piensalo serve --mode observe \
  --upstream-base-url http://127.0.0.1:11434/v1 --upstream-model <id>

# what would the cortex have done? (shadow only — nothing was intervened on)
piensalo gateway report
piensalo gateway inspect --last 20
```

Loopback-only by default, SSRF-guarded upstream, bearer-auth optional, no body
retention. Try it with **zero credentials** via the offline demo:
[examples/gateway/](examples/gateway/) · design:
[docs/gateway/ARCHITECTURE.md](docs/gateway/ARCHITECTURE.md). Intervention modes
(`optimize-safe`, `verified`) are DESIGNED, not yet implemented.

## Evidence and limitations

**Every capability ships with receipts.** Two pre-registered 120-cell
controlled runs sit behind the CHECK defaults — including the finding that
forced repair on already-correct drafts *damages* delivery ~29% of the time
while never corrupting cognition. That is why abstention is the default
posture. The Context Optimizer numbers above come from one pre-registered
paired run with committed artifacts.

- [EVIDENCE.md](EVIDENCE.md) — mechanism records with maturity levels
  (DESIGNED → … → PROMOTED, with NARROW and REJECTED as honest terminal
  states; nothing is PROMOTED yet)
- [BENCHMARKS.md](BENCHMARKS.md) — run designs and numbers, confounds attached
- [NEGATIVE-RESULTS.md](NEGATIVE-RESULTS.md) — the failures we keep public on purpose
- Reproduce: `make benchmark` (no API key needed) · full harness in [evals/](evals/)
- Current limits, honestly: one model family live-tested (Claude); n = 8
  tasks per run; single samples; OpenAI-compatible/Ollama adapters are
  unit-tested with live validation pending; no independent reproduction
  yet. Help change that:
  [docs/alpha/SUBMIT-RESULTS.md](docs/alpha/SUBMIT-RESULTS.md).

## Security

Offline by default; no telemetry; no shell execution from untrusted skill
text; skill packages scannable with `piensalo skill scan`. Threat model:
[docs/THREAT-MODEL.md](docs/THREAT-MODEL.md). Sensitive reports: GitHub
Private Vulnerability Reporting ([SECURITY.md](SECURITY.md)).

## Contributing

Real-task results are the most valuable contribution — all outcomes,
including "it correctly did nothing", "it fell back correctly", and "it
invented a problem". File one in two minutes with the
[real task result form](https://github.com/ralfyishere/piensalo/issues/new?template=real-task-result.yml);
installation trouble goes in the
[installation form](https://github.com/ralfyishere/piensalo/issues/new?template=installation-problem.yml).
Details: [docs/alpha/SUBMIT-RESULTS.md](docs/alpha/SUBMIT-RESULTS.md).
Code, skills, verifiers, adapters: [CONTRIBUTING.md](CONTRIBUTING.md) —
every contribution meets the same evidence and security bar. Principles:
[MANIFESTO.md](MANIFESTO.md).

## Creator

PIÉNSALO was created by
[Rafael “Ralph” Peña](https://github.com/ralfyishere).

It began as an attempt to preserve and transfer powerful AI problem-solving
behavior. The experiments showed that larger prompts alone were not enough:
some interventions helped, while others overloaded weaker models, damaged
correct delivery, routed incorrectly, or created false confidence. Watching
agents re-spend enormous context on history they no longer needed led to
the Context Optimizer: not another summarizer, but a system that removes
context, tests the resulting answer, restores information when needed, and
refuses optimization when it could cause harm.

PIÉNSALO was built from the mechanisms that survived the evidence — the full
story is in [docs/origin-story.md](docs/origin-story.md).

*Think through hard work. Verify what matters. Know when to stop.*

Piénsalo is an independent open-source project. It is not affiliated with or
endorsed by Anthropic.
