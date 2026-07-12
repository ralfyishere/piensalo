# Key — dev-05-greywater-recovery

Multiplicative recovery, not additive loss:
- Stage 1: 2000 * 0.90 = 1800 L/day
- Stage 2: 1800 * 0.85 = 1530 L/day
- Stage 3: 1530 * 0.80 = 1224 L/day
- Stage 4: 1224 * 0.75 = **918 L/day** usable

Net factor 0.90*0.85*0.80*0.75 = 0.459, so 2000 * 0.459 = 918 L/day.

Month (30 days): 918 * 30 = 27,540 L = **27.54 m³**.
Savings: 27.54 m³ * EUR 3.20/m³ = **EUR 88.13** (88.128 -> 88.13).

Correct summary lines:
```
RECOVERED_LPD: 918
RECOVERED_M3_MONTH: 27.54
SAVINGS_EUR_MONTH: 88.13
```

Trap: summing the losses (10+15+20+25 = 70% lost -> 30% passed) gives
600 L/day, 18.00 m³, EUR 57.60 — all wrong. Passing requires the compounded
918/27.54/88.13. Second trap: applying the four factors but then a one-step
unit slip (e.g. dividing by 100 instead of 1000, or forgetting the 30-day
multiply).
