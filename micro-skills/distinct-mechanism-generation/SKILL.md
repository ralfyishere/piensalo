---
name: distinct-mechanism-generation
description: "When enumerating causes, ideas, or hypotheses, generate candidates that are distinct causal mechanisms — not paraphrases of the symptom or of each other — including classes with no lexical footprint in the evidence."
license: MIT
---

# distinct-mechanism-generation

**Trigger (observable):** The task asks for multiple explanations, causes, ideas, or hypotheses ('brainstorm', 'list possible causes', 'what could explain'), or a draft candidate list exists whose items restate the input's wording.

**When NOT to activate:** The hypothesis space is already saturated and validated candidates await application (switch from generation to applying known results); a single known-correct answer exists; candidate count was explicitly capped at one by the user.

## Procedure
1. Generate candidates as one-line mechanism claims — each names a causal path (X causes Y via Z), not a re-description of the symptom — and keep going until generation genuinely stalls.
2. Check pairwise distinctness: two candidates that differ only in wording but share the causal path collapse into one.
3. Explicitly scan for classes with no lexical footprint in the evidence: 'the fix already exists nearby for an adjacent case', 'the measurement is wrong', 'a third factor drives both observations' — these are the ones lexical anchoring misses.
4. Deepen only the top candidates with a grounded why and a falsifying test; keep the tail as one-line claims — breadth must not shrink when detail is added.
5. Cap per-candidate schema at claim/why/test during generation; demand credences only for finalists.

## Required output
A numbered candidate list where each entry is a distinct one-line mechanism; top candidates carry why + falsifying test; at least one candidate has no lexical overlap with the input's wording.

## Verification
- No two candidates share the same causal path (paraphrase pairs are collapsed).
- At least one candidate names a mechanism class with no lexical footprint in the input evidence.

**Known risk:** Padding with exotic mechanisms to hit distinctness while the mundane likely cause gets crowded out. Mitigation: distinctness prunes duplicates; it never mandates exotic additions.

**Max intended cost:** ≤400 added output tokens for the list; no tool calls required for generation itself.

**Evidence status:** DESIGNED — specified from documented reasoning-failure modes; not yet executed as a packaged skill.

**Lineage:** Derived from an evidence-backed breadth-without-depth-tax principle (adding detail to top candidates must not shrink the candidate set) and from a documented reasoning-failure mode — candidate lists that paraphrase the symptom instead of naming distinct causal mechanisms.
