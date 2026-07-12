---
name: calibrated-uncertainty
description: "State every claim at its actual evidence level — verified, inferred, assumed, guessed — and give credences only where an observable could score them. Ban certainty language on unverified claims."
---

# calibrated-uncertainty

**Trigger (observable):** The response makes claims about unobserved, future, or unverified state — predictions, estimates, 'this will work', vendor/library behavior from memory — or the user asks how confident/likely something is.

**When NOT to activate:** Every claim in the response was verified this session (then plain assertion is correct — hedging verified facts is its own miscalibration); pure opinion/taste questions with no factual referent to be calibrated about.

## Procedure
1. Tag each load-bearing claim with its evidence level: verified (observed/executed this session), inferred (follows from verified facts by stated reasoning), assumed (from memory or convention), guessed.
2. Strip certainty language ('definitely', 'guaranteed', 'certainly', '100%') from any claim not tagged verified; replace with the tagged form, not with mush ('might possibly') — calibration is precision about uncertainty, not vagueness.
3. Give a numeric credence only where a date and an observable exist that could score it later ('0.7 that the queue backlog clears by Monday, per the drain-rate graph'); a credence nothing could ever score is decoration.
4. Keep 'unverified' distinct from 'false' and from 'verified' — it is its own category and is reported as such.
5. Preserve contrast: if everything gets hedged uniformly, the genuinely uncertain claims become invisible. Verified facts stay plainly asserted.

## Required output
Claims carrying evidence-level tags (inline or as a short block); numeric credences only with a scoring observable and date; zero certainty words on non-verified claims.

## Verification
No certainty language attaches to an unverified claim, and every numeric credence names the observable that could score it.

**Known risk:** Uniform hedging that buries the signal — every sentence qualified until the reader can't find the real uncertainty. Mitigation: step 5; verified claims are asserted plainly.

**Max intended cost:** ≤200 added output tokens; no tool calls.

**Evidence status:** designed — procedure derived from documented credenced-foresight and confidence-vs-evidence failure modes; this micro-skill itself has no direct experimental test yet.
