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
| OpenAI Chat Completions (`/v1/chat/completions`) | client ⇄ gateway ⇄ upstream | **UNIT TESTED + SMOKE TESTED** | non-stream, SSE streaming, tool-calls |
| OpenAI-compatible upstreams (Ollama, LM Studio, llama.cpp, OpenRouter) | gateway → upstream | **DESIGNED** (protocol is identical; not yet **LIVE TESTED** per server) | same wire format |
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

What is **not** yet proven: real-time token-by-token interleaving against a live
streaming provider (that is **LIVE TESTED**, a later step). The unit tests prove
ordered, faithful aggregate delivery against a mock that flushes per event.
