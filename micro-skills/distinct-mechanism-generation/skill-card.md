# distinct-mechanism-generation — skill card

## What it does
When the task calls for multiple explanations, causes, or ideas, it forces each candidate to be a distinct causal mechanism (X causes Y via Z) rather than a paraphrase of the symptom or of another candidate. It also mandates a scan for mechanism classes with no lexical footprint in the evidence — wrong measurement, common cause, an adjacent existing fix — which lexical anchoring systematically misses. Top candidates get a grounded why and a falsifying test; the tail stays as one-liners so breadth survives.

## Trigger
- The task asks for multiple candidate explanations, causes, ideas, or hypotheses ('brainstorm', 'list possible causes', 'what could explain', 'enumerate').
- A draft candidate list re-describes the symptom or its own entries rather than naming distinct mechanisms (e.g. a list of '<noun> issues' entries).

## Counterindications
- The hypothesis space is saturated and validated candidates await application — switch from generating novelty to applying known results.
- A single known-correct answer exists; enumeration is theater.
- The user explicitly capped the candidate count at one.

## Negative-transfer risk
Distraction risk: medium. The failure mode is padding the list with exotic mechanisms to satisfy distinctness while the mundane likely cause gets crowded out. The rule is asymmetric by design: distinctness prunes duplicates, it never mandates exotic additions.

## Evidence level
DESIGNED — specified from documented reasoning-failure modes; not yet executed as a packaged skill.
