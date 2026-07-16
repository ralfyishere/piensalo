# Cortex Gateway — Privacy

The gateway is offline-first and privacy-preserving by default. It stores the
**minimum** needed to be inspectable, and never phones home.

## What is stored, by retention level

| Level (`--retention`) | Request/response bodies | Headers | Router decision + token/latency metadata |
|---|---|---|---|
| `hashes` (default) | `sha256:` hash only | redacted (presence, secrets dropped) | yes |
| `metadata` | hash only | redacted | yes |
| `full` (requires `--store`) | full body retained | redacted (secrets still dropped) | yes |

- **No body retention by default.** With `hashes`, the ledger proves *which*
  content flowed (via hash) without keeping the content.
- **Secrets are never stored**, at any level — `Authorization`, `X-Api-Key`,
  `Cookie`, `Proxy-Authorization` are dropped.
- **No telemetry, no cloud storage, no network egress** other than the single
  configured upstream call.

## The ledger

- Location: `<--ledger-dir>/events.jsonl` (default `.piensalo/gateway/`).
- Format: append-only JSONL, one event per request — plain, greppable,
  tool-independent.
- Fields: request id, client (user-agent), protocol, requested/resolved model,
  router decision + reasons + features, token estimates and measured usage,
  latency, stream flag, tool-call count, status, and content hashes. Full field
  list: `gateway/ledger.py`.

## Controls

- `--no-store` (default) / `--store`
- `--retention hashes|metadata|full`
- `--no-redact` (keep non-secret header values; secrets are still dropped)
- `--ledger-dir <path>`
- `--auth-token-env <ENV>` — read the gateway token from the environment, not a
  flag, so it never lands in shell history or a process listing.

## Retention hygiene

The ledger is a local file you own — rotate or delete it like any log. Because
bodies are hashes by default, deleting the ledger removes routing history
without ever having exposed prompt content.

## Relationship to the Cortex Vault

Durable *memory* is a separate, future concern (see
[../context/CORTEX-VAULT.md](../context/CORTEX-VAULT.md)). The observe gateway is
**read-only with respect to durable memory** and never promotes any response
into trusted memory.
