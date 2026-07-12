# OPERATOR LAUNCH DECISION — PIÉNSALO v0.1.0 (NOT PUBLISHED)

> **IDENTITY MIGRATED (2026-07-12).** The public product name is now
> **PIÉNSALO** (technical identifiers: `piensalo`); "Fable Think" was the
> internal development codename. Repository proposal: `ralfyishere/piensalo`
> or a `piensalo` GitHub org — the final owner/org is an operator decision;
> docs use `github.com/piensalo/piensalo` as the placeholder until it is
> made. PyPI: **piensalo** — availability re-check pending name audit. A
> single console script (`piensalo`) ships; the `fablethink` alias originally
> recorded below was dropped in the technical migration. The local path is
> now `$HOME/Desktop/Piensalo`. Original identity fields as first
> recorded (historical): product name "Fable Think"; PyPI `piensalo` with
> alias `fablethink`; console scripts `piensalo` + `fablethink`. Apart from
> the Product identity section, the decision text below is preserved
> unchanged as the historical record — where it says "Fable Think" or uses
> the old local path, read the internal codename / pre-migration state.

Prepared 2026-07-12 by the verified claude-fable-5 session. Nothing below has
been executed against any remote. **The repository has no remote. Publication
requires Rafael's explicit approval of this document.**

## Product identity
- Final product name: **PIÉNSALO** (human-facing Piénsalo; identifiers
  `piensalo`). Internal development codename: "Fable Think".
- Proposed repository: `ralfyishere/piensalo` (verified 404/free at original
  check). Option: create a `piensalo` GitHub org (org name unclaimed at check
  time) — the final owner/org is an operator decision; the docs use
  `github.com/piensalo/piensalo` as a placeholder; pick one and sweep the
  placeholder before push.
- Package identifiers: PyPI **piensalo** — availability re-check pending name
  audit. Single console script `piensalo` (the originally planned
  `fablethink` alias no longer ships).
  The `fable` PyPI name is TAKEN — we claim neither the package nor a `fable`
  binary (collision risk documented).

## Repository state
- Local path: `<local clean-room checkout>` (since renamed to the Piensalo directory) (sibling clean-room; new
  git history; zero private history).
- ~552 files, 2.8 MB. Full tree hash manifest: `public-export/HASHES.sha256`
  (536 files). Per-artifact provenance: `public-export/EXPORT-MANIFEST.json`
  (73 entries: ported-rewritten / ported-hardened / authored; nothing exported
  from the never-export list).
- Public/private boundary: private repo remains the laboratory; exported
  content = 27 skill packages, ported runtime modules (loop, scanner,
  contract, layered grading), CONSUMED run-1 task set (renamed + hardened),
  3 fresh DEMO tasks, aggregate evidence only. NOT exported: .git, .fable,
  transcripts, unconsumed tasks, credentials, memory, bundles, business
  context, machine paths.

## q4 mechanism verdicts (drove the v0.1 defaults)
- inspect-then-repair with **abstention-first** posture: EXPERIMENTALLY_TESTED → the default.
- output-contract-guardian: EXPERIMENTALLY_TESTED, **default-on where a contract exists** (30% delivery reduction run-1; zero harm both runs; ≥50% gate not yet passed → not PROMOTED).
- targeted micro-skill repair content: **NARROW** — repair-when-failing only; forced repair measured destructive (delivery layer) on correct drafts.
- adaptive repair routing: **REJECTED as shipped** (correctness-blind detection) → ships EXPERIMENTAL, off by default.
- monolithic domain skill: **NARROW** (real knowledge-floor harm, artifact-free) → available, honestly labeled, not default.
- Full records: EVIDENCE.md; run summaries: BENCHMARKS.md; failures: NEGATIVE-RESULTS.md.

## Feature maturity labels
- stable: none (v0.1.0 is alpha; no mechanism is PROMOTED)
- beta: think/inspect/repair/verify CLI (offline), contract guardian, layered grading library, portable skills install
- experimental: adaptive router (off), loop slow-path self-improvement, provider adapters (unit-tested only, no live-provider runs)
- narrow: micro-skill forced repair, monolithic piensalo skill
- rejected: unconditional repair; silent model fallback (prohibited by design)

## Audits
- Security: skill_scan + doctor implemented; threat model T1–T11 with mitigations; defaults: no telemetry, no network without explicit adapter, no silent fallback. CI includes secret-scan step. Residual: adapters untested against live providers.
- Secret/private-data scan: orchestrator repo-level grep clean (only intentional hits inside the leak-detector itself and its test fixture); four workstream-level sweeps clean; NOT a full human read of all 552 files.
- License: MIT recommended and applied (LICENSE, per-skill frontmatter). THIRD_PARTY_NOTICES present. No copied third-party code identified by builders.

## Acceptance status
- Local: `python3 -m pytest` 49/49 · grader selftest 11/11 tasks PASS · `make benchmark` SMOKE OK (no API) · root Makefile delegates correctly.
- Fresh-clone: see FRESH-CLONE-RESULT block appended below after the check runs.
- CI: workflow authored, NOT executed (no runner locally). Known CI risks: `uv` steps unverified (uv absent on build machine; no uv.lock generated), Windows unsupported (documented).
- Alpha gate: NOT MET — outstanding: 3 model families live-run, public benchmark reproduction on live models, 10 independent users, 5 real-world case studies, demo recording, org/repo URL sweep, uv.lock. Tracked in ALPHA-PLAN.md / ALPHA-EXIT-CRITERIA.md.

## Claims policy
- Prohibited (enforced in docs): guaranteed improvement, cross-model generality, statistical certainty, Anthropic affiliation, copied-weights framing.
- Permitted: the pre-registered aggregates in BENCHMARKS.md with confounds attached; the abstention/harm findings; negative results.

## Launch content
- README (hero → 60-second demo → install → evidence), MANIFESTO, social/x-thread + show-hn + linkedin + demo-script, docs/origin-story (accurate: preserve-and-study origin; value stands independently). Demo assets: 4 SVGs; terminal recording still to produce (ALPHA item).

## Unresolved risks
1. v0.1 evidence base: one model family, n=8/run; run-2 saturated (lift claim rests on run-1).
2. Evals oracle-repair labels reference 5 genericized micro-skill names not yet present in micro-skills/ (degrades to SKIPPED, documented) — author or remap before alpha.
3. `github.com/piensalo/piensalo` placeholder appears in docs — must be swept to the chosen URL pre-push.
4. uv.lock absent; `uvx piensalo` untested until first PyPI (Test PyPI recommended first).
5. CoC/security contact email unset (LAUNCH gate item).

## Exact commands that WOULD publish (DO NOT RUN without approval)
```
# 1. choose identity (example: personal repo)
gh repo create ralfyishere/piensalo --public --source "$HOME/Desktop/Piensalo" --push
# or org route: create org 'piensalo' in UI, then:
# git remote add origin git@github.com:piensalo/piensalo.git && git push -u origin main
# 2. package (after uv lock + build on a machine with uv):
# uv build && uv publish            # Test PyPI first: uv publish --index testpypi
# 3. tag
# git tag v0.1.0-alpha && git push origin v0.1.0-alpha
```
Pre-push checklist (mandatory): sweep URL placeholder · re-run repo-level secret scan · private-data scan · fresh-clone acceptance green · Rafael reads README + EVIDENCE + this file.

## FRESH-CLONE-RESULT (2026-07-12, local clone to scratch)
- `python3 -m pytest -q` → 49 passed
- `python3 evals/harness/grader_selftest.py` → ALL GRADER SELF-TESTS PASS (11 tasks)
- `make benchmark` → SMOKE OK: 4 cells graded end-to-end (no API)
- `PYTHONPATH=src python3 -m piensalo.cli.main think examples/math/task.md` → renders the cognitive program (a Python-3.9 runpy warning appears on the below-floor interpreter; clean on 3.10+)
- `uv sync` / `uvx` NOT tested (uv absent on build machine — ALPHA item)
