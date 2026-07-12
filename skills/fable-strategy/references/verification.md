# Verification criteria

Verification criteria for this skill's domain. Deterministic criteria are checked mechanically; adversarial criteria require constructing probes; evidence criteria grade support quality. Disqualifying criteria fail the whole candidate.

## Domain: strategy
### causal_consistency (judgment) [disqualifying]
Per structured-reasoning and verification-discipline: walk the causal chain from action to claimed outcome and check every link is a mechanism, not a wish — 'we do X, therefore Y happens BECAUSE Z'. Any link that only works if an unstated actor cooperates or an unstated resource exists is an assumption and must be labeled with its breaks-if-false condition.

### constraint_fit (evidence) [disqualifying]
Per verification-discipline: check the plan against every stated constraint — budget, headcount, timeline, legal, technical capacity — with arithmetic recomputed independently. A plan that fits constraints 'roughly' has not been checked; show the numbers.
- Tool protocol: `Tabulate constraint | plan's demand | headroom; recompute all sums independently.`

### scenario_robustness (adversarial)
Per adversarial-verify and failure-mode-awareness: stress the strategy under at least three scenarios it was not designed for — the key assumption is wrong, the timeline doubles, the main resource halves. Per foresight: pre-register what breaks at 10x and what the plan regrets in 10 steps. A strategy robust only in its author's base case is a bet, not a plan.
- Tool protocol: `For each scenario: state the perturbation, trace the plan's behavior, record survives/degrades/dies.`

### incentive_response (adversarial)
Per adversarial-verify's hostile-reader attack applied to actors: for every party the strategy depends on (competitors, customers, regulators, internal teams), ask what their BEST response is once they observe the move — not their hoped-for response. Any step that requires a rational actor to act against their own interest is flagged as the plan's true risk.

### cheapest_discriminating_test (judgment) [disqualifying]
Per empirical-validation: before committing real resources, the strategy must name the cheapest real-world experiment that could FALSIFY its core bet — one with different predicted outcomes depending on whether the thesis is true (debugging-playbook's discriminating-test bar). Write the prediction before running it. A strategy with no falsifying test is unfalsifiable advocacy.
- Tool protocol: `Name the test, its cost, the pre-registered prediction, and the decision rule for each outcome.`

### Adversarial tests
- Assume the single most load-bearing assumption is false; check whether the strategy notices before the budget is spent (failure-mode-awareness).
- Play the strongest competitor's best counter-move on day one; re-trace the causal chain.
- Halve the key resource and double the timeline; check which milestones survive.
- Steelman the do-nothing baseline: if it beats the plan risk-adjusted, the plan fails (structured-reasoning).

### Disqualifiers
- A causal link that requires another actor to act against their own interest.
- A stated constraint the plan arithmetically violates.
- No falsifiable test of the core bet before major resource commitment.
- Success criteria that cannot be observed (empirical-validation: unmeasurable claims cannot be validated).
