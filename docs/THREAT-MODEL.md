# Threat Model

What can go wrong when an AI system reads untrusted text, holds state, calls
models, and acts — and what Piénsalo does about each. Every entry lists the
mitigation **and the residual risk**, because a threat model that claims zero
residual risk is marketing.

Scope: the `piensalo` runtime, skill loader, state store, adapters, and
evaluation tooling. The security defaults these mitigations rest on are in
[SECURITY.md](../SECURITY.md).

---

### T1 · Prompt injection

*Untrusted content (task inputs, fetched documents, tool output) contains
instructions the model may follow.*

**Mitigation:** untrusted content is delimited and labeled as data in every
prompt the runtime constructs; instructions from content can never trigger
tool execution directly — actions pass through the operator-boundary layer
([docs/operator-boundaries.md](operator-boundaries.md)), and destructive
ones require approval. Inspection treats "output follows embedded
instructions" as a classifiable failure.

**Residual risk:** high. Injection is an unsolved problem for every LLM
system; delimiting reduces, does not eliminate, compliance with embedded
instructions. Assume any sufficiently motivated injected text can steer
*non-actioned* output.

### T2 · Malicious skill packages

*A third-party skill contains harmful instructions, embedded commands, or
exfiltration attempts.*

**Mitigation:** skills are inert text — the loader never executes code from
skill files ([docs/skill-security.md](skill-security.md)).
`piensalo skill scan` flags command patterns, network references,
obfuscation, and secret-shaped strings before install. No unreviewed skill
marketplace exists or is planned.

**Residual risk:** medium. A skill can still *persuade* a model into bad
non-actioned output, and scanners miss novel obfuscation. Install skills like
you install dependencies: read them.

### T3 · Reference poisoning

*A skill or task references external files/URLs whose content changes after
review, altering behavior post-install.*

**Mitigation:** `skill scan` flags external references; skills are encouraged
to be self-contained; the core never fetches URLs (no network without an
explicit adapter).

**Residual risk:** medium-low. A user who configures an adapter and a skill
that requests fetching reintroduces the risk; the boundary is the explicit
adapter, not the impossibility of fetching.

### T4 · Path traversal

*Skill names, task ids, or model output containing `../` or absolute paths
cause reads/writes outside the workspace.*

**Mitigation:** all state paths are resolved and verified to remain under
`.piensalo/` (or the explicitly configured root) before any I/O; traversal
sequences in identifiers are rejected, not sanitized.

**Residual risk:** low, bounded by implementation correctness — this is
exactly the kind of guard that needs adversarial tests, and the test suite
targets it.

### T5 · Symlink attacks

*A symlink inside the workspace or a skill package points outside it,
turning an "internal" write into an external one.*

**Mitigation:** state and skill installation resolve symlinks and refuse
targets that escape the permitted root; skill packages containing symlinks
are rejected by `skill scan` and the installer.

**Residual risk:** low on the covered paths; TOCTOU races between check and
use are mitigated but not provably eliminated on all filesystems.

### T6 · Secret exfiltration

*API keys or credentials leak into evidence files, logs, prompts, or
published artifacts.*

**Mitigation:** secrets are read from environment/keychain, never persisted to
state; logs and evidence pass a secret-pattern scrub; `doctor` checks state
files for secret-shaped strings; no auto-publish means no accidental push of
state.

**Residual risk:** medium. Pattern-based scrubbing misses unconventional
secret formats, and a model can echo a secret it was (wrongly) shown. Keep
secrets out of task inputs.

### T7 · Tool escalation

*A component with narrow permissions chains into broader action — e.g. model
output convincing the runtime to run commands.*

**Mitigation:** the runtime has no generic "execute what the model said"
path. Actions are limited to a declared adapter surface; destructive actions
require approval; loops are bounded so escalation can't compound silently.

**Residual risk:** medium where users wire in a generic command adapter with
broad rights — the adapter boundary is only as narrow as you configure it.

### T8 · Memory / state poisoning

*Persisted state (evidence, counters, prior verdicts) is manipulated so later
sessions inherit false beliefs.*

**Mitigation:** state files are plain, inspectable text with recorded
provenance; verdicts reference their evidence rather than replacing it;
`verify` re-derives rather than trusting stored conclusions; `doctor` flags
state inconsistencies.

**Residual risk:** medium. Anyone with write access to `.piensalo/` can
alter history; state integrity is currently inspectability, not cryptographic
attestation.

### T9 · Silent model fallback

*The runtime substitutes a different model than configured, corrupting every
attribution and measurement downstream.*

**Mitigation:** prohibited by design. Model identity is declared per run,
recorded in evidence, and an unavailable model is a hard stop — never a
substitution ([docs/model-provenance.md](model-provenance.md)). This
entry exists because we measured exactly this corruption
([NEGATIVE-RESULTS.md](../NEGATIVE-RESULTS.md), NR-6).

**Residual risk:** low within Piénsalo; nonzero at provider level (an API
endpoint may itself route between model versions — provenance records what
the provider reported).

### T10 · Grader leakage

*Evaluation graders see information they shouldn't (oracle answers, class
vocabulary), or their criteria leak into the system under test, inflating
results.*

**Mitigation:** graders run separated from generation, on observable output
only; grading criteria are versioned apart from skills; grader errors in both
directions are treated as findings (NEGATIVE-RESULTS.md, NR-5).

**Residual risk:** medium. Leakage is subtle and recurring; the defense is
process (separation + audits), not a mechanism that makes it impossible.

### T11 · Supply chain

*A compromised dependency, build step, or release artifact ships malicious
code to users.*

**Mitigation:** minimal dependency surface (stdlib-only core), pinned dev
dependencies, CI builds from clean checkout on two OSes, secret scanning in
CI, releases built from tagged commits.

**Residual risk:** medium — the ecosystem-wide baseline. No signed
reproducible builds yet; that is roadmap material, and until then this entry
stays honest about it.

---

## What this model assumes

- The local user is trusted; Piénsalo does not defend against the machine's
  owner.
- The model provider honors its API contract; provenance records what the
  provider reports.
- Filesystem permissions work; state confidentiality is delegated to the OS.

Reports that break these assumptions in interesting ways are still welcome —
see [SECURITY.md](../SECURITY.md).
