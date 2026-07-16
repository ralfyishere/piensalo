# Cortex Gateway — offline demo (observe mode)

Try the gateway with **no credentials and no network** using a local mock
upstream. Every command below runs as written.

Observe mode forwards your traffic **unchanged**, runs the Cortex Router in
**shadow** (recorded, never acted on), and writes a local event ledger. It does
**not** modify responses and does **not** improve the model — it is a
pass-through + measurement surface.

## 1. Start the mock upstream (terminal A)

```bash
python examples/gateway/mock_upstream.py 8991
```

## 2. Start the gateway (terminal B)

```bash
piensalo serve \
  --upstream-base-url http://127.0.0.1:8991/v1 \
  --upstream-model demo/model-1 \
  --port 8788 \
  --ledger-dir .piensalo/gateway
```

## 3. Send a request through it (terminal C)

```bash
curl -s http://127.0.0.1:8788/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"demo/model-1","messages":[{"role":"user","content":"Return JSON. It must include a name. Output exactly this format."}]}'
```

The response is the upstream's, byte-for-byte. Try `"stream": true` to see the
SSE stream forwarded faithfully.

## 4. Inspect what the cortex *would* have done

```bash
piensalo gateway report  --ledger-dir .piensalo/gateway
piensalo gateway inspect --ledger-dir .piensalo/gateway --last 5
```

`report` shows a **shadow would-intervene rate** (the request above trips the
`CHECK` heuristic — several deterministic output requirements) and confirms
`additional_cortex_tokens: 0` — observe mode adds nothing.

## 5. Preflight a config

```bash
piensalo gateway doctor --upstream-base-url http://127.0.0.1:8991/v1
```

## Live test against a real provider

`live_test.py` is the reproducible harness behind the **LIVE TESTED** claim in
[../../docs/gateway/PROTOCOLS.md](../../docs/gateway/PROTOCOLS.md). With Ollama
running (`ollama serve` + `ollama pull qwen2.5:0.5b`):

```bash
python examples/gateway/live_test.py
```

It confirms the gateway response is semantically identical to a direct call,
the SSE stream is forwarded faithfully, latency overhead is a few ms, and the
ledger records the resolved model + measured usage with zero added cortex
tokens. Point it at any OpenAI-compatible server with `--direct/--upstream/--model`.

`live_tool_test.py` does the same for **streamed tool-calls** (needs a
tool-capable model, e.g. `ollama pull qwen2.5:7b`):

```bash
python examples/gateway/live_tool_test.py
```

It verifies the gateway reassembles tool-call name + arguments — both
non-stream and from the SSE stream — identically to a direct call.

## Point it at a real local model

The same commands work in front of any OpenAI-compatible upstream — for example
Ollama or LM Studio (`--upstream-base-url http://127.0.0.1:11434/v1`). That path
is **DESIGNED** and protocol-identical but not yet **LIVE TESTED** per server;
see [../../docs/gateway/PROTOCOLS.md](../../docs/gateway/PROTOCOLS.md).
