# Evidence

Every Fable Think capability ships with receipts. This file is the canonical
public evidence map: what has been measured, what the measurements actually
support, and what would change each verdict. Levels are defined in
[docs/evidence-levels.md](docs/evidence-levels.md):
`DESIGNED → SMOKE_TESTED → EXPERIMENTALLY_TESTED → REPLICATED → PROMOTED`,
with `NARROW` and `REJECTED` as honest terminal states.

**Reading rule:** a mechanism's level describes the *evidence*, not our
confidence in the idea. Nothing below is PROMOTED yet. The evidence base is
young: two controlled runs (120 cells each, one weak-model family), plus
grader-battery and unit-level verification. Negative results are in
[NEGATIVE-RESULTS.md](NEGATIVE-RESULTS.md) and they are load-bearing.

## The two controlled runs behind the current verdicts

Both runs: 8 sealed tasks × 3 repetitions × 5 conditions = 120 cells,
equal budget, small fast model (`claude-haiku-4-5`) as the execution model,
deterministic layered graders (cognition / delivery / rendering / routing /
verification separated), per-cell requested+resolved model recording,
infra-stub cells excluded (NOT RUN, never FAIL), pre-registered gates frozen
before any cell.

- **Run 1 (weak-baseline set):** the bare model failed most procedural
  tasks. Targeted repair content lifted procedural scores (+18.8pp overall,
  task-concentrated), and the output-contract guardian cut delivery
  failures 30% with zero paired cognition harm.
- **Run 2 (saturated set):** the bare model solved essentially everything
  (cognition rate 1.0). Nothing could be lifted — which made harm cleanly
  measurable: every forced intervention cost points; every abstaining path
  was harmless. This run also caught a router defect class and re-measured
  monolith harm with hardened graders.

**The one-layer harm law (run 2, the strongest single finding):** forced
second-pass repair on already-correct drafts damaged *delivery* in 7/24
cells (≥40-point drops from prose wrapped around contract-exact output) and
*never corrupted cognition* (0 flips in 48 forced-repair cells).
Re-prompting is a delivery risk, not a reasoning risk.

## Mechanism records

```json
{
  "mechanism": "inspect-then-repair (abstention-first)",
  "version": "0.1",
  "intended_effect": "intervene only on observable failure; NO REPAIR NEEDED is a first-class result",
  "trigger": ["draft exists", "observable defect signature or contract violation"],
  "counterindications": ["clean drafts (intervention measured harmful)"],
  "models_tested": ["claude-haiku-4-5 (execution)"],
  "task_classes": ["procedural", "competent", "knowledge-floor"],
  "trials": 120,
  "result": {"abstaining_paths_harm": "zero (24/24 and 16/24 abstentions, paired deltas 0)", "forced_intervention_cost": "-10 to -20pp"},
  "negative_transfer": {"measured": "none when abstaining"},
  "cost": {"added_tokens_when_abstaining": 0},
  "known_confounds": ["harm side measured on a saturated set; abstention's opportunity cost on failing work is bounded by run-1 repair evidence, not directly measured"],
  "evidence_level": "EXPERIMENTALLY_TESTED",
  "verdict": "default-on (the product's core posture)",
  "next_kill_test": "difficulty-calibrated set where abstention forgoes measurable recoverable lift"
}
```

```json
{
  "mechanism": "output-contract-guardian",
  "version": "0.1",
  "intended_effect": "repair delivery-format failures without touching content",
  "trigger": ["explicit output contract present", "required fields missing or decorated"],
  "counterindications": ["no contract declared"],
  "models_tested": ["claude-haiku-4-5 (execution)"],
  "task_classes": ["procedural", "competent", "knowledge-floor"],
  "trials": 48,
  "result": {"run1": "delivery failures 0.417 -> 0.292 (30% relative) with zero paired cognition harm", "run2": "0 fires on contract-clean drafts, 0 harm (correct abstention 24/24)"},
  "negative_transfer": {"measured": "none in either run"},
  "cost": {"median_added_tokens_when_fired": "small (single bounded reformat pass)"},
  "known_confounds": ["run-1 cognition-rate movement partly measurement-visibility (absent output ungradeable)", "run-2 could not exercise the fix pass (no delivery-failure surface)"],
  "evidence_level": "EXPERIMENTALLY_TESTED",
  "verdict": "default-on where a contract exists",
  "next_kill_test": "non-saturated set with a real delivery-failure surface; >=50% reduction gate must pass before PROMOTED"
}
```

```json
{
  "mechanism": "targeted micro-skill repair content",
  "version": "0.1",
  "intended_effect": "the smallest justified repair fixes a witnessed failure class",
  "trigger": ["draft observably wrong in a known failure class"],
  "counterindications": ["CORRECT drafts — forced application measured destructive (delivery layer)"],
  "models_tested": ["claude-haiku-4-5 (execution)"],
  "task_classes": ["procedural"],
  "trials": 48,
  "result": {"run1_failing_drafts": "+18.8pp procedural (task-concentrated: +66.7 best task, -20 worst)", "run2_correct_drafts": "-20pp, 7/24 paired delivery regressions >=40pp, 0 cognition flips"},
  "negative_transfer": {"measured": "delivery-layer only, ~29% of forced-repair cells on correct drafts"},
  "cost": {"added_tokens_live": "~1900 median (second pass)"},
  "known_confounds": ["run-1 grader artifacts depressed one task; run-2 baseline saturated"],
  "evidence_level": "NARROW",
  "verdict": "repair-when-failing only; never unconditional",
  "next_kill_test": ">=+15pp on a difficulty-calibrated fresh set with zero induced delivery regressions"
}
```

```json
{
  "mechanism": "adaptive repair routing (draft scanner)",
  "version": "0.1",
  "intended_effect": "automatically select which repair a draft needs",
  "trigger": ["post-draft scan"],
  "counterindications": ["currently: correct drafts (detector is correctness-blind)"],
  "models_tested": ["deterministic tool + claude-haiku-4-5"],
  "task_classes": ["procedural", "competent", "knowledge-floor"],
  "trials": 48,
  "result": {"run1": "0/24 fires (two deterministic defects: threshold arithmetic; contract-schema mismatch)", "run2_after_fixes": "8/24 fires, perfect abstention on competent/knowledge classes (12/12), but precision 0.375 on correct procedural drafts"},
  "negative_transfer": {"measured": "-10pp on saturated set, 4 paired delivery regressions"},
  "cost": {"scan": "deterministic, negligible"},
  "known_confounds": ["never validly exercised on failing drafts (run-1 dead, run-2 saturated)"],
  "evidence_level": "REJECTED (as shipped)",
  "verdict": "experimental, off by default; needs a draft-correctness veto signal",
  "next_kill_test": "precision >=0.70 / recall >=0.60 on a non-saturated set with the veto signal"
}
```

```json
{
  "mechanism": "monolithic domain skill (always-on large prompt)",
  "version": "0.1",
  "intended_effect": "one comprehensive thinking skill prepended to every task",
  "trigger": ["always-on"],
  "counterindications": ["knowledge-floor tasks (measured harm)", "already-competent work (cost without benefit)"],
  "models_tested": ["claude-haiku-4-5 (execution)"],
  "task_classes": ["procedural", "competent", "knowledge-floor"],
  "trials": 48,
  "result": {"run1": "highest overall mean but confounded by grader artifacts (documented + fixed in run 2 graders)", "run2": "knowledge-floor 60 vs 100 (two induced wrong answers, artifact-free), procedural -10 (delivery), competent unharmed"},
  "negative_transfer": {"measured": "real on knowledge-floor tasks; +1109 median tokens"},
  "cost": {"median_added_tokens": 1109},
  "known_confounds": ["n=6 knowledge-floor cells per run"],
  "evidence_level": "NARROW",
  "verdict": "available, honestly labeled; not the default",
  "next_kill_test": "beats inspect-repair pipeline on a calibrated set without knowledge-floor harm"
}
```

```json
{
  "mechanism": "layered deterministic grading (verify)",
  "version": "0.3",
  "intended_effect": "separate cognition from delivery from harness failure; verify the verifier before trusting it",
  "trigger": ["any evaluation"],
  "counterindications": [],
  "models_tested": ["deterministic"],
  "task_classes": ["all"],
  "trials": 240,
  "result": {"run1": "three grader artifact classes discovered (decoration under-credit, prose-fallback false credit, absent-output misclassified as cognition failure)", "run2": "hardened rules + 48-probe pre-seal battery: zero artifacts surfaced"},
  "negative_transfer": {"measured": "n/a"},
  "cost": {"per_cell": "negligible"},
  "known_confounds": [],
  "evidence_level": "EXPERIMENTALLY_TESTED",
  "verdict": "the shipped grading library (evals/graders/layered_common.py)",
  "next_kill_test": "artifact discovered in the wild that the probe battery misses"
}
```

Cognitive-core operations not listed above carry `DESIGNED` or
`SMOKE_TESTED` in their skill cards (`skills/`, `micro-skills/`) and have
not yet earned controlled-run records.

## What we will not claim

- No claim that any mechanism improves every model. Gains were measured on
  one small-model family; a competent model was measurably *harmed* by more
  prompting in specific classes.
- No claim of statistical certainty: n = 8 tasks per run; results are
  directional and pre-registered, not powered.
- No claim survives without its counterindication attached.
