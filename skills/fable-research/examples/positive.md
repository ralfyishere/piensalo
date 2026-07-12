# Positive example: the skill fires on conflicting reports

**Task:** "Ops says p99 is 120ms, the vendor dashboard says 480ms - which is right?"

Two sources disagree on a load-bearing number: exactly the trigger for fable-research. The skill fires and works the pipeline:

1. Question defined: p99 of what population, measured where, over what window.
2. Source grading: ops number = internal histogram, server-side, 24h, all routes (primary, high grade). Vendor number = client-side RUM, 7d, checkout route only (primary, high grade, different population).
3. Contradiction map: the two claims do not actually contradict - different measurement point (server vs client), route mix, and window. The contradiction is definitional, not factual.
4. Claim-level verification: recomputed server-side p99 for checkout-only, 7d: 210ms. Remaining 270ms gap = client network + JS, consistent with the RUM waterfall breakdown.
5. Verdict: both instruments are right about different things; the board-relevant number is client-observed checkout p99 (480ms), of which 210ms is server-addressable.
6. Coverage limits stated: mobile-app traffic absent from both instruments; verdict does not cover it.

Why this is the skill working: neither source was declared "wrong" by fiat; the reconciliation came from grading the instruments, mapping the definitional gap, and recomputing the discriminating number — and the verdict names what it does not cover.
