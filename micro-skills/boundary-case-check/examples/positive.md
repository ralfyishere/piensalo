# Positive example

**Task (code review):** a teammate submits a regex to extract order IDs from logs: `ORD-\d+`.

**Trigger present:** the deliverable is a matching rule that will face log lines nobody typed by hand.

**Procedure applied:**
- Input domain: production log lines — mixed case (mobile client lowercases), concatenated fields, arbitrary surrounding text.
- Boundary candidates enumerated: empty string, lowercase IDs, embedded matches, huge lines, unicode, hostile overlap. Top three by breakage likelihood: empty string, lowercase, hostile overlap.
- Executed for real:
  1. Empty string → no match (correct; quoted run).
  2. `ord-123` → no match. FAIL — real logs contain lowercase. Fix: `(?i)ORD-\d+`.
  3. `XORD-999` → matches the `ORD-999` suffix. FAIL — added word boundaries: `\b(?i)ORD-\d+\b`. Re-ran all three: pass.

**Required output produced:**
Three named boundary cases with actual quoted outcomes attached to the review; both failures fixed and re-verified before approval.
