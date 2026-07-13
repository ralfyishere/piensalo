# ALPHA-READINESS PASS — continuation prompt (self-contained)

Run this in a FRESH session. Do not re-derive state from conversation
history; this file + the repository are the state.

## Identity (final, migrated)
- Public product: **PIÉNSALO** (human-facing) / `piensalo` (repo, package,
  CLI, imports). Tagline: "Give any AI a better way to think." Category:
  an open artificial cortex for AI models and agents.
- Repository: `$HOME/Desktop/Piensalo` — local only, **no remote, NOT
  published**. Migration commit: `051af75` (start from the real HEAD; verify
  with `git log -1 --oneline`). Rollback refs (never push):
  `backup/fable-think-before-piensalo`, `fable-think-public-pre-piensalo`
  → `e69b647`. Local milestone tag: `piensalo-public-identity-migration`.
- The private laboratory (separate repo) remains Fable — never mirror it.

## Model integrity (mandatory before work)
Requested and resolved model must both be `claude-fable-5`; verify, record
branch+commit, confirm auto-switch stays disabled. On any switch:
MODEL_SWITCH_STOP — preserve safe work, record the event, write a
continuation prompt, exit. Headless cells pin full model IDs and assert
`modelUsage`. Deliberate operator-approved handoffs must be attributed.

## Read first
public-export/OPERATOR-LAUNCH-DECISION.md · ALPHA-PLAN.md ·
ALPHA-EXIT-CRITERIA.md · public-export/FRESH-CLONE-ACCEPTANCE.md ·
public-export/PIENSALO-NAME-AUDIT.md · EVIDENCE.md · BENCHMARKS.md ·
public-export/FABLE-REFERENCE-AUDIT.md

## Current evidence + maturity (do not re-litigate; from two 120-cell pre-registered runs)
- default posture inspect-then-repair with abstention-first: EXPERIMENTALLY_TESTED
- output-contract guardian: EXPERIMENTALLY_TESTED (on where contract exists; ≥50% gate unpassed → not PROMOTED)
- targeted repair content: NARROW (repair-when-failing only; forced repair harms delivery, never cognition — 0/48 flips)
- adaptive router: REJECTED as shipped (correctness-blind) → EXPERIMENTAL/off
- monolithic skill: NARROW (measured knowledge-floor harm)
- stable: none; no mechanism is PROMOTED. Never claim universal improvement.

## Known alpha blockers (the work of this pass)
1. uv flow unverified (uv absent on build machine): `uv sync`, `uv lock`,
   `uv run pytest`, `uv build` on a uv-equipped environment; commit uv.lock.
2. Three model families live-run (adapters are unit-tested only): manual +
   Claude CLI + one OpenAI-compatible/Ollama — smoke each documented CLI
   path against a live model; record requested+resolved per call.
3. Public benchmark reproduction on a live model (evals/harness) — small n
   is fine; publish variance; no cherry-picking.
4. Five real-world case studies (examples/ are DEMO illustrations, clearly
   labeled) — real tasks, bare vs Piénsalo, operator preference recorded
   separately; DO NOT fabricate users or results.
5. Ten independent alpha users install without the operator — recruitment
   PLAN + materials only; actual outreach is an operator boundary.
6. Evals oracle-repair labels name 5 micro-skills that don't exist
   (degrades to SKIPPED): author those micro-skill stubs or remap labels —
   narrow fix, no new architecture.
7. Demo recording per social/demo-script.md; obsidian-studio screenshot.
8. Repo URL placeholder `github.com/ralfyishere/piensalo` — final owner/org is
   an OPERATOR decision; sweep once decided.
9. CoC/security contact (operator).

## Commands
cd "$HOME/Desktop/Piensalo"
git log -1 --oneline                      # must show 051af75 or a descendant
python3 -m pytest -q                      # 49 passed baseline
python3 evals/harness/grader_selftest.py  # ALL PASS baseline
make benchmark                            # SMOKE OK baseline

## Hard boundaries
- NO publication: no remote, no push, no PyPI/npm/skills.sh submission, no
  account/domain purchases, no outreach — all operator-gated
  (OPERATOR-LAUNCH-DECISION.md is the gate).
- NO new architecture: no new skills (beyond blocker 6's stubs/remap), no
  new modes, loops, adapters beyond the three families, dashboards,
  frameworks, evidence mechanisms, or task sets.
- NO new evidence claims without a run behind them; no fabricated users,
  case studies, or numbers.
- Evidence/maturity labels change only from new measured runs.

## Acceptance (this pass is done when)
ALPHA-EXIT-CRITERIA.md items are individually marked PASS/FAIL/BLOCKED-ON-
OPERATOR with receipts; every documented README command executed from a
fresh clone on a uv-equipped environment; multi-model smoke recorded; case
studies real or explicitly pending; a final operator go/no-go packet
updates OPERATOR-LAUNCH-DECISION.md.

## Stop conditions
Model switch (MODEL_SWITCH_STOP) · any publication boundary reached →
operator decision file · blocker requires spending/accounts → operator
decision file · alpha packet complete → STOP and report. Bounded: one
alpha-readiness pass; do not begin launch execution.

## Fresh-session command
cd "$HOME/Desktop/Piensalo"
