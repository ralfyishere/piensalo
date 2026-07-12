# Verification criteria

Verification criteria for this skill's domain. Deterministic criteria are checked mechanically; adversarial criteria require constructing probes; evidence criteria grade support quality. Disqualifying criteria fail the whole candidate.

## Domain: research
### claim_to_source_alignment (evidence) [disqualifying]
Per verification-discipline: every load-bearing claim traces to a named source that actually says what the claim says — open the source, don't trust the citation. Paraphrase drift (source says 'associated with', claim says 'causes') is a mismatch. Claims without a source are labeled inference/assumption, never presented as sourced fact.
- Tool protocol: `For each load-bearing claim: locate the exact passage in the cited source; record claim | source | passage | aligned yes/no.`

### source_quality (evidence)
Per research-methodology's source triangulation and verification-discipline's evidence grading: grade each source (primary data / peer-reviewed / reputable secondary / vendor-or-SEO / anonymous) and check independence — three articles citing the same press release are one source, not three. Load-bearing claims need at least one high-grade or two independent mid-grade sources.
- Tool protocol: `List sources with grade and independence lineage (who cites whom).`

### contradiction_handling (judgment)
Per adversarial-verify's alternative-explanation attack: actively search for sources that DISAGREE with the synthesis — the strongest contradicting source found must be named and either reconciled, weighed, or explicitly overruled with reasons. A synthesis that encountered zero contradictions usually means the search only looked where agreement lives.

### missing_evidence_scan (adversarial)
Per adversarial-verify and proactive-rigor: list what evidence WOULD exist if the conclusion were true but was not found (absence check), and what was not searched (coverage check). Per research-methodology: coverage claims must be honest — name the databases/queries/date-ranges actually searched, and the ones skipped.
- Tool protocol: `Enumerate expected-but-absent evidence and unsearched regions; attach the actual query list.`

### unsupported_inference (judgment) [disqualifying]
Per verification-discipline: audit every leap from evidence to conclusion — correlation presented as causation, one study presented as consensus, old data presented as current, sample presented as population. Each leap is either downgraded to its honest evidence level (fact / inference / assumption / guess) or removed. Never present one level as another.

### Adversarial tests
- Pick the report's single most load-bearing claim and try to kill it: find the strongest source arguing the opposite (adversarial-verify).
- Trace the three most-cited numbers to their PRIMARY origin; check whether they all collapse into one upstream source.
- Check every 'recent'/'current' claim against its source date — stale evidence presented as live state violates live-state-truth.
- Steelman the opposite conclusion from the same evidence set; if it reads equally well, the synthesis is underdetermined.

### Disqualifiers
- A load-bearing claim whose cited source does not contain it.
- Causation asserted where sources support only correlation.
- Coverage claimed ('the literature shows') without naming what was actually searched.
- Contradicting evidence known and silently omitted.
