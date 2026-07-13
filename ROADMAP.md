# Roadmap

Direction, not promises. Items ship when they pass their evidence gates
([docs/evidence-levels.md](docs/evidence-levels.md)), not when the calendar
says so. Dates are targets; honesty outranks schedule.

## v0.1 — Alpha (current)

**Theme: the core works, honestly.**

- [x] Cognitive core: 11 operations, bounded lifecycle
- [x] Six CLI modes: `think` / `inspect` / `repair` / `verify` / `loop` / `skill`
- [x] Portable Agent Skills layer (runtime-free)
- [ ] `piensalo doctor` and `piensalo skill scan` hardened
- [x] Engineering alpha verification: PASSED (tests, battery, packaging, fresh-clone certification)
- [x] Public alpha: LIVE — [ralfyishere/piensalo](https://github.com/ralfyishere/piensalo)
- [ ] Independent user validation: IN PROGRESS (submit results — see [docs/alpha/SUBMIT-RESULTS.md](docs/alpha/SUBMIT-RESULTS.md))
- [ ] Cross-model validation: IN PROGRESS (Claude-family evidence exists; other adapters await live runs)
- [ ] Third-party reproduction: PENDING
- Broad performance claims: NOT AUTHORIZED until the above land (full gate: [docs/alpha/ALPHA-EXIT-CRITERIA.md](docs/alpha/ALPHA-EXIT-CRITERIA.md))
  (fresh-clone install, three model families, reproducible benchmark,
  negative-transfer and abstention measured, independent users, case studies)

## v0.2 — Adapters + case studies

**Theme: portable in practice, not just in principle.**

- [ ] Model adapters hardened: OpenAI-compatible, Ollama/local, generic
  command adapter brought to parity with the most-tested family
- [ ] Cross-model evidence: same tasks, multiple families, published deltas
- [ ] Five public case studies with full evidence trails (real tasks,
  real verdicts, including at least one `NO REPAIR NEEDED` and one failure)
- [ ] Obsidian Studio (optional) first public release
- [ ] Skill contribution pipeline: `skill scan` + review checklist mature
  enough for third-party skills

## v0.3 — Public benchmark season

**Theme: anyone can check our numbers.**

- [ ] Public task suite with pinned versions and one-command reproduction
- [ ] Third-party benchmark runs solicited and published as submitted —
  including unfavorable ones
- [ ] Grader audit: published grader error analysis (both directions —
  under-credit and false credit)
- [ ] Evidence levels re-scored against the season's results; demotions
  published alongside promotions

## Explicitly not planned

- Telemetry, "anonymous usage analytics", or any phone-home behavior
- A hosted service that the core depends on
- An unreviewed prompt marketplace
- Claims of guaranteed improvement, on any roadmap, ever
