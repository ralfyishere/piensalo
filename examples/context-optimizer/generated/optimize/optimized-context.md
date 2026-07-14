# Optimized context packet

Task-specific context compiled by PIENSALO Context Optimizer.
Behavioral status of this packet is reported separately; treat the
omissions section as authoritative about what was left out.

## Task

Fix the flaky CI failure in the widgets service. From the project context,
report exactly which file and function must change, the exact command that
reproduces the failure, and the exact staging deploy command — quote
commands byte-for-byte. Answer with exactly these lines:

FILE: <exact path>
FUNCTION: <name>
REPRO: <exact command>
DEPLOY: <exact command>

## Objective

Harden the acme-widgets service for the beta cut.

## Success conditions

- Staging runs 24h without a p95 regression.

## Critical constraints and invariants

- [constraint-0a393a3af227]
Deploy to staging only with `make deploy ENV=staging TAG=beta`.
- [constraint-4d485a4c8da4]
Keep p95 read latency under 250 ms at 400 rps.

## Active decisions

- [decision-65ccb27fdcb2]
Host the beta on a dedicated small cluster after the March
latency incident.

## Failed approaches — do not repeat these

- [failed_approach-3781971f8182]
Caching whole responses in Redis; stale order totals in checkout.

## Required artifacts and exact identifiers

- [artifact-926f0ae1e0ea]
services/widgets/src/store/pool.py
- [artifact-5ccfe899544c]
commit 4f2a9c1e7b3d5a20

## Stop conditions

- [stop_condition-f7c8530c7c17]
Stop the rollout if error rate exceeds 0.5% for 10 consecutive minutes.

## Relevant evidence (selected from the source context)

- [block-043da639061d] (file+lines:38-41)
The pool module's acquire() helper hardcodes timeout=5 and the CI runner is
slower than laptops, so tests/store/test_pool.py::test_acquire_timeout
flakes in CI. The team agreed the timeout in acquire() must become
configurable before the beta tag.

## Next action

Reproduce the CI failure locally with `pytest -q tests/store`.

## Note on omitted material

Material judged irrelevant to this task (27 chunk(s), mostly unrelated discussion) was deliberately filtered out; the sections above contain everything assessed as necessary for this task, and exact identifiers are quoted verbatim. Answer directly from the context above. Only if a fact you are explicitly required to report is genuinely absent, state that it is missing instead of guessing.
