---
name: source-claim-verification
description: "Trace each load-bearing claim to its primary source before believing it — especially self-labeled causes in error messages, logs, vendor explanations, and second-hand summaries. Activate when a diagnosis or decision is about to rest on a claim whose only support is a label, a log line, a doc/vendor statement, or someone's summary of a source you can open yourself."
license: MIT
---

# source-claim-verification

**Trigger (observable):** A diagnosis or decision is about to rest on a claim whose only support is a label ('rate limited', 'quota exceeded'), a log line, a doc/vendor statement, or someone's summary of a source you can open yourself.

**When NOT to activate:** The claim was already traced to its emitting line or primary document this session; the claim is decorative and nothing downstream depends on it; the primary source is genuinely inaccessible (then the claim is labeled unverified instead).

## Procedure
1. Identify the load-bearing claims and, for each, its actual provenance: computed observation, hardcoded string, secondary summary, or memory.
2. For error/log labels: trace the exact string to the line that emits it and check whether its content is derived from the real failure or hardcoded (a catch-all printing a fixed message explains nothing).
3. Collect the facts that should co-occur with the claimed cause (429s and throttle headers for rate limiting; quota usage for quota) and check they actually do — absence of co-occurring facts is evidence against the label.
4. Correlate onset timing with change events (deploys, version bumps, config changes) before accepting any steady-state explanation.
5. Claims that survive get their source cited; claims that don't are downgraded to unverified or replaced by what the primary source actually says.

## Required output
Per load-bearing claim: its primary source (file:line, document section, observed output) or an explicit unverified label; contradictions between label and co-occurring facts stated.

## Verification
- For error-label claims, the emitting line is cited and its hardcoded-vs-derived status stated (deterministic check).
- At least one fact that should co-occur with the claimed cause was checked against observation (deterministic check).
- No load-bearing claim in the final answer rests solely on a self-labeled cause or secondhand summary; each cites a primary source or wears the unverified tag.

**Known risk:** Provenance-tracing everything, including claims nothing depends on. Mitigation: load-bearing filter first; decorative claims are left alone.

**Max intended cost:** ≤300 added output tokens; a handful of greps/opens to reach emitting lines and primary docs.

**Evidence status:** SMOKE_TESTED — executed end-to-end in live sessions and behaves as specified; no measured lift is claimed.

**Lineage:** Distilled from an evidence-backed symptom-label-distrust repair pattern — error labels are claims about causes, not observations of them — and from a documented reasoning-failure mode: accepting the first plausible explanation and stopping.
