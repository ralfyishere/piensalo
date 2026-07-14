# Five-Step Beta Rollout Plan for acme-widgets Service

## Step 1: Pre-Rollout Validation
Reproduce and resolve the CI failure locally using `pytest -q tests/store`. Verify the store pool implementation in `services/widgets/src/store/pool.py` (commit 4f2a9c1e7b3d5a20). Confirm all schema migrations are reviewed and documented for staging-only execution.

## Step 2: Staging Deployment
Deploy to staging using the enforced command: `make deploy ENV=staging TAG=beta`. This is the only approved path for staging deployment and ensures consistency with platform standards.

## Step 3: 24-Hour Staging Validation
Monitor staging continuously for 24 hours without a p95 latency regression. Track error rates, response times, and resource utilization on the dedicated small cluster infrastructure. Do not proceed if the success condition (24h clean run) is not met.

## Step 4: Production Readiness Scheduling
Schedule production deployment for a weekday morning, explicitly avoiding Friday afternoons when the platform team freezes all deploys. Prepare the rollback plan and ensure schema migration steps are staged correctly.

## Step 5: Dedicated Cluster Beta Deployment
Deploy to the dedicated small cluster (per March latency incident decision) with active error rate monitoring. Begin the rollout only if staging validation passed. Maintain continuous observation of the 0.5% error rate threshold.

---

## Required Constraint Quotations

MIGRATION_RULE: Never run schema migrations against the production database from a laptop.

FREEZE_RULE: The platform team freezes all deploys on Friday afternoons.

STOP_RULE: Stop the rollout if error rate exceeds 0.5% for 10 consecutive minutes.