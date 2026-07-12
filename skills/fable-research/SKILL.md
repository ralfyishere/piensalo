---
name: fable-research
description: "Research and evidence-synthesis program: define the question, gather and grade sources, build a contradiction map, verify load-bearing claims at the claim level, and deliver a verdict with graded evidence. Use for 'what do we know about X', reconciling conflicting numbers or reports, literature or market questions, and any answer that must be assembled from multiple sources. Trigger phrases: 'research', 'reconcile these figures', 'what does the evidence say'."
license: MIT
---

# fable-research

A structured reasoning program for research and evidence synthesis, distilled from curated expert reasoning traces. Work the numbered steps in order; each step's output feeds the next. Do not skip steps silently - if one does not apply, say so in one line.

## Primary workflow
1. **Recover real objective** - Per intent-clarity: decode what the requester actually needs before optimizing anything. Distinguish the literal words from the mission; if the request was corrected or rephrased, the delta between versions IS the intent.
2. **Separate objective from proxy** - Per intent-clarity's symptom-vs-mission rule and product-thinking: split the measurable proxy (the metric, the named fix, the requested feature) from the underlying goal it stands for.
3. **Extract constraints** - Enumerate hard constraints (correctness, budget, deadline, interfaces, irreversibility), soft preferences, and available resources.
4. **Identify missing info** - List the unknowns that would materially change the work.
5. **Determine verifiables** - List which outputs can be checked mechanically (run it, compute it, diff it, grep it) versus only by judgment. Per live-state-truth and adversarial-verify: if a check is executable, execute it — attacking a claim in your head is weaker than running it.
6. **Decompose claims** - Decompose the research question into individually checkable claims and sub-questions (deep-decomposition applied to knowledge: each leaf is a claim one source-check could settle).
7. **Gather sources** - Per research-methodology: run a deliberate search strategy per claim — vary terms, venues, and viewpoints; deliberately search for DISCONFIRMING sources, not just supporting ones. Record for each source: origin, date, and how it was found.
8. **Assess source quality** - Per structured-reasoning's evidence-grading frame and verification-discipline: rank each source — primary data > strong secondary > weak secondary > anecdote > speculation — and record recency, independence (does it merely cite another source in the pool?), and incentive to distort.
9. **Build contradiction map** - For each claim, tabulate which sources support, contradict, or are silent.
10. **Build evidence table** - Assemble the master table: claim | verdict (supported / contested / refuted / unknown) | best evidence for | best evidence against | grade | as-of date.
11. **Missing evidence** - Name what the synthesis does NOT cover: claims with no independent source, populations/timeframes never sampled, the search that was not run.
12. **Claim level verification** - Per adversarial-verify, attack the synthesis claim by claim, not as a whole: for each 'supported' verdict run the wrongness probe ('what would have to be true for this to be wrong?') and re-read the primary source for the load-bearing quote — the compression step is where distortion enters (verification-discipline).
13. **Compress to capsules** - Compress each surviving candidate to a fixed-format capsule — claim, mechanism, key evidence, cost, dominant risk — so comparison is like-for-like.
14. **Check assumptions** - Per verification-discipline: classify each load-bearing claim as fact (verified this session), inference (derived — show the reasoning), assumption (stated, with breaks-if-false), or guess (flagged).
15. **Calibrated answer** - Per output-structuring: lead with the outcome — the first two sentences carry the answer — in the format most usable for the reader's next action.

## Conditional moves
- When a load-bearing verdict lost its source support: return to **Gather sources** and rework from there.
- When contradiction unresolvable without a missing source type: return to **Gather sources** and rework from there.
- When a gap's cheapest check is a search that fits remaining budget: return to **Gather sources** and rework from there.

## Output contract
A cited synthesis: claim-level evidence table (claim | verdict | best evidence for/against | source grade | as-of date), contradiction map with reconciliations, explicit coverage-gap list with cheapest closing checks, and a conclusion whose confidence never exceeds its graded evidence.

## Delivery notes (small-model packets)
If delegating steps to a smaller model, follow the small-model packet rules: one bounded objective per packet, all inputs named explicitly, facts separated from instructions, uncertainty marked 'UNCERTAIN: ...' rather than invented away.

## Before answering
Check the draft against references/failure-checks.md (the failure-mode catalog) and references/verification.md (domain verification criteria). Repair procedures live in references/contracts.md.
