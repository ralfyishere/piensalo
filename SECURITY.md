# Security Policy

## Reporting a vulnerability

Please **do not** open a public issue for security problems. Use GitHub's
private vulnerability reporting ("Security" tab → "Report a vulnerability") on
this repository. You'll get an acknowledgment within 72 hours and a status
update within 14 days. Coordinated disclosure preferred; we will credit
reporters unless you ask otherwise.

In scope: the `piensalo` CLI and runtime, the skill loader and
`skill scan`, model adapters, and anything in this repository's release
artifacts. Out of scope: the models themselves, third-party skills you
installed from elsewhere (report those to their authors — but tell us too if
`skill scan` should have caught it).

## Security defaults

These hold on a fresh install, with no configuration. Any release that breaks
one of them is a security bug, not a feature:

| Default | Meaning |
|---|---|
| **No telemetry** | Nothing is collected, counted, or phoned home. Ever. |
| **No network without an explicit adapter** | The core runs offline. Network happens only through an adapter you configured, to the endpoint you named. |
| **No silent uploads** | No content leaves the machine except as the model call you explicitly configured. |
| **No silent model fallback** | If the configured model is unavailable, Fable Think stops with an error. It never substitutes a model quietly. See [docs/model-provenance.md](docs/model-provenance.md). |
| **No destructive action without approval** | Deletes, overwrites outside the workspace, sends, and deploys require explicit approval. See [docs/operator-boundaries.md](docs/operator-boundaries.md). |
| **No arbitrary shell from untrusted skill text** | Skill files are instructions, not code. Text inside a skill can never cause command execution by itself. See [docs/skill-security.md](docs/skill-security.md). |
| **No secrets in logs** | Evidence and logs are scrubbed of values matching secret patterns; adapters must never log credentials. |
| **No hidden persistence** | All state lives in `.piensalo/` in the workspace (or an explicitly configured path). Nothing is written elsewhere. |
| **No auto-publish** | Nothing is pushed, published, or shared without an explicit command and confirmation. |

## Tooling

- **`piensalo skill scan <path-or-package>`** — vets a skill before
  install: flags embedded command patterns, network references, path traversal
  and symlink tricks, secret-shaped strings, and instruction patterns
  associated with prompt injection. A scan is a filter, not a guarantee —
  review what you install.
- **`piensalo doctor`** — audits the local installation: verifies the
  defaults above are intact, checks adapter configuration, state-directory
  permissions, and provenance recording; reports anything weakened.

## Threat model

The full threat catalog — prompt injection, malicious skills, reference
poisoning, path traversal, symlinks, secret exfiltration, tool escalation,
memory poisoning, model fallback, grader leakage, supply chain — with
mitigations and **residual risk stated honestly**, lives in
[THREAT-MODEL.md](THREAT-MODEL.md).

## Supported versions

Pre-1.0: only the latest release receives security fixes.
