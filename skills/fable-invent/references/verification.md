# Verification criteria

Verification criteria for this skill's domain. Deterministic criteria are checked mechanically; adversarial criteria require constructing probes; evidence criteria grade support quality. Disqualifying criteria fail the whole candidate.

## Domain: invention
### functional_feasibility (judgment) [disqualifying]
Per this skill's feasibility bar and adversarial-verify: attack the physics first, economics second, adoption third — energy/material/information budgets, scaling behavior at 10x, and the wrongness probe ('what would have to be true for this to be impossible?'). Every attack ends fixed, defended with evidence, or disclosed; per disclosure-is-not-a-fix, disclosure alone does not clear a disqualifying infeasibility.

### constraint_satisfaction (evidence) [disqualifying]
Per verification-discipline: check the design against every stated constraint (cost, size, power, materials, regulatory, interface) with numbers recomputed independently — a budget table, not adjectives. Constraints the design 'probably meets' are assumptions and must carry breaks-if-false notes.
- Tool protocol: `Tabulate constraint | required | design's value | margin; recompute independently.`

### mechanism_novelty (evidence)
Per the prior-art step and verification-discipline: 'novel' is a factual claim about the world and must be stated at its evidence level — 'no prior art found in searches X, Y, Z' is honest; 'unprecedented' is not. Identify the specific mechanism claimed as new and what distinguishes it from the nearest known mechanism.
- Tool protocol: `Name the nearest-neighbor prior mechanism and the exact delta.`

### prior_art_collision (evidence)
Per leverage-first and the prior-art step: search patents, products, papers, and open-source projects for the same mechanism before claiming it. Finding prior art is a win either way — a leverage-first shortcut or a map of the crowded region to design around. Record the actual queries run, per research-methodology's honest-coverage rule.
- Tool protocol: `List search venues + queries + nearest hits; collision = same mechanism solving same problem.`

### failure_mode_attack (adversarial)
Per failure-mode-awareness and adversarial-verify: enumerate how the invention fails — worst-case operating conditions, misuse by a naive user, degradation over time, the strongest domain-expert objection — and test the strongest attack for real, not rhetorically. Predict the failure before probing; an attack with no predicted outcome is an activity, not a test.
- Tool protocol: `For each failure mode: trigger condition | predicted failure | evidence or simulation | mitigation.`

### Adversarial tests
- Wrongness probe: state what would have to be true for the design to be impossible, then check whether it is (feasibility bar).
- Scale the design 10x up and 10x down; find the first budget (energy, cost, heat, attention) that breaks (foresight).
- Hand the design to a hostile expert persona: write their single strongest objection and answer it with evidence, not assertion.
- Search prior art with the OPPOSITE vocabulary (different field's jargon for the same mechanism) — same-vocabulary searches miss the killer collision.

### Disqualifiers
- A physics/feasibility budget that does not close and is merely disclosed (disclosure-is-not-a-fix).
- A stated constraint the design numerically violates.
- Novelty claimed with no recorded prior-art search.
- A known failure mode with neither mitigation nor an explicit dated decision to accept it.
