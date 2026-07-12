# Key — dev-07-calibration-windows

Run = 300 minutes.
- Complete 45-minute windows: 300 // 45 = 6 (covering 270 minutes).
- Leftover partial window: 300 - 270 = **30 minutes**.
- Rule: extra calibration if the partial is **at least 30 minutes**. 30 >= 30
  is TRUE, so the leftover triggers one extra.

Total = 6 + 1 = **7**. Correct line: `CALIBRATIONS: 7`.

Boundary trap: the leftover is exactly the 30-minute threshold. The obvious
answers miss it —
- "6 full windows, so 6" ignores the leftover entirely.
- reading the rule as "more than 30 minutes" excludes the exact-30 case and
  gives 6.
Both are wrong. "At least 30" includes exactly 30, so the answer is 7.

Grader note (hardened during public port): the anchored CALIBRATIONS value is
parsed on decoration-stripped lines and is authoritative when present, so a
correct WORKING mention of "6 complete windows" can never veto an anchored 7.
The prose fallback only fires when no anchored line exists, only confirms an
explicit total, and treats 6 as a veto trap value.
