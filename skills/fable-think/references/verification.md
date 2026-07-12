# Verification criteria

Domain verification criteria. Deterministic criteria are checked mechanically; adversarial criteria require constructing probes; evidence criteria grade support quality. Disqualifying criteria fail the whole candidate.

## Domain: generic
### verification_evidence_present (deterministic) [disqualifying]
Per live-state-truth: any claim that something was run, checked, or measured must be accompanied by the actual quoted output — 'should work' is a prediction, not a result. The candidate must contain at least one block of real captured evidence for its central claim.
- Tool protocol: `regex:(?is)(```.{10,}```|output:|result:|actual:)`

### claim_labeling (evidence)
Per verification-discipline's check_assumptions verifier: every load-bearing claim is classified as fact (verified this session), inference (reasoning shown), assumption (stated with breaks-if-false), or guess (flagged) — and cheap upgrades are executed, not deferred. A claim whose origin cannot be named is a defect.
- Tool protocol: `List load-bearing claims; attach each one's evidence level and origin.`

### arithmetic_recompute (deterministic) [disqualifying]
Per verification-discipline: recompute any arithmetic independently before asserting it. Extract every computed number in the candidate and re-derive it from its stated inputs; any mismatch is a finding regardless of magnitude.
- Tool protocol: `Extract each computation's inputs and result; recompute with a calculator/script, not by eye.`

### adversarial_self_attack (adversarial)
Per adversarial-verify: before presenting, try to break the result — one edge case, one counterexample, one alternative explanation — and actually TEST the strongest attack rather than rehearsing it rhetorically. The candidate should show which attack was run and what happened.
- Tool protocol: `Run the single strongest attack; record attack | prediction | actual outcome.`

### uncertainty_disclosure (deterministic)
Per output-structuring and verification-discipline: important deliverables end by naming what remains uncertain or unverified — anything unchecked is named as unchecked. A deliverable claiming completeness with zero stated uncertainty is suspect by default.
- Tool protocol: `tokens:any:uncertain,unverified,not checked,unchecked,assumption,limitation,caveat`

### Adversarial tests
- Pick the candidate's most confident sentence and demand its evidence chain; confidence with no named origin fails verification-discipline.
- Re-run one claimed verification from scratch and diff against the quoted output (live-state-truth).
- Construct the cheapest input/scenario that could falsify the central claim and run it (empirical-validation).
- Alternative-explanation attack: write one other story consistent with the same evidence; check the candidate rules it out.

### Disqualifiers
- A 'verified'/'tested'/'done' claim with no quoted evidence.
- An arithmetic result that fails independent recomputation.
- An assumption presented as a verified fact.
- Completeness claimed while named checks were skipped.
