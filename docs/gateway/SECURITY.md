# Cortex Gateway — Security

The gateway is a local network server, so it is built to **fail closed**. This
document is the threat model and the defenses that back it. Compatibility labels:
the defenses below are **UNIT TESTED** against a mock upstream unless noted.

## Defaults (safe by default)

| Setting | Default | Why |
|---|---|---|
| bind host | `127.0.0.1` (loopback) | never exposed to the network without an explicit opt-in |
| body retention | off (`--no-store`, hashes only) | prompts/responses are not written to disk |
| header logging | redacted | secret headers dropped; others recorded as presence only |
| auth | off, but when set → required | a configured token is enforced; missing/wrong → 401 |
| telemetry | none | no phone-home, no cloud storage |

## Threats and defenses

- **SSRF via the configurable upstream URL.** The upstream is operator-supplied,
  so it is validated: scheme allow-list (`http`/`https` only); DNS resolution
  with a block on link-local (`169.254.0.0/16`, incl. cloud metadata),
  multicast, reserved, and unspecified addresses; optional
  `--allowed-upstream` prefix allow-list; private-network upstreams require an
  explicit `--allow-non-loopback-upstream`. Resolution failure fails closed.
- **Recursive proxy loop.** Every forwarded request carries an
  `X-Piensalo-Gateway` marker; an incoming request already bearing it → `508`.
  At construction, an upstream whose loopback host+port equals the gateway's own
  bind is refused.
- **Credential / header leakage.** `Authorization`, `X-Api-Key`, `Cookie`, and
  peers are never written to the ledger (dropped even at full retention).
  Hop-by-hop headers are stripped on forward.
- **Prompt / response logging.** Off by default; bodies are stored as
  `sha256:` content hashes. `--retention full` (with `--store`) is the only way
  to persist bodies and it is a deliberate, documented choice.
- **Resource exhaustion.** Request bodies are capped (`max_body_bytes`, default
  8 MiB → `413`). Upstream calls have a timeout. No retries are performed
  (observe mode never re-issues a request).
- **Untrusted proxy targets.** The upstream is only ever what the operator
  configured; observe mode never picks a model or endpoint on its own.
- **Malformed stream / body events.** Parsing for the ledger is best-effort and
  never raises into the proxy path — a body we cannot parse still passes through
  untouched; only its metadata is blank.
- **Cross-session state leakage.** The ledger is per-`--ledger-dir`; there is no
  shared global state between requests beyond the append-only log.

## Fail-closed vs fail-safe

- **Auth / policy violations fail closed** (401/413/508 — request not forwarded).
- **Cognitive-analysis failures fail safe**: if the shadow router cannot analyze
  a request, the request still passes through unchanged (observe mode's contract
  is pass-through first).

## Not claimed

Observe mode has been **UNIT TESTED** and **SMOKE TESTED** (local mock upstream
via the real CLI). It has **not** been penetration-tested, and it has not been
**LIVE TESTED** against a hostile network. Do not expose it publicly.
