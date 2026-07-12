# Eval plan — boundary-case-check

## Conditions
- **Treatment:** micro-skill content injected into the system context.
- **Baseline:** same model, same tasks, no injection.

## Grader
Deterministic checks (both verification conditions allow it):
1. Count of boundary cases actually executed with quoted real output ≥ 3.
2. Every failing case is either fixed (with a re-run shown) or converted into an explicit stated domain restriction.
A rubric judge additionally scores whether the three chosen cases were the most breakable ones (ranking honesty), including one hostile case for guards/filters.

## Task classes (where the failure mode naturally occurs)
1. **Regex/matching rules:** write an extraction or validation pattern for messy real-world strings (IDs, emails, log lines) with lurking case, boundary, and overlap traps.
2. **Small functions with edge-heavy domains:** date arithmetic, pagination math, percentage/ratio helpers where empty, zero, and max inputs break naive code.
3. **Guards and filters:** allowlist/denylist or sanitizer logic where a crafted hostile input is designed to slip through.
