# Verification criteria

Verification criteria for this skill's domain. Deterministic criteria are checked mechanically; adversarial criteria require constructing probes; evidence criteria grade support quality. Disqualifying criteria fail the whole candidate.

## Domain: writing
### objective_fulfillment (judgment) [disqualifying]
Per intent-clarity and scope-fence: restate the piece's objective in one line, then check the text actually does that job — not an adjacent job done well. Per output-structuring: the first two sentences carry the answer/point; a reader acting only on the opening must not be misled.

### audience_fit (judgment)
Per output-structuring: identify the named audience's next action and check the format serves it — right altitude (executive vs. implementer), right assumed knowledge, jargon defined or dropped. Test: could the stated audience act on this without asking a clarifying question?

### factual_consistency (evidence) [disqualifying]
Per verification-discipline: every checkable claim in the text (numbers, dates, names, quotes, capabilities) is verified against its source or labeled at its evidence level; recompute any arithmetic independently. Internal consistency too: the same figure must not appear as two different values in two sections.
- Tool protocol: `Extract all numbers/names/dates; cross-check each against source material and against other mentions in the same text.`

### structural_coherence (judgment)
Per output-structuring and ruthless-editor: each section earns its place and appears where the reader needs it — no orphan sections, no conclusions that import claims the body never established, no burying the answer in paragraph three. Run ruthless-editor's cut pass: anything removable without losing meaning is a defect.

### constraint_adherence (deterministic) [disqualifying]
Check every explicit constraint mechanically: word/length limits, required sections, mandated format, forbidden content, style rules. Per live-state-truth: count, don't estimate — quote the actual word count or section list against the requirement.
- Tool protocol: `tokens:any:word count,within the limit,required section,format check,constraint`

### originality (judgment)
Per verification-discipline's evidence-level rule applied to authorship: the text is not a close paraphrase of a single source, quotes are attributed, and any claim of original framing is honest — 'synthesized from X and Y' is honest; presenting borrowed structure as original is not. Adversarial check: pick the most distinctive passage and search for a near-duplicate.
- Tool protocol: `Search distinctive phrases (8+ word spans) for near-duplicates in source material.`

### Adversarial tests
- Hostile-skim test (adversarial-verify): read only the title, first two sentences, and headings — check the takeaway matches the full text's claims.
- Give the text to the WRONG audience persona (one level more expert, one less) and find the sentence that breaks first.
- Cross-check every number against every other mention of it in the same document.
- Ruthless-editor attack: delete the weakest paragraph; if nothing is lost, the piece failed the earn-its-place bar.

### Disqualifiers
- An explicit constraint (length, format, required section) mechanically violated.
- A factual claim contradicted by the provided source material.
- The opening promises a conclusion the body never establishes.
- Unattributed close paraphrase of a source.
