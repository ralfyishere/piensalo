# X / Twitter launch thread

Rules: every claim must be defensible from EVIDENCE.md on launch day. No
"guaranteed", no vendor affiliation implications. Post 1 carries the hook;
post N carries the link + independence line.

---

**1/**
Most AI tooling makes models produce more.

We spent months making them think better — and publishing every time it
failed.

Fable Think: an open cognitive operating system for AI models and agents. 🧵

**2/**
It started as a preservation project: capture what a strong model does well
before access changes.

The obvious approach — write it all down, hand it to other models — failed
in ways we could measure.

**3/**
What actually happened in controlled runs:

· giant prompts made a competent model WORSE at easy tasks
· a full reasoning graph regressed a weak model
· a correct repair got erased by a routing bug
· correct answers got destroyed by output formatting

**4/**
Worst one: the runtime silently swapped models when one was unavailable.

Every measurement from that period attributed one model's behavior to
another. Plausible outputs, lying labels.

Silent fallback is now prohibited in Fable Think. Hard stop, loud error.

**5/**
The fix wasn't a better prompt. It was separation:

thinking ≠ inspection ≠ repair ≠ verification ≠ evidence ≠ continuation

Six CLI modes: think / inspect / repair / verify / loop / skill.
Each failure gets a layer. Each repair is the smallest justified change.

**6/**
The part we're proudest of: it knows when to do nothing.

"NO REPAIR NEEDED" is a first-class result. In our runs, abstention beat
intervention on already-correct work — so we made abstention a graded
capability, not a missing feature.

**7/**
Every capability ships with receipts. Explicit evidence levels:

DESIGNED → SMOKE_TESTED → EXPERIMENTALLY_TESTED → REPLICATED → PROMOTED
(+ NARROW and REJECTED, because honesty has terminal states)

Some of ours are still DESIGNED-only. The docs say which.

**8/**
And the failures stay published. NEGATIVE-RESULTS.md is a permanent file:
regressions, routing bugs, grader errors in both directions, the fallback
incident.

A field that only publishes wins teaches everyone to repeat the same losses.

**9/**
Portable by construction:

· Agent Skills = plain text, work in any agent, or copy/paste into any chat
· optional runtime adds state, bounded loops, provenance, measurement
· Claude / OpenAI-compatible / Ollama / any CLI command
· core runs offline, zero telemetry

**10/**
Honest limits, up front: the evidence base is young, n is small, one model
family is most-tested, and some mechanisms are unproven designs.

We will not claim guaranteed improvement. We'll show you the ledger instead.

**11/**
It's open source (MIT), and negative-result reports are a first-class
contribution — find a setup where it makes things worse and we'll publish
that with credit.

→ github.com/piensalo/piensalo

Fable Think is an independent open-source project. It is not affiliated
with or endorsed by Anthropic.
