# OPERATOR LAUNCH DECISION — PIÉNSALO v0.1.0 (NOT PUBLISHED)

> **IDENTITY MIGRATED (2026-07-12).** The public product name is now
> **PIÉNSALO** (technical identifiers: `piensalo`); "Fable Think" was the
> internal development codename. Repository proposal: `ralfyishere/piensalo`
> or a `piensalo` GitHub org — the final owner/org is an operator decision;
> docs use `github.com/ralfyishere/piensalo` as the placeholder until it is
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
  `github.com/ralfyishere/piensalo` as a placeholder; pick one and sweep the
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
3. `github.com/ralfyishere/piensalo` placeholder appears in docs — must be swept to the chosen URL pre-push.
4. uv.lock absent; `uvx piensalo` untested until first PyPI (Test PyPI recommended first).
5. CoC/security contact email unset (LAUNCH gate item).

## Exact commands that WOULD publish (DO NOT RUN without approval)
```
# 1. choose identity (example: personal repo)
gh repo create ralfyishere/piensalo --public --source "$HOME/Desktop/Piensalo" --push
# or org route: create org 'piensalo' in UI, then:
# git remote add origin git@github.com:ralfyishere/piensalo.git && git push -u origin main
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

---

# ALPHA-READINESS STATUS (2026-07-13, autonomous pass, verified claude-fable-5)

## COMPLETE (engineering, verified this pass)
- uv flow end-to-end: `uv sync` (uv 0.11.28 installed via Homebrew), `uv.lock` committed, `uv run pytest` 49/49, `uv run piensalo ...` CLI, **`uv build`** (wheel + sdist)
- Wheel/sdist inspected: correct `piensalo/` paths, zero old-package residue, metadata Name=piensalo License=MIT, sdist carries README/LICENSE/pyproject
- Isolated wheel install (fresh Python 3.11 venv): `piensalo version` → 0.1.0.dev0
- Dev dependency group added (pytest) — the one engineering defect uv exposed
- Orphan oracle-repair labels REMAPPED to existing micro-skills (7 meta.json files: compounding-check→rederive-the-numbers, hard-constraints-first→disqualifier-scan, boundary-condition-check→boundary-case-check, output-contract-echo→complete-the-delivery, contradiction-sweep→contradiction-resolution); oracle prompt-builder smoke-tested (skill bodies resolve; menu=20)
- Model-support claims aligned with actual testing (README testing-status note: live runs = Claude family only; other adapters experimental)
- CLI verification: all 7 `--help`s; think/inspect/repair/verify example runs; bounded loop smoke (start/status only); skill list; **skill lint 27/27**
- Scans: secrets 0 (CI pattern-definition false positive classified), machine paths 0, stale brand 0 non-intentional, old-dir refs 0, broken relative links 0
- Grader battery 11/11 PASS · benchmark smoke OK · full test suite 49/49
- Alpha package: ALPHA-START-HERE.md, ALPHA-INVITE.md (send-ready template), ALPHA-TESTER-INSTRUCTIONS.md, ALPHA-RESULT-TRACKER.md (empty by honesty), plus existing ALPHA-PLAN / FEEDBACK-SCHEMA / EXIT-CRITERIA
- Export manifest + hash manifest regenerated at final state; no remote; nothing published
- Final-HEAD certification: acceptance suite re-run on a fresh clone of the exact final commit; result recorded in the annotated tag `piensalo-alpha-ready-candidate` (tag message = certification record, keeping tested commit == final HEAD)

## BLOCKED BY ENGINEERING
- None known. (CI workflow itself still unexecuted — no local runner; first run happens when a remote exists. OPTIONAL pre-launch: run via act or a private mirror.)

## BLOCKED BY EXTERNAL HUMAN TESTING
- 10 independent alpha installs + structured reports (tracker empty — honestly)
- 5 real-world case studies (pipeline table NOT STARTED)
- Live multi-model smoke on non-Claude families (OpenAI-compatible/Ollama adapters need real endpoints; unit-tested only)
- Public benchmark reproduction by anyone other than the builder

## BLOCKED BY OPERATOR DECISION
- GitHub owner: org `piensalo` (recommended: matches package, free at check) vs `ralfyishere/piensalo`; then sweep the `github.com/ralfyishere/piensalo` placeholder if the personal route is chosen
- Security/CoC contact identity (email or GitHub-advisories-only)
- Domain purchases + USPTO/professional trademark review (name audit found no software/company collision; song-title namespace = LOW)
- The publication go/no-go itself (exact commands preserved above, still not executed)

## OPTIONAL
- Demo recording (script ready: social/demo-script.md); Obsidian Studio screenshot; Test PyPI dry-run before real PyPI; Windows support statement upgrade

## Claims allowed / prohibited — unchanged from the migration section; evidence limitations unchanged (one model family, n=8/run, run-2 saturated)

## Exact private-alpha next step (for the operator)
Pick 10 candidate testers → send public-export/ALPHA-INVITE.md via private
channels → deliver the repo privately (zip or private remote after your
owner decision) → track in ALPHA-RESULT-TRACKER.md. Nothing else is needed
from engineering to begin.

---

# CREATOR-BRAND FINALIZATION (2026-07-13, verified claude-fable-5)

## RESOLVED — Repository ownership
Owner: **ralfyishere** · Repository: **piensalo** · Canonical future
repository: **https://github.com/ralfyishere/piensalo**. This is a
deliberate creator-brand strategy, not a compromise; no PIÉNSALO GitHub
organization will be created. All prepared references resolved (17 files);
`piensalo/piensalo` remaining: 0.

## RESOLVED — Creator identity
Creator: **Rafael “Ralph” Peña** · GitHub: **@ralfyishere**. Attribution
durable across README (hero line + Creator section), CITATION.cff (Peña /
Rafael / alias ralfyishere; title PIÉNSALO), pyproject authors, CODEOWNERS
(* @ralfyishere), CoC enforcement, origin story, technical report, launch +
social drafts. No email invented anywhere (operator decision pending).

## RESOLVED — Brand architecture
Product **PIÉNSALO** · Tagline **Give any AI a better way to think.** ·
Category **The open artificial cortex for AI.** · Expanded: an open
artificial cortex for AI models and agents · Technical architecture: a
model-independent cognitive operating system. Hierarchy installed in the
README hero and led through LAUNCH + social drafts. Audit:
public-export/CREATOR-BRAND-AUDIT.md.

## Prepared GitHub repository metadata (record only — do not apply)
Description: "PIÉNSALO is the open artificial cortex for AI—an
evidence-driven system for understanding, verification, repair, abstention,
and continuation." (152 chars, within GitHub's 350 limit)
Topics: ai · ai-agents · agent-skills · reasoning · verification · llm ·
cognitive-architecture · cognitive-operating-system · model-agnostic ·
open-source

## Status taxonomy (unchanged where not listed)
- COMPLETE (this pass): ownership resolution, creator attribution,
  artificial-cortex positioning, canonical references, current-vs-future
  command split, profile draft (public-export/RALFYISHERE-PROFILE-DRAFT.md),
  brand audit, re-verification (tests/battery/smoke/lint/build/clone/scans)
- BLOCKED BY EXTERNAL HUMAN TESTING (unchanged): 10 testers · 5 case
  studies · live non-Claude runs · third-party reproduction
- BLOCKED BY OPERATOR DECISION (remaining): dedicated project email ·
  domain decision · trademark/legal review · public repository creation ·
  package publication · public launch approval
- OPTIONAL: demo recording · Obsidian screenshot · Test PyPI dry-run ·
  applying the profile draft

---

# PUBLICATION RECORD (2026-07-13, operator-authorized)

- PUBLIC GITHUB REPOSITORY: **COMPLETE** — https://github.com/ralfyishere/piensalo
- PUBLIC ALPHA: **LIVE** — release v0.1.0-alpha.1 (prerelease):
  https://github.com/ralfyishere/piensalo/releases/tag/v0.1.0-alpha.1
- Published commit: 803e27c (aa77486 + the required README public-alpha
  statement); public-clone verified equal, full flow green (uv sync, 49
  tests, battery 11/11, doctor, think, inspect, skills listing)
- Tags pushed: piensalo-alpha-ready-candidate, piensalo-creator-brand-final,
  v0.1.0-alpha.1 · Issues: ENABLED · Discussions: ENABLED · Private
  Vulnerability Reporting: ENABLED · Topics: 10 applied · Description: set
- Outside view: anonymous 200 on repo + raw README (hero hierarchy renders);
  private-artifact 404 checks pass; no private Fable refs pushed
- PYPI PUBLICATION: **NOT YET** · SKILLS.SH SUBMISSION: **NOT YET**
- BROAD PERFORMANCE CLAIMS: **BLOCKED BY ADDITIONAL EVIDENCE** (10 testers,
  5 case studies, live non-Claude runs, third-party reproduction — now
  public workstreams, not privacy blockers)
- Security contact (alpha): GitHub Issues (ordinary) + Private Vulnerability
  Reporting (sensitive); dedicated project email = future operational
  improvement
- Announcement campaign: NOT executed in this pass by design
