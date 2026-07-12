# Near-miss example — skill must NOT fire

**Task:** "Earlier this session we traced the 'quota exceeded' error to the billing service's emitting line and confirmed the account's usage dashboard shows 100% of quota consumed. Now write the incident summary."

**Why it must not fire:** This matches a counterindication: provenance was already established live this session — the label was traced to its emitting line and the co-occurring fact (quota usage at 100%) was observed. There is nothing left to verify.

**Why firing would hurt:** Re-tracing an already-verified claim burns tool calls and delays the actual deliverable (the summary), while adding redundant citation scaffolding that makes the write-up longer without making it one bit more true.
