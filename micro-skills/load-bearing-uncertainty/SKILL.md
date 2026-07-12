---
name: load-bearing-uncertainty
description: "Identify which uncertain assumptions a conclusion actually rests on — the ones that flip the answer if wrong — state them explicitly, and attach the cheapest check to each. Activate when a recommendation, verdict, or go/no-go decision is being produced and at least one of its inputs is assumed or unverified rather than observed this session."
license: MIT
---

# load-bearing-uncertainty

**Trigger (observable):** A recommendation, verdict, or go/no-go decision is being produced, and at least one of its inputs is assumed or unverified rather than observed this session.

**When NOT to activate:** All inputs were verified this session; the output is exploratory brainstorming with no conclusion; the conclusion is insensitive to every assumption (checked, not presumed).

## Procedure
1. List the assumptions and unverified inputs the draft conclusion uses — including implicit ones (library behavior from memory, 'the script worked like last time', quoted numbers never recomputed).
2. For each, run the flip test: if this assumption is wrong, does the conclusion change? Partition into load-bearing (flips it) and decorative (doesn't).
3. For each load-bearing assumption, name the cheapest check that would settle it, and run any that cost less than being wrong.
4. State the load-bearing set explicitly next to the conclusion: 'This holds if A and B; if A is false, the answer inverts.'
5. Decorative assumptions get no airtime — listing them all dilutes the signal.

## Required output
The conclusion plus a short 'rests on' block: each load-bearing assumption, its status (verified / unverified), and its cheapest check.

## Verification
- The flip test was applied: assumptions are partitioned into load-bearing vs decorative, not listed indiscriminately (judgment check).
- The conclusion is accompanied by an explicit rests-on statement with per-assumption status (deterministic check).
- No load-bearing assumption is presented in the same register as verified fact.

**Known risk:** Hedging overload — surfacing every assumption instead of the flip set, making the answer read as evasive. Mitigation: step 5 caps the block to load-bearing items only.

**Max intended cost:** ≤250 added output tokens; checks run only when cheaper than the cost of a wrong conclusion.

**Evidence status:** DESIGNED — specified from documented reasoning-failure modes; not yet executed as a packaged skill.

**Lineage:** Distilled from two evidence-backed repair patterns — completion-integrity checking and credenced foresight with instrumentation — and from a documented reasoning-failure mode: confidence stated at a level the underlying evidence does not support.
