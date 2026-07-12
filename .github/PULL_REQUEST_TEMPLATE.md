# Pull request

## What this changes

<!-- One concern per PR. If you're tempted to write "and", consider two PRs. -->

## Type

- [ ] Skill (all 11 required fields present — see the new-skill issue template)
- [ ] Verifier (adversarial test case included; FP/FN behavior stated)
- [ ] Model adapter (provenance honored, no silent fallback, no creds in logs)
- [ ] Task / benchmark reproduction
- [ ] Bug fix
- [ ] Docs
- [ ] Other:

## Verification I actually ran

<!-- Paste the commands and their real output. "Should work" is a prediction,
     not a result. For docs PRs: paste the link-check / claim-check you did. -->

```
```

## Evidence discipline

- [ ] No capability claim in this PR exceeds its evidence level (docs/evidence-levels.md)
- [ ] I did not upgrade any evidence level via prose (only experiments do that)
- [ ] N/A — this PR makes no capability claims

## Security invariants (SECURITY.md)

- [ ] No telemetry, no network outside explicit adapters, no silent fallback,
      no code execution from skill text, no secrets in code/logs/fixtures
- [ ] If this PR touches a guard (scanner rule, path check, scrubber): the
      adversarial test that tries to defeat it is included

## Breaking changes

- [ ] None
- [ ] Yes — described above, CHANGELOG.md updated
