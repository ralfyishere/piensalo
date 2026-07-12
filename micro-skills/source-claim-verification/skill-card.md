# source-claim-verification — skill card

## What it does
Stops diagnoses and decisions from resting on labels. Every load-bearing claim gets its provenance established: error strings are traced to the line that emits them (hardcoded catch-all vs derived from the real failure), claimed causes are checked against the facts that should co-occur with them (rate limiting should come with 429s and throttle headers), and onset timing is correlated with change events. Claims that survive cite a primary source; claims that don't are downgraded to unverified or replaced by what the primary source actually says.

## Trigger
- An error label names its own cause with unknown provenance: "rate limited", "quota exceeded", "timeout", "out of memory", "permission denied".
- A claim arrives as a summary of a source that could be opened directly: "the docs say", "the log shows", "the vendor reports", "according to...".
- A draft diagnosis rests on a label or summary with no primary-source trace.

## Counterindications
- Provenance was already established live this session (claim traced to its emitting line or primary document).
- The claim is decorative — nothing downstream depends on it.
- The primary source is genuinely unreachable; the claim gets an explicit unverified label instead of a trace.

## Negative-transfer risk
Provenance-tracing everything, including claims nothing depends on — turning every answer into a citation audit. The load-bearing filter runs first and decorative claims are left alone; still, distraction risk is medium because the procedure legitimately spends tool calls (greps, file opens) reaching emitting lines and primary documents.

## Evidence level
SMOKE_TESTED — executed end-to-end in live sessions and behaves as specified; no measured lift is claimed.
