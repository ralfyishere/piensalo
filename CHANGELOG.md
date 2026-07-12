# Changelog

All notable changes to Fable Think are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [SemVer](https://semver.org/) once we reach 0.1.0; until then,
everything may change.

## [Unreleased] — 0.1.0-dev

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
- `fable-think skill scan` (third-party skill vetting) and
  `fable-think doctor` (environment + configuration audit).
- Evidence discipline: per-capability evidence levels with promotion gates
  (docs/evidence-levels.md), public negative results (NEGATIVE-RESULTS.md).
- Security defaults: zero telemetry, offline core, no silent model fallback,
  no destructive actions without approval (SECURITY.md, THREAT-MODEL.md).

### Notes
- Pre-release. Evidence base is young; see README "Limitations" and
  EVIDENCE.md before relying on any capability claim.
