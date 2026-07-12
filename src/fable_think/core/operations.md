# The cognitive core — 11 operations

`operations.json` is the machine-readable source of truth; this file is the
human-readable companion. An operation is a bounded, verifiable unit of
thinking: it has an observable trigger, a 3–6 step procedure, an explicit
stop condition, known failure signatures, and a mapping from each signature
to a repair micro-skill in `fable_think/repair/library/`.

The core thesis: **attempt first, inspect the observable draft, repair only
a demonstrated defect, verify in layers.** Operations marked
`EXPERIMENTALLY_TESTED` carry direct experimental evidence from controlled
eval runs; operations marked `DESIGNED` are derived from documented failure
modes but have no direct experimental test yet. The distinction is part of
the product — evidence status is never rounded up.

## The program shape

A full cognitive program runs the operations in this order (the compiler
selects a subset when the task doesn't need all of them):

1. **recover_objective** — state the objective behind the request; check the
   literal ask against it.
2. **identify_constraints** — extract every must/only/never clause verbatim
   into a hard/soft table.
3. **decompose_problem** — split into units with observable completion
   tests; unknowns are listed, never hidden.
4. **locate_load_bearing_uncertainty** — name the one uncertainty whose
   wrong resolution invalidates the most downstream work.
5. **select_cheapest_discriminating_test** — pick the cheapest test whose
   outcomes actually separate the live branches; pre-register predictions.
6. **execute** — run the bounded unit; record what was done, not what was
   intended; stop at the budget boundary.
7. **inspect_result** — scan the draft for observable defect signatures;
   score candidates precision-first; select at most one repair or abstain
   (NO REPAIR NEEDED is a success, not a penalty).
8. **classify_failure** — assign exactly one failure layer; absent output is
   UNMEASURED cognition, never a wrong answer; decoration never fails
   cognition.
9. **apply_targeted_repair** — one demonstrated defect, one repair; correct
   portions stay untouched.
10. **verify** — layered verdict: cognition on decoration-stripped text,
    contract compliance on raw text; a fallback parse may only lower credit.
11. **deliver** — map every requested item to its location; partition the
    claim into delivered-and-verified / delivered-unverified / not
    delivered.

## Field reference

| Field | Meaning |
|---|---|
| `trigger` | Observable condition that activates the operation. |
| `inputs` / `outputs` | Named artifacts the operation consumes/produces. |
| `procedure` | 3–6 concrete steps. |
| `stop_condition` | When the operation is done — bounded by construction. |
| `failure_signatures` | How this operation is observed to go wrong. |
| `repair_mappings` | Signature → micro-skill in the repair library. |
| `verification` | How to check the operation ran correctly. |
| `cost_expectation` | Intended cost ceiling. |
| `evidence_status` | `EXPERIMENTALLY_TESTED` or `DESIGNED` — never inflated. |
