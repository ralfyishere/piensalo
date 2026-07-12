# Positive example: the skill fires on a mechanism-design brief

**Task:** "Design a device that opens a greenhouse vent when it gets hot - no electricity, no user action."

An unpowered actuation mechanism must be designed to quantitative requirements: exactly the trigger for piensalo-invent. The skill fires and works the pipeline:

1. Physics-level requirements: actuation force ~20N over ~10cm stroke, trigger band 24-30C, cycle life >5k, unpowered.
2. Prior art check: paraffin-wax thermal actuators are standard commercial practice for exactly this - so NOVELTY IS NOT CLAIMED; the task becomes selection + integration.
3. Distinct mechanisms considered anyway (different operating principles): (a) wax-motor piston, (b) bimetallic coil, (c) gas-charged cylinder (vapor pressure).
4. Feasibility attack with numbers: (b) bimetal delivers ~2N at this scale - two orders short, killed. (c) gas charge drifts with ambient pressure (~10% force error per 100hPa), marginal for the 6C trigger band. (a) wax expansion ~15% over the band, easily 20N through a piston - survives.
5. Design: wax-motor cylinder + lever (3:1 stroke amplification) + return spring; fail-safe analysis: wax leak -> vent stays open (safe direction for plants).
6. Honest claims: mechanism selection and sizing are calculated; cycle-life figure is a vendor datasheet value, labeled as unverified here.

Why this is the skill working: candidates were killed with numbers, not vibes; prior art demoted the novelty claim honestly; and the fail-safe direction was analyzed rather than assumed.
