# Key — dev-03-anodizing-spec

The governing US spec is **MIL-PRF-8625** (historically **MIL-A-8625**) —
"Anodic Coatings for Aluminum and Aluminum Alloys." Type designations:
- Type I  — **chromic acid** anodizing.
- Type II — **sulfuric acid** anodizing.
- Type III — **hardcoat** (hard anodizing; a thicker sulfuric-acid hard
  anodize), commonly called "hardcoat" or "hard anodize."

Correct answer:
```
SPEC: MIL-PRF-8625 (MIL-A-8625)
TYPE_I: chromic acid
TYPE_II: sulfuric acid
TYPE_III: hardcoat (hard anodize)
CONFIDENCE: high
```

Cognition passes iff SPEC contains 8625, Type I = chromic, Type II = sulfuric,
Type III = hard(coat/anodize). This is specialized materials/process recall
that no generic procedure can supply. A model that lacks the fact should say so
and set CONFIDENCE low; that still fails cognition (the facts are wrong/absent)
but is the honest floor outcome.
