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

## Domain: invention
### functional_feasibility (judgment) [disqualifying]
Per the invention-design program's feasibility verifier and adversarial-verify: attack the physics first, economics second, adoption third — energy/material/information budgets, scaling behavior at 10x, and the wrongness probe ('what would have to be true for this to be impossible?'). Every attack ends fixed, defended with evidence, or disclosed; per disclosure-is-not-a-fix, disclosure alone does not clear a disqualifying infeasibility.

### constraint_satisfaction (evidence) [disqualifying]
Per verification-discipline: check the design against every stated constraint (cost, size, power, materials, regulatory, interface) with numbers recomputed independently — a budget table, not adjectives. Constraints the design 'probably meets' are assumptions and must carry breaks-if-false notes.
- Tool protocol: `Tabulate constraint | required | design's value | margin; recompute independently.`

### mechanism_novelty (evidence)
Per invention-design's prior-art node and verification-discipline: 'novel' is a factual claim about the world and must be stated at its evidence level — 'no prior art found in searches X, Y, Z' is honest; 'unprecedented' is not. Identify the specific mechanism claimed as new and what distinguishes it from the nearest known mechanism.
- Tool protocol: `Name the nearest-neighbor prior mechanism and the exact delta.`

### prior_art_collision (evidence)
Per leverage-first and invention-design: search patents, products, papers, and open-source projects for the same mechanism before claiming it. Finding prior art is a win either way — a leverage-first shortcut or a map of the crowded region to design around. Record the actual queries run, per research-methodology's honest-coverage rule.
- Tool protocol: `List search venues + queries + nearest hits; collision = same mechanism solving same problem.`

### failure_mode_attack (adversarial)
Per failure-mode-awareness and adversarial-verify: enumerate how the invention fails — worst-case operating conditions, misuse by a naive user, degradation over time, the strongest domain-expert objection — and test the strongest attack for real, not rhetorically. Predict the failure before probing; an attack with no predicted outcome is an activity, not a test.
- Tool protocol: `For each failure mode: trigger condition | predicted failure | evidence or simulation | mitigation.`

### Adversarial tests
- Wrongness probe: state what would have to be true for the design to be impossible, then check whether it is (invention-design feasibility verifier).
- Scale the design 10x up and 10x down; find the first budget (energy, cost, heat, attention) that breaks (foresight).
- Hand the design to a hostile expert persona: write their single strongest objection and answer it with evidence, not assertion.
- Search prior art with the OPPOSITE vocabulary (different field's jargon for the same mechanism) — same-vocabulary searches miss the killer collision.

### Disqualifiers
- A physics/feasibility budget that does not close and is merely disclosed (disclosure-is-not-a-fix).
- A stated constraint the design numerically violates.
- Novelty claimed with no recorded prior-art search.
- A known failure mode with neither mitigation nor an explicit dated decision to accept it.

## Domain: mathematics
### independent_derivation (judgment) [disqualifying]
Per verification-discipline (recompute any arithmetic independently) and adversarial-verify's independent-recomputation attack: re-derive the result by a DIFFERENT route than the candidate used — different method, different decomposition, or different starting identity. Agreement via the same route is replication of the same error, not verification.

### numerical_substitution (deterministic) [disqualifying]
Substitute at least two concrete numeric values (one ordinary, one awkward — negative, fractional, large) into both sides of every derived identity/equation and confirm equality to tolerance. Per verification-discipline: this is arithmetic and must be recomputed, not eyeballed. The candidate must show the substitution, not assert it.
- Tool protocol: `regex:(?i)(substitut|plug(ging)?\s+in|numerical(ly)?\s+(check|verif)|both sides|x\s*=\s*-?\d)`

### symbolic_check (deterministic)
Where a CAS applies, verify the manipulation symbolically (sympy simplify/expand of LHS-RHS to zero) rather than trusting hand algebra — per empirical-validation, run the cheapest experiment that could falsify instead of reasoning about whether it works. Quote the tool output per live-state-truth.
- Tool protocol: `tokens:any:sympy,symbolic,simplify,expand,identity holds,lhs - rhs`

### boundary_behavior (adversarial)
Per adversarial-verify's edge-case attack: evaluate the result at the domain's boundaries — 0, 1, infinity/limits, degenerate cases (empty set, n=0, singular matrix), and points where denominators, logs, or square roots blow up. Each boundary either behaves as the claim predicts or is an explicit stated exclusion.
- Tool protocol: `Evaluate the expression/claim at each boundary point; record point | predicted | actual.`

### counterexample_search (adversarial) [disqualifying]
Per adversarial-verify: actively try to disprove the claim before presenting it. For universal claims ('for all n', 'always converges'), search small cases exhaustively and randomized cases broadly for a counterexample. One counterexample kills the claim regardless of how elegant the proof reads; failure to find one after a REAL search is stated at its evidence level per verification-discipline ('no counterexample found for n ≤ 10^6' is honest; 'shown' is not).
- Tool protocol: `Brute-force small cases + randomized sampling; report the search space actually covered.`

### Adversarial tests
- Substitute an awkward value (negative, irrational, huge) the derivation's implicit assumptions might not survive.
- Attack the weakest inference step: find the exact line where the proof would break if a sign or quantifier flipped.
- Check whether the claim silently assumes positivity, integrality, commutativity, or convergence that was never established.
- Run the smallest case by hand (n=0, n=1) — hand-checkable cases catch more derivation bugs than re-reading the algebra.

### Disqualifiers
- A counterexample exists within the claimed domain.
- Numerical substitution disagrees on both sides of a claimed identity.
- Independent re-derivation reaches a different result and the discrepancy is unresolved.
- Arithmetic asserted without independent recomputation.

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

## Domain: software
### tests_pass_with_quoted_output (deterministic) [disqualifying]
Per live-state-truth and debugging-playbook: run the relevant test suite and quote the ACTUAL output — 'should work now' is a prediction, not a result. The candidate must contain real captured test output, not a claim that tests would pass.
- Tool protocol: `regex:(?i)(\d+\s+(tests? )?passed|all tests pass(ed)?|\bOK\b|exit (code )?0|PASSED)`

### hidden_case_probe (adversarial)
Per adversarial-verify's edge-case attack: construct at least three inputs the author visibly did NOT test — empty/zero, boundary (max size, off-by-one), and malformed/hostile — and predict the behavior before executing. Any surprise is a finding; a probe whose outcome you couldn't predict wrong is an activity, not a test.
- Tool protocol: `Execute each probe input against the candidate code; record input | prediction | actual | verdict rows.`

### scope_diff_clean (deterministic) [disqualifying]
Per scope-fence and change-control: the diff touches only files and behavior named or implied by the task. Compare the changed-file list against the task's scope; every out-of-scope change is either reverted or explicitly flagged in an 'Out of scope — noted:' block, never silently included.
- Tool protocol: `cmd:git diff --stat — compare changed paths against task scope; not runnable from candidate text alone`

### regression_guard (deterministic) [disqualifying]
Per debugging-playbook's regression_test verifier: the previously-passing suite must still pass, and a new regression test encodes the fixed behavior so it cannot silently return — the regression test must fail on the pre-fix code. Quote both runs per live-state-truth.
- Tool protocol: `regex:(?i)(regression test|repro(duction)?.{0,40}passes|no previously.{0,15}(green|passing).{0,20}(red|fail)|suite still (green|passes))`

### interface_compatibility (evidence)
Per change-control and verification-discipline: enumerate every public interface the change touches (signatures, CLI flags, file formats, API contracts) and show evidence each caller/consumer still works or that the break is documented with a migration path. 'Nothing else uses this' is an assumption until grepped.
- Tool protocol: `grep for each changed public symbol across the repo; list callers and their status.`

### Adversarial tests
- Feed the empty/zero-length input and the maximum-size input; predict before running (adversarial-verify).
- Run the test suite on the PRE-change code: any 'new' test that already passes proves nothing (empirical-validation: the experiment must be able to falsify).
- Grep for callers of every changed public symbol; try to find one the author missed.
- Revert the fix and re-run the reproduction: if it still passes, the fix is not the cause (debugging-playbook toggle test).

### Disqualifiers
- Any claim of passing tests without quoted execution output.
- The regression test passes even without the fix applied.
- Silent out-of-scope changes in the diff.
- A previously-green test is now red.

## Domain: strategy
### causal_consistency (judgment) [disqualifying]
Per structured-reasoning and verification-discipline: walk the causal chain from action to claimed outcome and check every link is a mechanism, not a wish — 'we do X, therefore Y happens BECAUSE Z'. Any link that only works if an unstated actor cooperates or an unstated resource exists is an assumption and must be labeled with its breaks-if-false condition.

### constraint_fit (evidence) [disqualifying]
Per verification-discipline: check the plan against every stated constraint — budget, headcount, timeline, legal, technical capacity — with arithmetic recomputed independently. A plan that fits constraints 'roughly' has not been checked; show the numbers.
- Tool protocol: `Tabulate constraint | plan's demand | headroom; recompute all sums independently.`

### scenario_robustness (adversarial)
Per adversarial-verify and failure-mode-awareness: stress the strategy under at least three scenarios it was not designed for — the key assumption is wrong, the timeline doubles, the main resource halves. Per foresight: pre-register what breaks at 10x and what the plan regrets in 10 steps. A strategy robust only in its author's base case is a bet, not a plan.
- Tool protocol: `For each scenario: state the perturbation, trace the plan's behavior, record survives/degrades/dies.`

### incentive_response (adversarial)
Per adversarial-verify's hostile-reader attack applied to actors: for every party the strategy depends on (competitors, customers, regulators, internal teams), ask what their BEST response is once they observe the move — not their hoped-for response. Any step that requires a rational actor to act against their own interest is flagged as the plan's true risk.

### cheapest_discriminating_test (judgment) [disqualifying]
Per empirical-validation: before committing real resources, the strategy must name the cheapest real-world experiment that could FALSIFY its core bet — one with different predicted outcomes depending on whether the thesis is true (debugging-playbook's discriminating-test bar). Write the prediction before running it. A strategy with no falsifying test is unfalsifiable advocacy.
- Tool protocol: `Name the test, its cost, the pre-registered prediction, and the decision rule for each outcome.`

### Adversarial tests
- Assume the single most load-bearing assumption is false; check whether the strategy notices before the budget is spent (failure-mode-awareness).
- Play the strongest competitor's best counter-move on day one; re-trace the causal chain.
- Halve the key resource and double the timeline; check which milestones survive.
- Steelman the do-nothing baseline: if it beats the plan risk-adjusted, the plan fails (structured-reasoning).

### Disqualifiers
- A causal link that requires another actor to act against their own interest.
- A stated constraint the plan arithmetically violates.
- No falsifiable test of the core bet before major resource commitment.
- Success criteria that cannot be observed (empirical-validation: unmeasurable claims cannot be validated).

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
