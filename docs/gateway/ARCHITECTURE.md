# Cortex Gateway — Architecture (Stage 0 audit + decision)

**Status of this document:** Stage 0. It records the current-system audit, the
gap it closes, the protocol/router decisions, the threat model summary, and the
acceptance gates for each stage. No intervention mode is claimed here as
working; see the maturity table.

The **Cortex Gateway** is a *delivery layer*. It does not add a fourth brand.
It makes the existing three-system cortex — **THINK · CHECK · CONTEXT** —
reachable from the AI tools people already use, and it earns each intervention
through evidence, one stage at a time. Internally the policy component is the
**Cortex Router**; the server is the **Cortex Gateway**. The public product
remains PIÉNSALO.

---

## 1. Current-system audit

Classification of every existing mechanism the gateway touches.

| Mechanism | Location | Class | Note |
|---|---|---|---|
| Adapter contract (provenance-first, fallback prohibited) | `adapters/base.py` | **DO NOT TOUCH** | `ModelResponse` + `ModelFallbackError` are exactly the invariants the gateway needs. |
| `OpenAICompatAdapter` (stdlib `/v1/chat/completions`) | `adapters/openai_compat.py` | **KEEP** | Proves the repo already speaks the Stage-2 wire protocol. |
| Context Optimizer / runtime / capsule | `context/` | **DO NOT TOUCH** (Stage 2) · **STRENGTHEN** (Stage 4) | Only deterministic, already-validated Context behavior may later run *inside* the gateway. |
| Layered verify + contract | `verify/` | **KEEP** (Stage 2) · reused by CHECK (Stage 4+) | Verdict types (`cognition/delivery/rendering/routing/verification`, `UNMEASURED`) are the CHECK vocabulary. |
| Loop controller + provenance ledger | `loop/` | **KEEP** | Bounded-loop discipline and JSONL provenance are the model for the gateway event ledger. |
| Evidence records | `evidence/records.py` | **KEEP** | Gateway mechanisms carry the same records. |
| CLI subparser dispatch | `cli/main.py` | **STRENGTHEN** | Add `serve` and `gateway` subcommands next to `doctor`. |
| Routing (as a *failure layer*) | graders | **KEEP, distinct** | Existing "routing" is a grading dimension, not infrastructure. The Cortex *Router* is new and separately named. |

**Gap.** Nothing today accepts client traffic, forwards it to a chosen model,
preserves streaming/tool-calls, decides whether the cortex should intervene, or
records what happened. Every building block is present; the *delivery surface*
is missing. That surface is this work.

**What must not happen (stop conditions, from the brief):** observe mode must
never modify traffic; no silent model calls or substitution; no recursive proxy
loop; no unbounded retries; THINK/CHECK/CONTEXT must not be replaced; the
evidence gate must not be weakened; the work must not drift into a provider
marketplace.

---

## 2. Protocol decision

**Stage-2 boundary: OpenAI Chat Completions (`POST /v1/chat/completions`).**

Rationale — repository fit and adoption, not assumption:

1. The repo already ships a unit-tested `OpenAICompatAdapter` speaking this
   exact wire format. Real fit, not a greenfield guess.
2. Every generic/local upstream PIÉNSALO is meant to sit in front of — LM
   Studio, llama.cpp servers, Ollama-compat shims, OpenRouter — speaks
   `/v1/chat/completions`. One boundary reaches all of them.
3. It is fully testable **offline** with an in-process mock upstream, including
   SSE streaming and tool-call deltas. No credentials required to prove
   fidelity.

The Anthropic Messages boundary (what Claude Code speaks natively) and the
OpenAI Responses boundary are **DESIGNED** in the neutral core and are the
Stage-3 target. They are not implemented here and are not claimed as working.

**Neutral core rule.** The cognitive core, router decisions, ledger, provenance,
and failure semantics are SDK-free and wire-agnostic (`gateway/protocol.py`).
Wire serialization and event ordering live only in the protocol adapter
(`gateway/wire_openai.py`). One wire protocol's assumptions never reach the
core.

---

## 3. Cortex Router decision model

One inspectable, **deterministic** policy layer. It maps request features to one
decision and always explains itself. No opaque classifier.

Decisions: `PASS_THROUGH · THINK · CONTEXT · CHECK · THINK_AND_CONTEXT ·
CONTEXT_AND_CHECK · FULL_CORTEX · ABSTAIN · FALLBACK`.

Every decision carries `reasons[]`, a bounded `confidence`, an
`intervention_budget` (max extra latency/tokens/attempts), and the `features`
it was computed from. Signals considered in Stage 2: estimated input tokens,
message/turn count, tool presence, image presence, output-contract signals
(JSON/"must"/numbered requirements), ambiguity signals, and stream flag —
all derived deterministically from the normalized request.

**Abstention-first.** `PASS_THROUGH` is the default and a *successful* outcome.
The router must not recommend intervention merely because it is available. In
observe mode the decision is **shadow only**: recorded, never acted on.

Model-assisted routing is explicitly out of scope here; if added later its
recommendation stays bounded, recorded, and overridable.

---

## 4. Modes and maturity (honest)

| Mode | Status | What it does |
|---|---|---|
| `observe` | **implemented, this work** | Byte-faithful pass-through; preserves streaming + tool-calls; shadow router; event ledger. Never alters traffic. |
| `optimize-safe` | **DESIGNED, not implemented** | Would activate only already-validated deterministic CONTEXT under explicit policy. Gated on observe-mode evidence. |
| `verified` | **DESIGNED, not implemented** | Would run THINK→CONTEXT→EXECUTE→CHECK→expand/repair/fallback. Gated on safe-mode evidence. |

Observe mode is **not** a performance improvement and is never described as one.
It is a measurement and pass-through surface.

---

## 5. Threat model (summary; full text in SECURITY.md)

Defaults fail closed. Bind loopback only; no telemetry; no prompt/response
retention unless explicitly enabled; redacted logs with content hashes instead
of content. Explicitly defended: credential/header leakage, prompt/response
logging, private-path leakage, **SSRF via the configurable upstream URL**
(allow-list + loopback-metadata block), untrusted proxy targets, malformed
stream events, oversized bodies, resource exhaustion, recursive gateway loops,
unbounded retries, cross-session state leakage. Auth and policy violations fail
closed; cognitive-analysis failures fail safe (pass through per documented
mode).

---

## 6. Stage plan and acceptance gates

- **Stage 0 — this document.** Coherent audit + decisions before implementation. ✅
- **Stage 1 — neutral contracts.** `protocol.py`, `router.py`, `ledger.py`,
  `config.py`, all SDK-free, each with unit tests. Gate: tests green;
  deterministic router; ledger redacts by default; config rejects unsafe binds
  and off-allow-list upstreams.
- **Stage 2 — observe gateway.** OpenAI Chat Completions boundary; loopback
  server; byte-faithful pass-through; streaming + tool-call fidelity;
  shadow router; ledger; `serve` + `gateway status/inspect/report/doctor`.
  Gate: observe leaves request/response bytes unchanged (proven against a mock
  upstream, non-stream + stream + tool-call); security defaults hold; existing
  210 tests still green; no silent model calls.
- **Stages 3–6** — second protocol, safe deterministic intervention, operation
  routing + cross-model evidence, verified full cortex. Each earns its gate
  before the next begins. Work **stops at the first failed gate** and the branch
  is pushed with an honest result.

**Merge gate (observe scope).** May merge only if: all existing + new tests
pass; CLI and Context Optimizer behavior do not regress; pass-through is
byte-faithful at the supported boundary; streaming and tool-call fidelity tests
pass; security tests pass; no private paths/secrets; no silent model
calls/substitution; no unbounded retries or recursive proxy loop; observe mode
leaves traffic unchanged; fresh install works; public CI green. If only Stages
1–2 pass, the observe-only gateway merges and releases **with exactly that
scope** and is not described as improving model performance.
