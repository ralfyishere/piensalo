# Cortex Gateway — Evaluation

This is the **preregistered** evaluation plan for the gateway. It states what
will be measured *before* any results exist, so the gate cannot be moved after
seeing them. Nothing here authorizes a performance claim for observe mode —
observe mode is a pass-through + measurement surface and improves nothing.

## Conditions to compare

1. **direct model** — client → upstream, no gateway.
2. **gateway pass-through** — client → gateway → upstream, `PASS_THROUGH`.
3. **gateway observe** — as (2) but with shadow-router recording.
4. **gateway optimized** — DESIGNED, not implemented (safe deterministic CONTEXT).
5. **gateway full-cortex** — DESIGNED, not implemented (THINK→CONTEXT→CHECK).

Only conditions **1–3** exist today. 4–5 are gated behind their own stages.

## Task classes (from the brief §20)

simple/abstain · difficult planning · long-context · tool-use coding ·
structured-output · critical-constraint · distractor-heavy · ambiguous ·
already-correct · incorrect-needing-repair · compression-unsafe ·
weak-model-benefits-from-scaffolding · scaffolding-harms · streaming tool-call.

## Metrics

task success · deterministic requirements passed · critical regressions ·
quality improved/regressed · token savings · total token cost · latency ·
tool-call fidelity · stream fidelity · **intervention rate** ·
**unnecessary-intervention rate** · expansion rate · fallback rate ·
abstention accuracy · repair harm · model-switch correctness.

## What is measured **now** (observe scope)

Observe mode can only honestly report *fidelity* and *shadow* metrics:

| Metric | Result (this branch) | Level |
|---|---|---|
| non-stream pass-through byte-identical | yes | UNIT TESTED |
| streaming payload ordered + faithful (aggregate) | yes | UNIT TESTED |
| tool-call fidelity (non-stream + streamed) | yes | UNIT TESTED |
| request forwarded verbatim to upstream | yes | UNIT TESTED |
| secret redaction / no body retention | yes | UNIT TESTED |
| SSRF / auth / size / loop guards | yes | UNIT TESTED |
| real CLI serve → request → ledger | yes | SMOKE TESTED |
| response semantically identical vs direct (real provider) | yes — Ollama qwen2.5:0.5b | LIVE TESTED |
| streamed content identical vs direct (real provider) | yes — 8 SSE events, [DONE] preserved | LIVE TESTED |
| streamed tool-call fidelity vs direct (real provider) | yes — Ollama qwen2.5:7b (name+arguments reassemble identically) | LIVE TESTED |
| latency added by observe | +3.4 ms median (Ollama, local) | LIVE TESTED |
| shadow would-intervene rate on real traffic | pending broader corpus | DESIGNED |

## Discipline

- Do **not** tune task answers after seeing results.
- Do **not** average away critical failures.
- Include negative results.
- Separate: unit-tested compatibility · live-tested compatibility ·
  evidence-supported improvement · independent reproduction.

## Cross-model plan

Replicate across at least one Claude-family, one OpenAI-compatible, and one
genuinely different/local model — **using only configured adapters and
credentials**. Where credentials are unavailable, build and unit-test the
harness, document the exact blocked live cell, and do not fabricate results or
weaken the gate.
