# Continuation packet

Compiled by PIENSALO Context. Deterministic structural compilation;
behavioral equivalence: UNMEASURED (no behavioral verification was run).
This packet is plain text and model-independent: paste it into any AI
system to continue the work described below.

Compilation goal: Continue the acme-widgets beta-hardening work in a fresh session

## Objective

Harden the acme-widgets service for the beta cut.

## Success conditions

- The full suite passes and staging runs 24h without a p95 regression.

## Active decisions

- [decision-edafa35abba5]
Host the beta on a dedicated small cluster, because noisy neighbors
on acme-platform caused the March latency incident.
- [decision-5ee17da45716] (CONTESTED)
Adopt a weekly release cadence for the beta period.

## Critical constraints and invariants

- [constraint-fb31f03ae558]
Never run schema migrations against the production database from a laptop.
- [constraint-4d485a4c8da4]
Keep p95 read latency under 250 ms at 400 rps.
- [constraint-0a393a3af227]
Deploy to staging only with `make deploy ENV=staging TAG=beta`.
- [invariant-faac9ef35a90]
The public API stays backward compatible within the v1 prefix.

## Completed work

- [completed-6ee48578455d]
Connection pool rewrite merged and load-tested.
- [completed-4a6199f30ec3]
Flaky test quarantine emptied; suite is green twice in a row.

## Failed approaches — do not repeat these

- [failed_approach-74c55f53a042]
Caching whole responses in Redis; cache invalidation bugs
produced stale order totals in checkout and the approach was abandoned.

## Relevant artifacts

- [artifact-926f0ae1e0ea]
services/widgets/src/store/pool.py
- [artifact-5ccfe899544c]
commit 4f2a9c1e7b3d5a20

## Open questions

- [open_question-75cddba9d6ef]
Do we need a read replica for the reporting endpoints before beta?

## Open actions

- [open_action-d6a89315d45c]
Wire the latency histogram into the staging dashboard.

## Stop conditions

- [stop_condition-f7c8530c7c17]
Stop the rollout if error rate exceeds 0.5% for 10 consecutive minutes.

## Next action

Run `pytest -q tests/store` and fix the first failure before touching the dashboard work.

## Known limitations

- behavioral equivalence: UNMEASURED — structural checks only.
- [unstructured] lines 4-21: The session opened with a long discussion about naming, weekend plans, and
whether the logo should be teal. None of i...
- [unstructured] lines 45-62: Someone pasted a partial stack trace here and the discussion moved on before
anyone confirmed whether it was from sta...

## Source-expansion references

Every record id above maps to an exact, content-hashed source span in
capsule.json (references + per-record source_reference). Expand by
opening the source at the recorded location; a hash mismatch means
the source changed since compilation (STALE) and must not be trusted
as the original.
- project_state: file:project-state.json (sha256 87a4194c98b42376..., local)
- transcript: file:transcript.txt (sha256 4ad02eef9fc17309..., local)
