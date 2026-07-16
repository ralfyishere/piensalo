# Changelog

All notable changes to Piénsalo are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [SemVer](https://semver.org/) once we reach 0.1.0; until then,
everything may change.

## [0.1.0-alpha.5] — 2026-07-16

### Added
- **Cortex Gateway (observe mode)** — the delivery layer that makes the
  THINK · CHECK · CONTEXT cortex reachable from existing AI tools. It does
  **not** add a fourth brand and does **not** own the model.
  - `piensalo serve --mode observe --upstream-base-url <url> --upstream-model <id>`:
    a loopback HTTP gateway on the OpenAI Chat Completions boundary. Forwards
    requests **verbatim** and non-stream responses **byte-for-byte**; forwards
    SSE streams in order (application payload byte-identical); preserves
    tool-call ids/arguments; runs the deterministic **Cortex Router** in
    **shadow** (recorded, never acted on); writes a redact-by-default local
    event ledger.
  - `piensalo gateway status|inspect|report|replay|doctor` — read-side over the
    local event ledger (JSON/JSONL, no dashboard).
  - Security defaults fail closed: loopback-only bind, SSRF-guarded upstream
    (scheme allow-list + link-local/metadata/reserved block + optional prefix
    allow-list), bearer auth (401), body cap (413), recursive-loop guard (508),
    secret-header redaction, no body retention by default.
  - Docs: `docs/gateway/{ARCHITECTURE,SECURITY,PROTOCOLS,ROUTING,PRIVACY,EVALUATION}.md`;
    offline demo `examples/gateway/`.
- **Cortex Vault** (persistent cognitive memory) reserved as a DESIGNED future
  stage under CONTEXT (`docs/context/CORTEX-VAULT.md`); gateway event schema
  gains empty-in-observe `memory_refs_read`/`memory_updates_proposed` seams so
  the memory layer can attach without a core redesign.

### Scope note
- **Observe mode is a pass-through + measurement surface. It does not modify
  responses and makes no performance claim.** Intervention modes
  (`optimize-safe`, `verified`) are DESIGNED, not implemented.

## [0.1.0-alpha.4] — 2026-07-14

### Added
- **PIÉNSALO Context** subsystem (`piensalo context …`):
  - `compile` / `inspect` / `verify` / `diff` — deterministic Continuation
    Capsules: typed consequence records, active vs superseded decisions,
    exactness classes, content-addressed source references, byte-stable
    serialization, honest budget refusal; behavioral equivalence reported
    UNMEASURED (structural verification only).
  - `optimize` / `run` / `evaluate` — task-specific Context Optimizer:
    normalizes plain text, marker transcripts, generic JSONL/chat JSON,
    tool records, and file artifacts; inspectable per-chunk selection with
    mandatory-context preservation and OPTIMIZATION REFUSED when mandatory
    content exceeds the budget; explicit-adapter execution with
    deterministic verification, bounded expansion (default 2), safe
    fallback that is never counted as optimized success, and a full token
    ledger separating benchmark cost from deployable runtime cost.
- Pre-registered 8-task paired evaluation suite with committed results
  (`evals/context-optimizer/`): median gross context reduction 80.2%,
  median runtime net input savings 76.9%, zero critical regressions,
  designed fallback task refused safely (one model family, single samples).
- Demos with anti-drift tests: `examples/context/` (deterministic,
  byte-for-byte) and `examples/context-optimizer/` (deterministic step
  byte-for-byte plus one real recorded model run).

### Fixed
- `claude-cli` adapter: disables tools (`--tools ""`) so a completion is a
  single turn (with tools on, the model could explore the machine —
  breaking provenance and any context-limited comparison), and reports
  real billed input (`input + cache_creation + cache_read`; previously
  only `input_tokens`, e.g. 9 for a 2.4k-token prompt).

## [0.1.0-alpha.3] — 2026-07-13

### Fixed
- `piensalo version` derives from installed package metadata instead of a
  hardcoded string (0.1.0-alpha.2 shipped printing `0.1.0.dev0`); regression
  test added.

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
