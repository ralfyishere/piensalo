# Near-miss: when fable-build should NOT fire

**Task:** "Rename the variable `usr` to `user` in this 10-line function."

Nothing is broken, there is no symptom to capture, no hypothesis space, and no regression surface beyond the compiler/linter catching a missed reference.

Why firing would hurt: a full symptom-reproduction-hypothesis loop on a mechanical rename adds latency and ceremony (evidence tables for a change with no hypotheses), diluting attention from the one thing that matters - doing the rename cleanly.
