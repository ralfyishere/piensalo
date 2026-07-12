# Failure checks

A catalog of weak-model failure signatures, ordered most-relevant-first for this skill. Before finalizing, scan the draft against each signature; on a hit, apply the repair contract(s) in references/contracts.md.

## proxy-solving (severity: high)
- Signature: Optimizes the stated metric or KPI without ever questioning whether it measures the real objective
- Signature: Proposes fixes for a number that is partly measurement artifact
- Signature: Kill/ship decisions cite the metric as ground truth with no instrument check
- Check: Did the response name at least one hypothesis in which the metric itself is wrong (censoring, denominator drift, benign-case miscounting)?
- Check: Was any cheap probe of the instrument sequenced BEFORE fixes to the measured system?
- Repair: RC-01-diagnose-the-ruler, RC-10-mission-gradient-over-urgency (see references/contracts.md)

## first-representation-acceptance (severity: high)
- Signature: Adopts the problem framing, schema, or ontology exactly as handed over and never revisits it
- Signature: Merges concepts because they co-occur in the input, without checking lifecycles
- Signature: Names components after the system they serve rather than what they do
- Check: Was an alternative framing or decomposition considered before committing?
- Check: For any unified concepts: do created-when / update-rule / retired-when / who-acts-on-it all match?
- Repair: RC-13-operational-semantics-ontology, RC-02-kills-close-hypotheses-not-spaces (see references/contracts.md)

## paraphrase-not-mechanisms (severity: medium)
- Signature: Candidate lists restate the evidence's surface wording instead of naming causal mechanisms
- Signature: Systematically misses candidates far from the input's vocabulary (e.g. 'the fix already exists in-repo for an adjacent case')
- Signature: Explanations describe WHAT happened in new words rather than WHY it happened
- Check: Does each candidate name a mechanism (a causal path) rather than re-describing the symptom?
- Check: Are any candidates drawn from classes with no lexical footprint in the input?
- Repair: RC-05-breadth-without-depth-tax, RC-15-verdict-first-synthesis-from-failure (see references/contracts.md)

## confidence-vs-evidence (severity: critical)
- Signature: Certainty of tone uncorrelated with strength of evidence; 'definitely' attached to guesses
- Signature: Verified, unverified, and assumed claims presented in the same register
- Signature: Rounds 9/10 verified up to 'done'; unverified merged into either 'passed' or 'failed'
- Check: Is every claim tagged (or taggable) as verified / unverified / inferred / assumed?
- Check: Does any 'done' claim cover an item that was never checked?
- Repair: RC-07-completion-integrity, RC-12-credenced-foresight-with-instrumentation (see references/contracts.md)

## non-discriminating-tests (severity: high)
- Signature: One confirmatory test per hypothesis ('add logging', 'increase coverage')
- Signature: Proposed tests whose every possible outcome is consistent with several hypotheses
- Signature: No pre-stated mapping from result to verdict before the experiment runs
- Check: For each proposed test: which hypotheses does each possible outcome kill?
- Check: Does a discrimination table (result row -> verdict) exist before the run?
- Repair: RC-04-unifying-discriminant (see references/contracts.md)

## performative-tool-use (severity: medium)
- Signature: Re-reads, listings, and exploratory greps whose results never change the answer
- Signature: Tool calls performed as ritual evidence of diligence rather than to resolve a pending decision
- Signature: Inverse form: answers about current state without reading it at all
- Check: Which tool calls in the trajectory produced results unused in the final answer?
- Check: Was any load-bearing named input never read?
- Repair: RC-14-minimal-tool-footprint (see references/contracts.md)

## syntax-not-semantics-verification (severity: high)
- Signature: Checks form (file exists, JSON parses, table present, credences present) and declares the substance correct
- Signature: Produces the required artifact shape without the selection judgment it was meant to carry
- Signature: Validators verify formatting while the invariant they exist for silently fails
- Check: Would this check have caught the historical failures it was built from (retro-run)?
- Check: Does the verification test the meaning (right discriminant chosen, right column differs) or only the format?
- Repair: RC-06-determinize-dont-rediscover, RC-13-operational-semantics-ontology, RC-07-completion-integrity (see references/contracts.md)

## plausible-and-stop (severity: high)
- Signature: Accepts the first explanation that fits the visible facts; search halts at plausibility
- Signature: Takes error labels, log lines, and vendor explanations at their word
- Signature: No check for facts that should co-occur with the claimed cause but don't
- Check: Was the error string traced to the emitting line and checked for hardcoding?
- Check: Which facts should co-occur with the claimed cause, and were they observed?
- Repair: RC-03-symptom-label-distrust, RC-04-unifying-discriminant (see references/contracts.md)

## boundary-ignoring (severity: critical)
- Signature: Exceeds granted scope: executes what it was asked to reason about, edits what it was asked to review
- Signature: Attempts ungranted tools/permissions repeatedly until the session dies on limits
- Signature: Silently fixes adjacent defects found en route instead of reporting them
- Check: Were granted tools/permissions checked against the task's implied actions before starting?
- Check: Is there an explicit NOT-do list, and were adjacent defects reported rather than fixed?
- Repair: RC-14-minimal-tool-footprint, RC-09-explicit-negative-space (see references/contracts.md)

## local-optimization-harm (severity: high)
- Signature: Optimizes the component in front of it at the expense of the system (speed here, correctness there)
- Signature: Picks the urgent/visible item over the mission-central or gating one
- Signature: Cleanup and repair run before diagnosis (blind dedupe, killed in-flight jobs, deleted rollback paths)
- Check: Which direction of error is cheaper given the system's actual detection/recovery machinery?
- Check: Does the chosen action unblock others, or is it an isolated visible win?
- Repair: RC-10-mission-gradient-over-urgency, RC-09-explicit-negative-space (see references/contracts.md)

## overbuild-before-bottleneck (severity: medium)
- Signature: Builds frameworks, dashboards, abstractions, or infrastructure before the constraint that would justify them binds
- Signature: Capacity math for the far future while the in-window binding constraint goes unaddressed
- Signature: Glamour work (novel builds) chosen over burden-reducing or evidence-capturing work
- Check: Which constraint binds inside the decision window, and does this build address it?
- Check: What perishable evidence or baseline must be instrumented NOW because it cannot be reconstructed later?
- Repair: RC-10-mission-gradient-over-urgency, RC-12-credenced-foresight-with-instrumentation (see references/contracts.md)

## absence-as-negative (severity: high)
- Signature: Treats 'not observed' as 'not present' and 'unverified' as 'failed' (or as 'passed')
- Signature: Treats a kill-list as covering the whole hypothesis space when it only covers tested points
- Signature: Grades empty/quota-stub/harness-death outputs as capability failures
- Check: Did each kill falsify the mechanism, or only one implementation/message/measurement of it?
- Check: Are NOT-RUN / INVALID cells separated from FAIL cells?
- Repair: RC-02-kills-close-hypotheses-not-spaces, RC-07-completion-integrity, RC-15-verdict-first-synthesis-from-failure (see references/contracts.md)

## unresolved-contradictions (severity: high)
- Signature: Notices (or half-notices) conflicting facts and proceeds without resolving or logging them
- Signature: Contradiction between live evidence and the standing verdict is explained away or ignored
- Signature: Handoff-document claims accepted while live signals disagree
- Check: What is the strongest live contradiction to the current belief, stated in one sentence?
- Check: Was every document-vs-reality discrepancy logged, including ones that don't change the plan?
- Repair: RC-02-kills-close-hypotheses-not-spaces, RC-08-live-state-over-plan-markers (see references/contracts.md)

## novelty-without-feasibility (severity: medium)
- Signature: Keeps generating novel ideas after the space is exhausted instead of applying what is known
- Signature: Proposals carry no cost, mechanism, horizon, or observable that could ever validate them
- Signature: Ideas selected for interestingness; the boring known-good fix is never shortlisted
- Check: Is the space saturated — should effort switch from generation to applying known results?
- Check: Does each novel proposal carry a mechanism, cost, and falsifying observable?
- Repair: RC-11-saturation-recognition, RC-12-credenced-foresight-with-instrumentation (see references/contracts.md)

## critique-without-synthesis (severity: medium)
- Signature: Falsifies, criticizes, or kills options without generating replacements
- Signature: Failure reports say 'it failed' with no ranked causes at stated confidence and no next changes
- Signature: Verdicts buried under caveats, or rescued post-hoc, instead of stated first and mined for information
- Check: Does the report state the verdict first, then convert each supported cause into one concrete next change?
- Check: For every killed option, was a candidate from an untested mechanism class generated?
- Repair: RC-15-verdict-first-synthesis-from-failure, RC-02-kills-close-hypotheses-not-spaces (see references/contracts.md)

## complexity-without-benefit (severity: medium)
- Signature: Adds abstractions, config layers, or always-on rules whose absence would change nothing observable
- Signature: Absorbs corrections as ever-longer prose/prompts instead of deterministic gates
- Signature: Rich per-item schemas imposed at generation time, cutting throughput without improving outcomes
- Check: What observable behavior changes if this added element is deleted?
- Check: Could a generated artifact or blocking validator replace this advisory prose?
- Repair: RC-06-determinize-dont-rediscover, RC-14-minimal-tool-footprint, RC-05-breadth-without-depth-tax (see references/contracts.md)
