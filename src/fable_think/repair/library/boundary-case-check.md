---
name: boundary-case-check
description: "For any rule-like deliverable — code, regex, query, formula, validator, policy — enumerate the boundary inputs (empty, zero, one, max, duplicate, malformed, hostile) and actually exercise the most breakable three before shipping."
---

# boundary-case-check

**Trigger (observable):** The deliverable is executable or rule-like: a function, regex, SQL query, spreadsheet formula, matching rule, allowlist/denylist, or threshold policy that will meet inputs the author didn't type.

**When NOT to activate:** Pure prose deliverables with no input domain; throwaway one-off commands already run against their only real input; boundaries already covered by an existing executed test suite named in the session.

## Procedure
1. Write down the input domain the artifact will actually face — types, ranges, encodings, adversarial sources — not just the examples in the prompt.
2. Enumerate boundary candidates mechanically: empty, zero, one element, duplicates, maximum size, negative, unicode/odd encoding, wrong type, and (for guards/filters) the hostile input designed to slip through.
3. Rank by breakage likelihood and pick the top three.
4. Exercise them for real — run the code, test the regex against the string, execute the query on edge rows. A predicted outcome is not a result; quote actual output.
5. Report the three outcomes with the artifact; fix or scope-document any failure before shipping.

## Required output
Three named boundary cases with actual (not predicted) outcomes, attached to the deliverable; failures fixed or the artifact's valid domain narrowed explicitly.

## Verification
At least three boundary cases were executed with quoted output, and any failing case is resolved or the limitation is a stated domain restriction, not a silent gap.

**Known risk:** False confidence from testing three convenient edges rather than the three most breakable ones. Mitigation: the ranking step, plus one hostile case being mandatory for guards.

**Max intended cost:** ≤250 added output tokens; three real executions.

**Evidence status:** designed — procedure derived from documented plausible-and-stop and syntax-not-semantics verification failure modes; this micro-skill itself has no direct experimental test yet.
