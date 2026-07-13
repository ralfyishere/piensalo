# Alpha Exit Criteria

The gate between alpha and public launch. Every item is **binary and
checkable** — no "mostly done". An item passes only with the evidence
artifact linked next to it. If an item can't pass, the alpha extends; the
criteria don't shrink.

| # | Criterion | Pass condition | Evidence |
|---|---|---|---|
| 1 | Fresh clone works | On a machine with no prior exposure: `git clone` → documented install → `piensalo doctor` passes, ≤ 10 minutes | recorded session log |
| 2 | One-command install | Each of `uvx piensalo`, `pipx install piensalo`, `npx skills add piensalo` succeeds on a clean environment | CI or recorded logs, one per path |
| 3 | Three model families | The demo lifecycle (think → inspect → repair → verify) completes on 3 distinct families, at least one fully local/offline | evidence bundles with provenance records |
| 4 | Benchmark reproduces | A third party reproduces the published benchmark from the public repo alone, no maintainer assistance beyond the docs | reproducer's writeup + outputs |
| 5 | Negative transfer measured | A paired comparison (with/without Piénsalo) run and published, including any task where we made things worse | published in EVIDENCE.md |
| 6 | Abstention measured | `NO REPAIR NEEDED` rate on already-correct inputs measured and published, with false-abstention rate | published in EVIDENCE.md |
| 7 | Scans pass | `piensalo skill scan` clean on all shipped skills; secret scan clean on full git history; no private identifiers or machine paths in the repo | scan outputs archived |
| 8 | Ten independent users | ≥ 10 users outside the project completed ≥ 1 full feedback record each ([schema](ALPHA-FEEDBACK-SCHEMA.json)); blockers they reported are fixed or documented as known limitations with an explicit decision | feedback records (consented subset published) |
| 9 | Five case studies | 5 published case studies with full evidence trails, including ≥ 1 abstention case and ≥ 1 failure/negative case | docs/ case studies |
| 10 | Docs match behavior | README, SECURITY.md, THREAT-MODEL.md, evidence-levels reviewed line-by-line against actual CLI behavior; every discrepancy fixed or the doc corrected | review checklist, dated + signed off |
| 11 | Demo is real | The 60-second demo re-recorded against the shipping build; transcript in README matches actual output shape | recording + diff check |

## Hard blockers (any one stops launch regardless of the table)

- A security default from [SECURITY.md](../../SECURITY.md) found violated in the
  shipping build.
- An evidence-level claim in any public doc that exceeds its receipts.
- Unresolved secret or private identifier in git history.

## Sign-off

Two maintainers independently walk the table, then record: date, commit hash,
and any items passed with noted caveats. The sign-off record is published in
the release notes — including the caveats.
