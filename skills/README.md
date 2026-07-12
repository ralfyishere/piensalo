# Piénsalo — domain skills

Eight domain-level cognitive skills in the Agent Skills format. Each one packages a
full reasoning workflow — objective recovery, constraint extraction, candidate
generation, discriminating tests, adversarial verification, calibrated synthesis —
specialized for one class of work:

| Skill | Domain |
|---|---|
| `piensalo` | General hard problems — the core loop, domain-agnostic |
| `piensalo-build` | Building software: features, fixes, refactors |
| `piensalo-math` | Quantitative and formal reasoning |
| `piensalo-research` | Multi-source research and synthesis |
| `piensalo-strategy` | Decisions, plans, and strategy under uncertainty |
| `piensalo-invent` | Invention and novelty-seeking tasks |
| `piensalo-write` | High-stakes writing and editing |
| `piensalo-verify` | Standalone verification passes over existing work |

Every skill directory is self-contained and uses progressive disclosure:

```
<skill>/
  SKILL.md          # frontmatter (name, activation trigger, MIT license) + workflow
  skill-card.md     # one-page summary: trigger, counterindications, evidence level
  manifest.json     # machine-readable metadata
  references/       # loaded on demand, not at activation time
  examples/         # one positive example + one near-miss (when NOT to fire)
  evals/            # EVAL-PLAN.md — how this skill would be publicly evaluated
  BENCHMARK.md      # honest evidence status (most are DESIGNED; none claim proven lift)
```

## Install

### One skill, with the `skills` CLI

```bash
npx skills add <owner>/piensalo --skill piensalo
```

### One skill, manual copy

Copy the skill folder into your agent's skills directory:

```bash
cp -r skills/piensalo ~/.claude/skills/piensalo     # Claude Code
# or wherever your agent runtime discovers Agent Skills
```

### All eight

```bash
cp -r skills/piensalo* ~/.claude/skills/
```

Nothing else is required: skills have no runtime dependency, call no network
services, and read only their own bundled files plus your task.

### Managing skills with the Piénsalo CLI

```bash
piensalo skill list                          # enumerate visible skill packages
piensalo skill inspect piensalo              # print a skill's SKILL.md
piensalo skill export piensalo --target DIR  # export a portable copy
piensalo skill lint skills/piensalo          # structural checks
piensalo skill scan <third-party-dir>        # vet a third-party skill before install
```

## Choosing a skill

Load the domain skill that matches the work; `piensalo` is the fallback for any
hard multi-constraint problem. Do not stack several domain skills on one task —
they share the same core loop and stacking mostly adds prompt weight. For a single
targeted behavior repair, use a [micro-skill](../micro-skills/) instead.

## Honesty note

`BENCHMARK.md` in each skill states its real evidence level. Read it before
assuming a skill helps your model on your tasks: large added prompts can *hurt*
already-competent models on easy tasks, and no skill here claims replicated,
general lift.
