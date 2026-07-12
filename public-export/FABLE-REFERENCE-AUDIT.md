# Fable Reference Audit — PIÉNSALO identity migration (2026-07-12)

Post-migration classification of every remaining "Fable" token in the public
tree (case-insensitive; `.git/` and the generated hash manifest excluded).
Pre-migration survey: 88 files mentioned the old identity; 120 files were
changed by the technical-identifier pass, plus classified prose edits by
three owned workstreams and the primary session.

## Totals
- References found pre-migration: ~88 files (54 `fable-think`, 36 `fable_think`, 86 "Fable Think"; 0 "Fable 5"/"Fable5" — no model-name references ever existed in this tree)
- Current stale branding REMOVED: all (identifiers, commands, skill ids, env var `FABLE_THINK_ROOT`→`PIENSALO_ROOT`, evals/example headers, prose, wrapped-line remnants, `fablethink` alias claims + entry point)
- Historical references RETAINED: 15 lines in 4 files (below)
- Private-source references SANITIZED: operator-machine absolute paths removed from OPERATOR-LAUNCH-DECISION.md (historical text otherwise preserved); EXPORT-MANIFEST `private_source` fields deliberately KEEP true private-lab paths (`dist/skills/fable-*` etc.) — that is provenance, not branding, and an early mechanical pass that briefly rewrote them was detected and REPAIRED
- Ambiguous references requiring review: 0

## Final residual inventory (all intentional)

| File | Lines | Class | Disposition |
|---|---|---|---|
| CHANGELOG.md | 1 | historical | migration entry: "previously internal codename Fable Think" — RETAIN |
| docs/origin-story.md | 1 | historical | codename sentence — RETAIN |
| LAUNCH.md | 1 | historical | codename sentence in origin section — RETAIN |
| public-export/EXPORT-MANIFEST.json | 12 | provenance | `private_source` true lab paths (`dist/skills/fable-think`, ...) — RETAIN (historical truth outranks cosmetic consistency) |
| public-export/OPERATOR-LAUNCH-DECISION.md | 12 | historical record | dated IDENTITY MIGRATED note quoting original identity fields + preserved decision body; machine paths sanitized — RETAIN |

## Verification at close
- `grep -rniE "fable"` (excl. .git, hash manifest): 27 hits, all enumerated above
- old repo-URL references (`github.com/fable-think/...`): 0
- old directory references (`Desktop/Fable Think`): 0
- absolute operator-machine paths (`/Users/...`): 0
- `fablethink` entry point: removed from pyproject; no doc claims it
- tests 49/49 · grader battery 11/11 PASS · benchmark smoke OK · skill lint 27/27 (workstream) + spot re-run by primary session
