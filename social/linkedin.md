# LinkedIn launch post

*(Single post, professional register, no thread mechanics. Claims must match
EVIDENCE.md on launch day.)*

---

We just open-sourced Fable Think — a cognitive operating system for AI
models and agents.

The short version: most AI tooling optimizes for producing more output.
Fable Think optimizes for thinking better. It separates a task into distinct,
inspectable operations — understand the task, build a bounded cognitive
program, execute, inspect the result, classify the failure, apply the
smallest justified repair, verify independently, preserve the evidence, and
decide whether to continue or stop.

Three design decisions I'd highlight for anyone building with AI in
production:

**1. Abstention is a feature.** "NO REPAIR NEEDED" is a first-class result.
In our measured runs, intervening on already-correct work made outcomes worse
more often than better. A system that can't decline to act isn't safe to
automate.

**2. Every capability carries an evidence level.** From DESIGNED (a reasoned
bet, untested) through PROMOTED (survived validation, held-out testing,
regression, cost, negative-transfer, and no-harm gates). Some of our own
mechanisms are still DESIGNED-only — the documentation says exactly which.
We don't claim guaranteed improvement, because nobody honestly can.

**3. Negative results are published, permanently.** Oversized prompts that
degraded a competent model. A knowledge graph that regressed a weaker one.
A silent model fallback that corrupted attribution across an evidence base.
These are in the repo, in NEGATIVE-RESULTS.md, because a field that only
publishes wins teaches everyone to repeat the same losses.

It's MIT licensed, the core runs offline with zero telemetry, and the
portable skills layer works with any model — Claude, OpenAI-compatible APIs,
local models via Ollama, or plain copy/paste.

If your team is wrestling with AI reliability, the most useful thing you can
do is try to break it: reproduce our benchmark, test the abstention behavior,
and report any configuration where it makes results worse. Negative-transfer
reports are a first-class contribution and get published with credit.

Repo: github.com/fable-think/fable-think

Fable Think is an independent open-source project. It is not affiliated with
or endorsed by Anthropic.
