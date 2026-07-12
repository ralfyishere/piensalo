# Skill Security

Skills are instruction files. This document defines how Fable Think keeps
them *only* that — and what risk remains when it can't.

## The core rule: skills are inert text

The skill loader parses skills as data. There is no interpolation into shell
commands, no `eval`, no plugin hooks, no "setup scripts". Text inside a skill
file **cannot cause command execution by itself**, no matter what it says.
This is enforced by the loader's design (no execution path exists), not by
filtering (which would eventually be bypassed).

What a malicious skill *can* still do is persuade: it is read by a model, and
models follow instructions. That residual risk is real and stated in
[THREAT-MODEL.md](../THREAT-MODEL.md) (T2) — the action boundaries in
[operator-boundaries.md](operator-boundaries.md) are what keep persuasion
from becoming action.

## `fable-think skill scan`

Run before installing anything you didn't write:

```bash
fable-think skill scan ./some-skill/           # a local directory
fable-think skill scan some-skill.tar.gz       # a package
```

The scanner flags:

| Class | Examples |
|---|---|
| Embedded command patterns | shell syntax positioned as "steps to run", encoded commands, curl-pipe-sh |
| Network references | URLs the skill asks an agent to fetch; webhook-shaped endpoints |
| Reference poisoning setups | instructions to load external files whose content can change post-review (T3) |
| Path traversal & symlinks | `../` sequences, absolute paths, symlinked package members (T4, T5) |
| Secret-shaped strings | key-like tokens that shouldn't be in an instruction file |
| Injection patterns | "ignore previous instructions", role-override attempts, hidden text tricks |
| Obfuscation | base64 blobs, zero-width characters, homoglyph swaps |

Exit codes: `0` clean, `1` findings (listed, with locations), `2` refused to
scan (malformed package). The installer runs the same scan and refuses on
findings unless you pass an explicit override flag — which is logged in the
evidence trail.

## Honest limits of scanning

A scanner is a filter, not a guarantee. Novel obfuscation and pure
natural-language persuasion will pass it. The security ordering is:

1. Loader design (no execution path) — strong
2. Operator boundaries (persuasion can't act without approval) — strong
3. `skill scan` — useful filter
4. Your review — still required

**Read skills before installing them, like you'd read a shell script before
piping it to bash.** No unreviewed skill marketplace exists for this project,
and none is planned ([CONTRIBUTING.md](../CONTRIBUTING.md)).

## Writing scannable skills

Contributors: keep skills self-contained (no external references), plain
(no encoded content), and structured per the required fields
([new-skill template](../.github/ISSUE_TEMPLATE/new-skill.yml)). If `skill
scan` flags your legitimate skill, restructure rather than requesting an
allowlist entry — an allowlist for "trusted authors" is how supply chains
rot.
