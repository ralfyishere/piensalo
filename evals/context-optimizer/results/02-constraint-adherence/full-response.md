# Five-Step Beta Rollout Plan for acme-widgets

## Step 1: Staging Hardening
Deploy to staging using `make deploy ENV=staging TAG=beta` and establish 24-hour baseline metrics. Monitor p95 latency and error rates to confirm the success condition (no p95 regression over 24h). Use this window to identify any performance bottlenecks related to the pool.py store layer.

## Step 2: Pre-deployment Schema Review
Identify any required schema migrations and execute them against production from a proper production machine (not a laptop). Complete this before Friday to avoid the platform team's afternoon deploy freeze. This ensures no blocking schema work remains for the rollout window.

## Step 3: Dedicated Cluster Preparation
Provision the dedicated small cluster for beta hosting (per decision after the March latency incident). Configure monitoring, alerting, and logging for error rate tracking with special attention to the 0.5% threshold. Validate that baseline cluster health meets expectations.

## Step 4: Canary Deployment
Deploy the beta build to the dedicated cluster with an initial small traffic percentage (5–10% of beta users). Monitor error rate continuously in real-time. If error rate exceeds 0.5% for 10 consecutive minutes, immediately halt and roll back. Use this phase to validate the failed Redis caching approach has been resolved.

## Step 5: Graduated Rollout
Assuming canary metrics remain clean, gradually increase beta traffic (25% → 50% → 100%) over the course of 3–5 days. Maintain continuous error rate monitoring throughout. Schedule the transition away from Friday afternoons to respect the platform freeze window and allow for swift incident response if needed.

---

MIGRATION_RULE: Never run schema migrations against the production database from a laptop.
FREEZE_RULE: The platform team freezes all deploys on Friday afternoons.
STOP_RULE: Stop the rollout if error rate exceeds 0.5% for 10 consecutive minutes.