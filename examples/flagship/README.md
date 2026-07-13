# Flagship demo: the inspect → repair → verify loop on a real pricing defect

`demo.sh` (offline, deterministic, no model calls) runs one realistic task — a Growth-plan
quote with two sequential discounts and a 50.00 USD minimum-charge floor — through the full
PIÉNSALO loop: inspect the broken draft (a repair is selected from observable evidence),
emit the honestly-labeled offline repair packet (nothing is applied), verify the broken
draft (the wrong total lands under FAILED), then inspect and verify the correct draft
(NO REPAIR NEEDED; CONTRACT VERIFIED + DETERMINISTICALLY VERIFIED; cognition stays UNMEASURED).

<!-- Derivation (computed with Python, not by hand):
     correct (compounded): 340.00 * 0.80 = 272.00, then 272.00 * 0.85 = 231.20
     broken  (added):      340.00 * (1 - 0.35)     = 221.00  <- 20% + 15% wrongly summed to 35%
     floor: both 231.20 and 221.00 are above 50.00, so FLOOR_APPLIED: NO either way. -->
The broken draft adds the discounts (35% off → 221.00); compounding them gives 231.20.
`TRANSCRIPT.md` is a committed capture of a real run; `tests/test_flagship_transcript.py`
reruns the demo and fails on any drift from it or from `expected-findings.json`.
