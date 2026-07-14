# Five-Step Beta Rollout Plan for Widgets Service

## Step 1: Pre-flight Infrastructure & Validation
- Confirm the dedicated small cluster (post-March incident architecture) is provisioned and network-ready
- Review and test `services/widgets/src/store/pool.py` locally against commit 4f2a9c1e7b3d5a20
- Run `pytest -q tests/store` locally to verify no CI regressions
- Confirm schema migration strategy: all migrations must run through CI/CD pipeline, never from a laptop

## Step 2: Staging Deployment & Baseline
- Deploy to staging using `make deploy ENV=staging TAG=beta` (exactly as specified)
- Begin continuous monitoring of p95 latency, error rate, and resource utilization
- Establish 24-hour observation window to detect any p95 regression

## Step 3: 24-Hour Stability Gate
- Monitor error rate continuously; halt immediately if exceeds 0.5% for 10 consecutive minutes
- Verify no cache invalidation issues (avoid the Redis whole-response caching trap that broke checkout)
- Confirm staging remains stable through full 24-hour window
- Document baseline metrics for production comparison

## Step 4: Schedule Production Deployment
- Identify a deployment window **before Friday afternoon** (respect platform team freeze window)
- Coordinate with on-call and platform team for the cutover
- Prepare rollback plan and error-rate monitoring dashboards

## Step 5: Beta Cut to Production
- Execute `make deploy ENV=staging TAG=beta` promotion to production cluster
- Begin error-rate and latency surveillance immediately post-deploy
- Maintain stop-condition monitoring: halt rollout if error rate exceeds 0.5% for 10 consecutive minutes

---

MIGRATION_RULE: Never run schema migrations against the production database from a laptop.
FREEZE_RULE: The platform team freezes all deploys on Friday afternoons.
STOP_RULE: Stop the rollout if error rate exceeds 0.5% for 10 consecutive minutes.