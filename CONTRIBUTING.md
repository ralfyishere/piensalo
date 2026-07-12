# Contributing to Piénsalo

Contributions are welcome — and negative results are as welcome as features.
This document tells you what kinds of contributions exist, what evidence each
one needs, and what will get a PR declined.

## Ground rules

1. **Evidence standards apply to everyone,** maintainers included. A
   capability claim needs an evidence level
   ([docs/evidence-levels.md](docs/evidence-levels.md)); "it seemed better"
   is not a level.
2. **Security defaults are invariant.** No PR may add telemetry, network
   access outside explicit adapters, silent fallback, or code execution from
   skill text ([SECURITY.md](SECURITY.md)). Such PRs are declined regardless
   of the feature attached to them.
3. **No unreviewed prompt marketplace.** We do not merge skill dumps,
   auto-generated skill collections, or "100 prompts" packs. Every skill is
   reviewed individually against the checklist below.
4. **One concern per PR.** Small, reviewable, with the verification you ran
   quoted in the PR description.
5. Be excellent to each other — [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Contribution types

### 1. Skills

The highest-leverage contribution. Open a
[new-skill issue](.github/ISSUE_TEMPLATE/new-skill.yml) first — it captures
the required fields, all of which are mandatory in the PR too:

- **Observable trigger** — what a session can *see* that activates the skill
- **Counterindications** — when it must NOT fire
- **Bounded procedure** — steps with an explicit budget
- **Expected output** — what the skill's result looks like
- **Verification** — how a reader checks the skill did its job
- **Stop condition** — when the skill is done or must abort
- **Positive example** — a real trace where it helps
- **Near miss** — a case that looks like a trigger but isn't
- **Negative-transfer risk** — where this skill could make things *worse*
- **Evaluation plan** — how it will be measured
- **Evidence level** — claimed level with receipts (new skills start at
  `DESIGNED`; that's fine and honest)

### 2. Verifiers

Checkers used by `verify` and `inspect` — arithmetic re-derivation, schema
checks, completeness checks, layer-specific defect detectors. A verifier PR
needs: the defect class it detects, test cases including at least one
adversarial case designed to fool it, and its false-positive/false-negative
behavior stated.

### 3. Model adapters

Adapters for new model backends. Requirements: honors provenance recording
(model identity per run, hard stop on unavailability — **no silent
fallback**), no network activity beyond the declared endpoint, no credentials
in logs or state, and a smoke-test script a reviewer can run.

### 4. Tasks and benchmark reproductions

Evaluation tasks for the public suite, or reproductions of our published
numbers on your hardware/models. Reproductions are publishable **especially
when they disagree with us** — file a
[case-study issue](.github/ISSUE_TEMPLATE/case-study.yml) with your setup,
exact versions, and outputs.

### 5. Negative-transfer reports

Found a configuration where Piénsalo makes results worse? That's a
first-class contribution — file a
[negative-transfer report](.github/ISSUE_TEMPLATE/negative-transfer.yml).
Confirmed reports are added to [NEGATIVE-RESULTS.md](NEGATIVE-RESULTS.md)
with credit.

### 6. Docs, examples, case studies

Real usage traces (with your permission to publish, secrets scrubbed) teach
more than reference docs. See
[docs/good-first-issues.md](docs/good-first-issues.md) for starter tasks.

## Development setup

```bash
git clone https://github.com/piensalo/piensalo
cd piensalo
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

CI runs pytest on Python 3.10–3.12 across Ubuntu and macOS, plus skill lint,
secret scan, and package build — green CI is required, and reproducing it
locally before pushing saves everyone a cycle.

## Security standards for contributions

- Never commit credentials, tokens, real user data, or machine-identifying
  paths. CI greps for secret patterns, but the grep is a net, not a license.
- Skill text is treated as untrusted input by the loader — don't write skills
  that assume otherwise, and don't add loader features that execute skill
  content.
- If your contribution touches a guard (scanner rule, path check, scrubber),
  include the adversarial test that tries to defeat it.

## Review and merge

Maintainers review for correctness, evidence honesty, security invariants,
and scope. Expect requests to *shrink* PRs. Capability claims in docs are
checked against EVIDENCE.md — a doc PR cannot upgrade an evidence level; only
an experiment can.
