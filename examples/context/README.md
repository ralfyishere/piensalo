# PIENSALO Context — demo

Compile a long agent-session transcript into a **Continuation Capsule**: the
smallest task-specific packet that preserves critical decisions, constraints,
rejected approaches, exact artifacts, stop conditions, and the valid next
action — then verify that preservation deterministically.

Everything here runs offline: no model call, no network, no API key, no
provider SDK. The transcript could have been produced by any model or agent,
and `generated/resume.md` is plain text you can paste into any AI system.

## Run it

```sh
./demo.sh          # from this directory (uses piensalo, uv, or python3 -m)
```

`demo.sh` regenerates `generated/` from `transcript.txt` using the shipping
code — the committed files are program output, not handwritten. An anti-drift
test (`tests/test_context_example_parity.py`) recompiles the transcript and
fails if the committed output ever diverges from what the code produces.

## What the transcript plants, and what the capsule must do with it

| Planted in `transcript.txt` | Expected behavior (asserted by tests) |
|---|---|
| Early decision: shared cluster | `SUPERSEDED` — kept as historical truth, **never rendered as current** |
| Later decision: dedicated cluster | `ACTIVE`, carries the supersession link |
| Weekly release cadence | `CONTESTED` — surfaced as a conflict, not resolved by fiat |
| SSO hearsay | `UNVERIFIED` — carried, clearly not established truth |
| Redis response caching | `FAILED APPROACH` — preserved so it is not re-attempted |
| `services/widgets/src/store/pool.py`, `commit 4f2a9c1e7b3d5a20`, the exact deploy command, `250 ms at 400 rps`, the 0.5%/10-minute stop rule | EXACT — survive **byte-for-byte** |
| Long unstructured chatter | known omissions with content-hashed line references — **not invented into records**, still recoverable from the source |

## Honest limits

- `verification.json` verdicts cover deterministic structure only.
  **Behavioral equivalence is UNMEASURED** — nothing here claims a model
  resumed from the capsule behaves like a model given the full history.
- Token numbers are estimates (chars/4 heuristic, provider-independent).
  The gross compression ratio on this deliberately small example is modest;
  it grows with session length because typed consequences grow much slower
  than chatter. A smaller capsule is **not automatically a successful
  result** — the future economic test must count retrieval tokens,
  behavioral-verification tokens, latency, and net savings.
- `expected-active-state.json` is the hand-authored ground truth the tests
  compare against; `generated/` is machine output.
