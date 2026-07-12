# Piénsalo — micro-skills

A **micro-skill** is the smallest useful unit of cognitive repair:

> **one observable trigger + one bounded procedure + one verification condition.**

Where a domain skill installs a whole workflow, a micro-skill patches exactly one
known failure mode — and does nothing else. Each is designed to add at most a few
hundred output tokens, and each states the conditions under which it must **not**
fire.

## Failure-first philosophy

These skills were built backwards from failures, not forwards from virtues. The
pipeline for every micro-skill was:

1. **Name a documented failure mode** — a specific, recurring way answers go wrong
   (accepting a metric as ground truth, shipping untested boundary behavior,
   silently dropping half the deliverable, resolving a contradiction by averaging).
2. **Define the observable trigger** — what in the task or draft signals that this
   failure is live *right now*. No trigger, no activation.
3. **Write the smallest bounded repair** — the shortest procedure that reliably
   prevents that one failure, with an explicit cost ceiling.
4. **Attach a verification condition** — a check (deterministic where possible)
   that tells you the repair actually happened, not just that the words appeared.

The counterindications are as load-bearing as the procedures: a micro-skill that
fires on the wrong task class wastes attention and can degrade output
(negative transfer). Every `skill-card.md` names that risk explicitly.

## Directory format

```
<micro-skill>/
  SKILL.md          # frontmatter (name, activation trigger, MIT license) +
                    # trigger / procedure / required output / verification / cost
  skill-card.md     # one-page summary incl. counterindications & negative-transfer risk
  manifest.json     # machine-readable: triggers, counterindications, evidence level
  examples/         # positive.md (fires correctly) + near-miss.md (must NOT fire)
  evals/            # EVAL-PLAN.md — how this micro-skill would be publicly evaluated
  BENCHMARK.md      # honest evidence status
```

## Evidence levels

Each `BENCHMARK.md` uses one status from:
`DESIGNED | SMOKE_TESTED | EXPERIMENTALLY_TESTED | REPLICATED | PROMOTED | NARROW | REJECTED`

Current honest summary: a handful of micro-skills are EXPERIMENTALLY_TESTED
(their repair content lifted a weak model on procedural tasks in controlled runs;
the effect is task-concentrated, and automatic *selection* of micro-skills by a
router is a separate, unproven layer). A few are SMOKE_TESTED. The rest are
DESIGNED. None claim replicated general lift.

## Install and use

Micro-skills are plain Agent Skills — copy any directory into your agent's skills
path, or inject the `SKILL.md` body directly into a prompt when you know the
failure mode you are guarding against:

```bash
npx skills add <owner>/piensalo --skill rederive-the-numbers
# or
cp -r micro-skills/rederive-the-numbers ~/.claude/skills/
```

The Piénsalo CLI manages them the same way as the domain skills:
`piensalo skill list` / `inspect` / `export` / `lint` / `scan` — e.g.
`piensalo skill lint micro-skills/rederive-the-numbers`.

Use them surgically: pick the one or two whose trigger matches your task, rather
than loading all nineteen. Bulk-loading defeats the design — the value is a
targeted repair at near-zero attention cost.
