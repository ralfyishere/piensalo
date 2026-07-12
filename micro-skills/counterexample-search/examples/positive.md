# Positive example — code review with a universal claim

**Task:** Review a `dedupe_emails(list)` helper and summarize its guarantees.

**Draft before the skill fires:**
> The function always returns a list with no duplicate addresses, for any input.

**Trigger appears:** "always ... for any input" — a universal claim about all inputs.

**Procedure applied:**
1. Universal claim extracted verbatim: "always returns a list with no duplicate addresses, for any input."
2. Domain: lists of strings. Edges: empty list, single element, case variants, whitespace variants, non-string entries.
3. Strongest candidate: `["A@x.com", "a@x.com "]` — same address in different case with a trailing space. Traced through the code: the function lowercases but does not strip whitespace, so both entries survive.
4. Counterexample found → claim weakened.

**Required output produced:**
- Claim: "always deduplicates for any input"
- Strongest counterexample candidate: `["A@x.com", "a@x.com "]` (case + trailing-space variant)
- Result: traced — both entries survive; duplicate remains
- Disposition: **weakened** to "deduplicates exact-and-case-variant addresses; whitespace variants are not normalized" (with a suggested `strip()` fix if the stronger guarantee is wanted).
