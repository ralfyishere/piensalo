# Near-miss example (must NOT fire)

**Case:** "The report total looks off — it might be a rounding issue." One hypothesis, and recomputing the total by hand takes ten seconds.

**Why it must not fire:** only one live hypothesis exists (counterindication), and the single available check is near-free — running it beats designing anything.

**Why firing would hurt:** building a discrimination table for one hypothesis is pure ceremony; the ten-second recomputation would already be done before the table's first row was written, and the table adds tokens without eliminating anything.
