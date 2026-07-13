# Creator-Brand Consistency Audit — PIÉNSALO (2026-07-13)

Audited after the creator-brand finalization pass, on the working tree that
became the `piensalo-creator-brand-final` tag.

## Identity hierarchy (verified present, in order, in README hero)
Product **PIÉNSALO** → tagline **"Give any AI a better way to think."** →
category **"The open artificial cortex for AI."** → architecture
**"a model-independent cognitive operating system"** → creator
**Rafael "Ralph" Peña / @ralfyishere** → repository
**github.com/ralfyishere/piensalo**.

## Consistency results

| Surface | Result |
|---|---|
| Product name | PIÉNSALO (titles) / Piénsalo (prose) / `piensalo` (identifiers) — consistent |
| Tagline | 5 files (README hero, LAUNCH lead, social set) — verbatim |
| Artificial-cortex category | 7 files; leads README hero, LAUNCH, show-hn, linkedin, x-thread; "cognitive layer" survives only as informal deep-doc phrasing, never in hero positioning |
| Technical architecture | "model-independent cognitive operating system" in README hero + show-hn + linkedin (supporting, not replacing, the category) |
| Creator name | "Rafael "Ralph" Peña" ×10; plain "Rafael Peña" ×2 — both in technical metadata fields (CITATION.cff given/family split; pyproject authors), where the quoted-nickname form doesn't fit. No "Rafael Pena"/"Ralph Pena" variants remain in authored content (git commit metadata retains the pre-existing ASCII author name — historical, unrewritten by design) |
| GitHub handle | @ralfyishere / alias `ralfyishere` (CITATION) — consistent |
| Repository owner | `ralfyishere/piensalo` in 17 files; `piensalo/piensalo` remaining: **0** |
| Canonical future URL | https://github.com/ralfyishere/piensalo everywhere a URL appears |
| Independence notice | verbatim in 8 files |
| Evidence limits | testing-status note intact (Claude-family live evidence; other adapters experimental); no universal-improvement claims introduced |
| Current vs future commands | README install split into "Now (private alpha)" (uv sync / pip install ., working) vs "After publication" (uvx/pipx/npx/git clone, explicitly marked non-working); alpha docs unchanged (local-first) |

## Classification of every repository-owner reference
- `ralfyishere/piensalo` (17 files): **CURRENT AND CORRECT** (marked future
  where the remote doesn't exist yet)
- `backup/fable-think-before-piensalo`, `fable-think-public-pre-piensalo`
  (audit/prompt docs): **HISTORICAL AND INTENTIONAL** (real git refs)
- Old org form `piensalo/piensalo`: **STALE AND REMOVED** (0 remain)
- Third-party references: none found
- **OPERATOR DECISION STILL REQUIRED:** none for ownership (RESOLVED); the
  dedicated project email remains an operator decision and is deliberately
  absent from all metadata

## Over-branding check
Creator appears: README (1 hero line + 1 Creator section), CITATION,
pyproject, CODEOWNERS, CoC enforcement, origin-story opening, technical-
report author line, show-hn (one sentence), linkedin/x-thread (lead voice),
LAUNCH lead, profile draft. README does not open with biography; no
unrelated business/personal details anywhere. Judged: unmistakable, not
obnoxious.

## Missing-attribution check
All surfaces from the directive list carry attribution or deliberately omit
it (ALPHA tester docs stay product-focused by design; release metadata =
pyproject/CITATION, done). No gaps found.
