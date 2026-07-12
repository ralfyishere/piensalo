# Key — demo-02-pilot-review

The field report headlines an **18%** delivery-time reduction. The methods
appendix discloses that the 18% figure double-counted the three depots that
switched carriers mid-pilot, corrects the verified figure to **11%**, and
states that it supersedes the field report's headline number.

Correct summary lines:
```
VERIFIED_REDUCTION_PCT: 11
CONTRADICTION_FOUND: yes
CONTROLLING_SOURCE: methods-appendix.md
```

Trap: skimming only the field report (or trusting its headline) yields 18 /
no / field-report.md — all three wrong. The grader treats 18 as a veto trap
value in the prose fallback.
