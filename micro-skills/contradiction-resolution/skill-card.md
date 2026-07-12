# contradiction-resolution — skill card

## What it does
When inputs conflict, stops and resolves the conflict explicitly: states each contradiction in one sentence with both sources named, classifies it (transcription error / version skew / scope difference / stale source / genuine conflict), applies a named resolution rule (live state beats documents; recomputation beats quotation; fresher primary beats older secondary), downgrades a discredited source's other claims to unverified, and attaches explicit caveats to anything left unresolved.

## Trigger
- Text flags disagreement: "contradicts", "inconsistent", "conflicts", "doesn't match", "but the dashboard says/shows/reports".
- Two inputs state different values for the same named quantity.
- Post-draft signal: a conclusion uses one side of a detected conflict without resolution or caveat.

## Counterindications
- The difference is explained by stated scope — different windows, units, or populations, with the scoping already stated.
- The differing values are experimental arms or deliberate counterfactuals meant to differ.
- Pure opinion differences with no factual referent.

## Negative-transfer risk
Medium distraction risk. Main failure mode: contradiction-hunting in noisy data where trivial mismatches (rounding, timestamps) stall real work — the classification step routes trivia to one-line closure. Do not treat intentional variants as conflicts.

## Evidence level
SMOKE_TESTED
