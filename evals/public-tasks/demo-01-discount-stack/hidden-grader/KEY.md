# Key — demo-01-discount-stack

Sequential (multiplicative) discounts, not additive:
- After 30%: 250.00 * 0.70 = 175.00
- After 20%: 175.00 * 0.80 = 140.00
- After 10%: 140.00 * 0.90 = **126.00**

Correct line: `FINAL_PRICE: 126.00`.

Trap: adding the discounts (30 + 20 + 10 = 60% off) gives 250.00 * 0.40 =
100.00 — wrong. The grader treats 100 as a veto trap value in the prose
fallback and never infers the answer from mentions of the list price or the
percentages.
