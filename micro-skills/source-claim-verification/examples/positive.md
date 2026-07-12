# Positive example — skill fires and repairs the output

**Task:** "The nightly sync job keeps failing with 'rate limited by upstream'. Add exponential backoff to fix it."

**Trigger appears:** The proposed fix rests entirely on a self-labeled cause — an error string claiming "rate limited" — whose provenance is unknown.

**Procedure applied:**
1. Load-bearing claim: the upstream API is rate-limiting us. Provenance: a log string only.
2. Trace the string: grep finds it in the sync client's catch-all handler — `except RequestError: log("rate limited by upstream")` — a hardcoded message printed for every request failure. It explains nothing.
3. Co-occurrence check: real rate limiting should show HTTP 429s and Retry-After headers. The raw response logs show HTTP 401 Unauthorized, zero 429s.
4. Timing: failures began the same night the upstream API key was rotated in the config store.

**Required output produced:**

> Claim "rate limited by upstream" — **rejected**. Source: hardcoded string in the sync client's catch-all exception handler (client module, error branch), printed for any request failure. Co-occurring facts contradict the label: responses are 401 Unauthorized, no 429s, no throttle headers. Onset coincides with the key rotation. Actual cause: stale API key. Backoff would not fix this — refreshing the credential does. (Backoff request set aside; say the word if you still want it for genuine throttling.)
