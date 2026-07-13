# PIÉNSALO — Name Availability Audit (preliminary product search, not a legal opinion)

Checked 2026-07-12/13 by the build session. Registry checks are live HTTP
facts; web sweeps are search-engine results at check time. No purchases, no
reservations, no accounts created, no publication.

```json
[
 {"surface":"PyPI package","query":"pypi.org/pypi/piensalo/json","result":"404 — AVAILABLE","checked_at":"2026-07-12","risk":"LOW","evidence":"HTTP 404","operator_action_required":false},
 {"surface":"PyPI package (fallback)","query":"pypi.org/pypi/piensalo-ai/json","result":"404 — AVAILABLE","checked_at":"2026-07-12","risk":"LOW","evidence":"HTTP 404","operator_action_required":false},
 {"surface":"GitHub org/user","query":"api.github.com/users/piensalo","result":"404 — UNCLAIMED","checked_at":"2026-07-12","risk":"LOW","evidence":"HTTP 404","operator_action_required":true},
 {"surface":"GitHub repo","query":"api.github.com/repos/ralfyishere/piensalo","result":"404 — AVAILABLE","checked_at":"2026-07-12","risk":"LOW","evidence":"HTTP 404","operator_action_required":true},
 {"surface":"npm package","query":"registry.npmjs.org/piensalo","result":"404 — AVAILABLE (only needed if a JS shim ships)","checked_at":"2026-07-12","risk":"LOW","evidence":"HTTP 404","operator_action_required":false},
 {"surface":"skills.sh","query":"not checked programmatically (no public availability API found)","result":"UNKNOWN","checked_at":"2026-07-12","risk":"UNKNOWN","evidence":"n/a — submission is an operator-gated launch step anyway","operator_action_required":true},
 {"surface":"Web — software/AI project collision","query":"\"piensalo\" software OR app OR AI project github","result":"NO software project named piensalo surfaced","checked_at":"2026-07-12","risk":"LOW","evidence":"search returned only generic AI-repo listings","operator_action_required":false},
 {"surface":"Web — company/trademark collision","query":"\"piénsalo\" company OR trademark OR product name","result":"no company/product surfaced; USPTO full-text search NOT performed (requires interactive session)","checked_at":"2026-07-12","risk":"UNKNOWN","evidence":"search returned only generic trademark-law pages","operator_action_required":true},
 {"surface":"Cultural namespace (accented + unaccented)","query":"general knowledge + search","result":"\"Piénsalo\" is a common Spanish imperative and exists as popular SONG titles (e.g., a well-known banda track). Different category from software; descriptive common word — weak trademark surface both ways (for and against us)","checked_at":"2026-07-12","risk":"LOW-MEDIUM","evidence":"song-title uses only; no software use found","operator_action_required":false},
 {"surface":"Domains (piensalo.com/.dev/.ai)","query":"not checked (no registrar lookup from this environment)","result":"UNKNOWN — common Spanish word, .com likely taken","checked_at":"2026-07-12","risk":"UNKNOWN","evidence":"n/a","operator_action_required":true},
 {"surface":"Social handles","query":"informational only — not checked","result":"UNKNOWN","checked_at":"2026-07-12","risk":"UNKNOWN","evidence":"n/a","operator_action_required":false}
]
```

## Summary
- **All load-bearing technical identifiers are free**: PyPI `piensalo`, npm
  `piensalo`, GitHub org `piensalo`, repo `ralfyishere/piensalo`.
- **No software, AI-product, or company collision surfaced.** The name lives
  in a musical/cultural namespace (song titles) — a different category and
  LOW risk for an open-source developer tool, but it means search results
  will be shared with music content (discoverability consideration, not a
  conflict).
- **Not done here** (operator items before launch): USPTO/EUIPO trademark
  full-text search (professional review if the project commercializes),
  domain registrar checks, skills.sh namespace, social handles.
- **No severe collision found → no OPERATOR-NAME-DECISION-REQUIRED.md needed.**
  Final org-vs-personal-repo choice remains the operator's launch decision.
