# Near-miss example (must NOT fire)

**Case:** "Does the config file set the timeout to 30 seconds?" — the file was opened and read this session; the answer is "yes, line 14 sets `timeout: 30`."

**Why it must not fire:** every claim in the response was verified this session (counterindication). There is no unobserved or future state to calibrate.

**Why firing would hurt:** hedging an observed fact ("it appears the timeout may be 30 seconds") is its own miscalibration — it signals uncertainty that does not exist, erodes the reader's trust in plainly asserted facts, and makes genuinely uncertain claims elsewhere indistinguishable.
