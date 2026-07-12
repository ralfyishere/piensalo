# Positive example — skill fires and repairs the output

**Task:** "Summarize the pilot results for the exec update: 1,240 of 8,300 invited users activated, and the draft says that's a 22% activation rate, up 5 points from last quarter's 17%."

**Trigger appears:** The draft asserts derived numbers (a percentage and a delta) that the update's headline claim rests on, with no visible recomputation.

**Procedure applied:**
1. Tagging: 1,240 activations and 8,300 invites are quoted (from the pilot dashboard); "22%" and "+5 points" are derived.
2. Independent recomputation by another route: 1,240 / 8,300 = 0.1494 → **14.9%**, not 22%. Cross-check: 22% of 8,300 would be 1,826 activations — inconsistent with the quoted 1,240.
3. Mismatch located before shipping: the 22% came from an earlier draft that used a 5,600-invite denominator (the first cohort only) — denominator drift, exactly the step-4 suspect.
4. Delta recomputed against last quarter's 17%: 14.9% is **down 2.1 points**, not up 5.

**Required output produced:**

> Activation: **14.9%** (derived: 1,240 activations / 8,300 invites — full-pilot denominator; an earlier 22% figure used only the first cohort's 5,600 invites). Versus last quarter's 17% (quoted, prior report): **−2.1 points**, not an increase. Headline corrected accordingly.
