# Five-Step Beta Rollout Plan for acme-widgets Service

## Step 1: Pre-flight Validation & Infrastructure Setup
- Verify the dedicated small cluster is provisioned and healthy (supersedes shared platform cluster per the March latency incident decision)
- Run schema migrations (if needed) through CI/CD pipeline, never from a laptop
- Establish baseline metrics: p95 latency, error rate, throughput, connection pool health (artifact: services/widgets/src/store/pool.py)
- Set up dashboards and alerting to track the success condition: 24-hour stability window without p95 regression

## Step 2: Staging Deployment & Validation
- Deploy beta build using the exact command: `make deploy ENV=staging TAG=beta`
- Run 24-hour observation period in staging to validate p95 latency stability
- Verify no cache invalidation issues like the abandoned Redis response-caching approach that caused stale order totals
- Sign off on staging readiness; document baseline metrics for comparison

## Step 3: Schedule & Deploy to Dedicated Beta Cluster
- Schedule beta deployment **before Friday afternoon** to respect the platform team's Friday deploy freeze
- Deploy to the dedicated small cluster using CI/CD (never from a laptop)
- Confirm deployment status using commit baseline (4f2a9c1e7b3d5a20)
- Activate comprehensive monitoring immediately post-deployment

## Step 4: Continuous Monitoring & Rollback Readiness
- Track error rate and p95 latency in real-time against staging baselines
- Maintain 10-minute observation windows for error rate threshold evaluation
- Have rollback plan ready with isolated infrastructure on dedicated cluster
- Verify pool.py behavior under production load

## Step 5: Progressive Traffic Migration
- Route initial 5-10% of production traffic to beta cluster
- Monitor error rate and latency drift for 4+ hours
- Expand traffic in increments (25% → 50% → 100%) if metrics remain stable
- Maintain deployment freeze compliance for any follow-up deploys

---

## Binding Constraints (Exact)

MIGRATION_RULE: Never run schema migrations against the production database from a laptop.
FREEZE_RULE: The platform team freezes all deploys on Friday afternoons.
STOP_RULE: Stop the rollout if error rate exceeds 0.5% for 10 consecutive minutes.