# Near-miss: when piensalo should NOT fire

**Task:** "What HTTP status code means 'not found'?"

This is a single-step factual lookup with a deterministic, instantly checkable answer (404). There is no proxy to separate, no contradiction to extract, no candidate space to discriminate.

Why firing would hurt: running the full loop here adds latency and produces hedged, scaffolded output ("confidence per component") for a question with exactly one correct answer - pure dilution, no gain.
