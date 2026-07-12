# Positive example: the skill fires on a high-stakes summary

**Task:** "Write the 200-word exec summary of Tuesday's outage postmortem."

High-stakes prose with a hard length limit where every number must be defensible: exactly the trigger for piensalo-write. The skill fires and works the pipeline:

1. Claim ledger built first (each with source): 47 min downtime (monitoring), 3.2% of daily orders affected (order DB query), root cause = expired internal TLS cert (incident doc), no customer data exposed (security review sign-off), fix = automated renewal + expiry alerting (merged PR).
2. Constraint checklist: <=200 words; no blame language; every number sourced; must state what is NOT yet done.
3. Draft divergence: two openings tried - timeline-first vs impact-first; impact-first wins (exec audience acts on impact).
4. Critic passes, separately: argument pass (does the summary support its own 'resolved' claim? -> weakened to 'mitigated; renewal automation ships Friday'); accuracy pass (3.2% recomputed from raw counts: 3.18%, rounds fine); style pass (removed passive voice in two sentences).
5. Compression pass: 231 -> 198 words; ledger re-checked after compression - all five claims still present, none mutated.
6. Delivered with the ledger appended so reviewers can audit each claim's source.

Why this is the skill working: the ledger existed before the first draft, the critic passes ran separately instead of as one merged "review", and compression was verified against the ledger rather than trusted.
