# Cortex Gateway — Protocols

The gateway keeps a strict boundary: one **neutral core** and thin **wire
adapters** at the edge. One wire protocol's assumptions never reach the core.

## Compatibility labels

We never collapse these into a vague "supported":

- **DESIGNED** — architecture reserved; no code path yet.
- **UNIT TESTED** — covered by tests against a mock upstream.
- **SMOKE TESTED** — run once end-to-end via the real CLI against a local server.
- **LIVE TESTED** — exercised against a real provider.
- **EVIDENCE SUPPORTED** — measured improvement in a preregistered suite.

## Current status

| Boundary | Direction | Status | Notes |
|---|---|---|---|
| OpenAI Chat Completions (`/v1/chat/completions`) | client ⇄ gateway ⇄ upstream | **LIVE TESTED** (Ollama) | non-stream, SSE streaming, tool-calls |
| Ollama (`/v1`) | gateway → upstream | **LIVE TESTED** | qwen2.5:0.5b: response semantically identical to direct, stream identical, +3.4 ms median overhead |
| LM Studio, llama.cpp, OpenRouter (`/v1`) | gateway → upstream | **DESIGNED** (protocol identical to Ollama; not yet **LIVE TESTED** per server) | same wire format |
| Anthropic Messages | client ⇄ gateway | **DESIGNED** | Stage 3 target (Claude Code's native boundary) |
| OpenAI Responses | client ⇄ gateway | **DESIGNED** | Stage 3 target |

## Why Chat Completions first

Real repository fit and adoption, not assumption: the repo already ships a
unit-tested `OpenAICompatAdapter` speaking this exact format; every generic and
local upstream PIÉNSALO sits in front of speaks `/v1/chat/completions`; and it
is fully testable offline with an in-process mock (including SSE and tool
calls). See [ARCHITECTURE.md §2](ARCHITECTURE.md).

## The neutral core

`gateway/protocol.py` defines SDK-free types — `NormalizedRequest`,
`NormalizedResponse`, `Message`, `ContentBlock`, `ToolDef`, `ToolCall`,
`Usage`. Wire adapters map onto these; the router and ledger only ever see the
neutral types. Token counts derived here are **estimates** (labelled
`*_est`), never presented as measured; only provider-reported usage is
`measured: true`.

## Fidelity guarantees (observe mode)

- **Request:** forwarded to the upstream **verbatim** — the original bytes. The
  neutral projection is a read-only copy for the router.
- **Non-stream response:** client receives the upstream body **byte-for-byte**.
- **Streaming response:** the application payload (the `data:` SSE events) is
  forwarded **in order, byte-identical in aggregate**. Only the HTTP transfer
  framing is re-managed (chunked) — a transport detail, not application data.
- **Tool calls:** tool-call ids and arguments are preserved (they ride inside
  the untouched response body); the ledger additionally tallies them.

**Path join.** An OpenAI client points its base URL at the gateway's `…/v1` and
sends `/v1/chat/completions`; the upstream is also configured as `…/v1`. The
gateway joins these without duplicating the shared prefix (it does **not**
produce `…/v1/v1/…`). This was found by the live Ollama test — the path-agnostic
mock upstream had masked it — and is now covered by a regression test.

What is **not** yet proven: real-time token-by-token interleaving against a live
streaming provider, and any cloud/tool-calling provider. The Ollama live test
proves ordered, faithful aggregate delivery and semantic identity against a real
local model; the unit tests prove the same against a per-event-flushing mock.
