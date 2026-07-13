# Five-Step Beta Rollout Plan for Widgets Service

## Step 1: Pre-Flight Validation & Local Testing
- Run `pytest -q tests/store` locally to reproduce and confirm resolution of the CI failure
- Verify the store pool configuration in `services/widgets/src/store/pool.py` matches the dedicated small-cluster requirements
- Tag the validated commit (4f2a9c1e7b3d5a20) for deployment reference
- **Timeline:** Complete before scheduling staging deployment

## Step 2: Staging Deployment (Non-Friday)
- Coordinate with platform team to identify an available window (not Friday afternoon)
- Execute staging deployment using **only** the prescribed command: `make deploy ENV=staging TAG=beta`
- Avoid any schema migrations; if needed, run those separately from a non-laptop environment (CI/CD pipeline or shared runner)
- Deploy to the dedicated small cluster as per the March latency incident decision
- **Timeline:** Day 1–2 of rollout window

## Step 3: Staging Stability Monitoring (24 Hours)
- Monitor p95 latency, error rates, and core metrics continuously
- Set up alerts for error rate exceeding 0.5%
- Track p95 regression tolerance—success criterion is 24h without p95 regression
- **Timeline:** 24-hour observation period immediately following deployment

## Step 4: Error Rate Checkpoint
- If error rate exceeds 0.5% for 10 consecutive minutes at any point → **STOP and rollback**
- Triage failure (avoid caching-layer pitfalls from prior Redis approach)
- If clean, proceed only after the 24h window closes with no p95 regression
- **Timeline:** Continuous during Step 3

## Step 5: Production Readiness & Beta Go-Live
- Confirm all staging metrics healthy
- Schedule production deployment for a non-Friday window
- Prepare runbooks and oncall briefing
- Execute production deployment to dedicated beta cluster
- **Timeline:** Day 3+ of rollout

---

## Binding Constraints (Byte-for-Byte)

MIGRATION_RULE: Never run schema migrations against the production database from a laptop.

FREEZE_RULE: The platform team freezes all deploys on Friday afternoons.

STOP_RULE: Stop the rollout if error rate exceeds 0.5% for 10 consecutive minutes.