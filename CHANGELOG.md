# Changelog

All notable changes to Piénsalo are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [SemVer](https://semver.org/) once we reach 0.1.0; until then,
everything may change.

## [0.1.0-alpha.2] — 2026-07-13

Truthfulness and UX correction release.

### Added
- Real flagship workflow: `examples/flagship/` with a committed transcript of
  actual CLI output; CI parity tests prevent README/demo drift
- `repair` adapter mode: writes a NEW repaired file + provenance sidecar and
  automatically re-inspects the result; source drafts are never overwritten
- `think` accepts a task file or inline text (`--file`/`--text` overrides)
- `python -m piensalo`; `skill lint`/`scan` accept multiple and parent paths
- PyPI publication via GitHub trusted publishing (release-triggered)

### Changed
- `repair` default mode clearly labeled as a repair PACKET (nothing applied)
- `verify` reports in five strict buckets; UNMEASURED never counts as a pass
- Roadmap reconciled to the truthful maturity hierarchy; stale
  pre-publication language removed; public tree simplified (operator/process
  scaffolding removed, provenance kept under docs/provenance/)

### Fixed
- Red CI Skill lint job (root cause: missing `__main__.py` + single-path lint)
- Tests: 49 → 86

## [Unreleased] — 0.1.0-dev

### Changed
- 0.1.0-dev — public identity migrated to PIÉNSALO (previously internal
  codename Fable Think); no functional changes.

### Added
- Cognitive core: 11 operations (`recover_objective` → `deliver`) with a
  bounded execute → inspect → repair → verify lifecycle.
- Six CLI modes: `think`, `inspect`, `repair`, `verify`, `loop`, `skill`.
- Portable Agent Skills layer (works in any agent that reads skills; no
  runtime required).
- Optional runtime: persistent state, bounded loops, model provenance
  recording, measurement hooks.
- Abstention as a first-class result: `NO REPAIR NEEDED`.
- Model adapters: manual copy/paste, Claude / Claude Code, OpenAI-compatible,
  Ollama/local, generic command adapter.
- `piensalo skill scan` (third-party skill vetting) and
  `piensalo doctor` (environment + configuration audit).
- Evidence discipline: per-capability evidence levels with promotion gates
  (docs/evidence-levels.md), public negative results (NEGATIVE-RESULTS.md).
- Security defaults: zero telemetry, offline core, no silent model fallback,
  no destructive actions without approval (SECURITY.md, THREAT-MODEL.md).

### Notes
- Pre-release. Evidence base is young; see README "Limitations" and
  EVIDENCE.md before relying on any capability claim.
