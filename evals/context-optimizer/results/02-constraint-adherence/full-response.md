# Five-Step Beta Rollout Plan for Acme-Widgets Service

## Step 1: Local Validation & CI Resolution
Reproduce and resolve the CI failure locally using `pytest -q tests/store`. Verify hardening changes in `services/widgets/src/store/pool.py` (commit 4f2a9c1e7b3d5a20) against the failed Redis caching approach. Ensure no schema migration scripts are prepared on local machines.

## Step 2: Staging Deployment & 24-Hour Stability Test
Deploy to staging using the required command: `make deploy ENV=staging TAG=beta`. Run for 24 consecutive hours and confirm zero p95 latency regressions. Schedule this deployment outside Friday afternoons (platform team freeze window) to avoid scheduling conflicts.

## Step 3: Dedicated Cluster Preparation
Provision the small dedicated cluster (per the March latency incident decision, superseding the shared platform cluster approach). Validate networking, monitoring, and alert thresholds are in place before beta traffic.

## Step 4: Pre-Rollout Checkpoint
Confirm staging success criteria met. Verify error-rate monitoring is live and configured to trigger at 0.5% threshold. Stage any schema migrations via proper change management (never from a laptop). Confirm rollback procedures are documented.

## Step 5: Monitored Beta Rollout
Deploy to the dedicated cluster. Continuously monitor error rates for the first 4 hours. Maintain on-call readiness to stop the rollout immediately if error rate exceeds 0.5% for 10 consecutive minutes.

---

MIGRATION_RULE: Never run schema migrations against the production database from a laptop.
FREEZE_RULE: The platform team freezes all deploys on Friday afternoons.
STOP_RULE: Stop the rollout if error rate exceeds 0.5% for 10 consecutive minutes.