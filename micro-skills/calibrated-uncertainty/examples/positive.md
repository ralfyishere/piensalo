# Positive example

**Draft under review:** "The fix definitely resolves the memory leak and will hold at production load."

**Trigger present:** the second half is a claim about future, unobserved state ("will hold at production load"), and a certainty word spans both claims.

**Procedure applied:**
- "Resolves the leak": tagged VERIFIED — heap profile stayed flat over a 2-hour replay of Tuesday's traffic, run this session. Stays plainly asserted.
- "Holds at production load": tagged INFERRED — the replay peaked at 60% of production QPS; the extrapolation assumes allocation scales linearly.
- Credence attached only because an observable exists: 0.8 that it holds through Friday's peak, scored by the 18:00 heap alert staying silent.
- "Definitely" removed from the unverified claim; no mush substituted.

**Required output produced:**
"The fix resolves the leak — verified by a flat heap profile over a 2h traffic replay run today. Holding at full production load is inferred, not verified: the replay peaked at 60% of production QPS. Credence 0.8 it holds through Friday's peak; the 18:00 heap alert is the scorer."
