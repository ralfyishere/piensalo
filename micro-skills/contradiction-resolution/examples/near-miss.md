# Near-miss example (must NOT fire)

**Case:** a report states monthly revenue of $412k in one table and $389k in another — but the first table is labeled "calendar month, all regions" and the second "fiscal month, excluding EMEA," and the report says so.

**Why it must not fire:** the difference is fully explained by stated scope — different windows and populations, with the scoping already stated (counterindication).

**Why firing would hurt:** logging a "contradiction" between correctly scoped figures manufactures doubt where none exists, stalls the actual analysis, and trains readers to ignore the contradiction log when a real conflict appears.
