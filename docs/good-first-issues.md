# Good First Issues

Five well-scoped entry points. Each lists what done looks like, so you can
self-check before opening the PR. General rules:
[CONTRIBUTING.md](../CONTRIBUTING.md).

## 1. Write a verifier: unit-consistency check

**What:** an `inspect`/`verify` checker that flags when a draft mixes units
or currencies without conversion ($100/mo vs. annual totals, %, absolute).

**Done means:** detects the defect class in the provided fixture drafts;
includes at least one adversarial fixture designed to fool it (e.g. a correct
mixed-unit sentence it must NOT flag); false-positive/false-negative behavior
stated in the PR.

**Skills needed:** Python, care. No ML.

## 2. Reproduce the demo lifecycle on a local model

**What:** run the README pricing demo end-to-end (think → inspect → repair →
verify) through the Ollama adapter with any local model, and write up what
actually happened — including if it went badly.

**Done means:** a case-study issue filed with exact model tag, provenance
records, and the full evidence bundle. An unfavorable result is a **pass**
for this issue — we need the data, not the flattery.

## 3. Add a near-miss example to an existing skill

**What:** every skill needs a documented near miss — a situation that *looks*
like its trigger but isn't. Several shipped skills have thin near-miss
sections. Pick one, write a realistic near miss, and explain why the skill
must not fire.

**Done means:** the near miss is concrete (a real-looking input, not a
category description), the counterindication logic references it, and the
skill still passes `fable-think skill scan` and skill lint.

## 4. Harden `skill scan` against one obfuscation trick

**What:** pick one evasion from [skill-security.md](skill-security.md)
(zero-width characters, homoglyphs, base64 fragments split across lines) and
add detection for it.

**Done means:** a failing test written *first* demonstrating the evasion
passing the current scanner; the rule; the test now passing; and — required —
one test showing a benign skill that superficially resembles the pattern is
NOT flagged. Guards that overfire get disabled by users, which is worse than
no guard.

## 5. Write the "manual mode" walkthrough

**What:** a doc showing the full lifecycle with **no runtime at all** — pure
copy/paste of the portable skills into any chat model: what to paste, in what
order, and how to keep a paper evidence trail by hand.

**Done means:** a newcomer with only a browser chat can follow it end-to-end;
each lifecycle stage maps to a specific paste; the provenance habit
(state your model in the artifact, per
[model-provenance.md](model-provenance.md)) is included; tested by someone
other than the author.

---

Claim an issue by commenting on it. Stuck for more than an hour on setup?
That's a documentation bug — please report where you got stuck; the report
is a contribution by itself.
