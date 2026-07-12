---
name: recover-real-objective
description: "Recover the objective behind a solution-shaped or vague request before executing it literally. Activate when a request names a solution or knob rather than an outcome ('increase the timeout'), or uses a vague referent ('fix it', 'make this better') with no stated goal. Single intervention: state the interpreted objective in one line, check the literal request against it, flag any divergence."
license: MIT
---

# recover-real-objective

**Trigger (observable):** The request names a solution or knob rather than an outcome ('increase the timeout', 'set retries to 5'), or uses a vague referent ('fix it', 'make this better') with no stated goal or acceptance criterion.

**When NOT to activate:** The request already states its objective or acceptance criteria ('so that X', 'because Y'); single-fact lookups; requests where the literal action and the plausible objective are obviously identical.

## Procedure
1. Quote the literal request in one line.
2. Write the most plausible underlying objective in one line — the problem this request is trying to solve, not a paraphrase of the request.
3. Check: does executing the literal request achieve that objective? Name any divergence (symptom-fix, proxy target, wrong layer).
4. If they diverge, proceed with the literal request only if the divergence is cheap; otherwise state the interpretation and the better-aimed action in one line before acting. Ask a question only if a wrong guess is expensive.
5. Carry the stated interpretation into the final answer so the user can veto it.

## Required output
A one-line 'Interpreting this as: <objective>' statement, plus a named divergence (or 'literal request serves the objective directly').

## Verification
- The output contains a one-line stated objective that is not a paraphrase of the request (deterministic check).
- The chosen literal action is explicitly checked against that objective — divergence named or ruled out (judgment check).

**Known risk:** Over-interpretation: inventing an objective the user never had and drifting from the literal ask. Mitigation: the literal request stays the default; interpretation is stated, never silently substituted.

**Max intended cost:** ≤150 added output tokens; no added tool calls.

**Evidence status:** SMOKE_TESTED — executed end-to-end in live sessions and behaves as specified; no measured lift is claimed.

**Lineage:** Distilled from an evidence-backed diagnose-the-instrument-first repair pattern and from a documented reasoning-failure mode: solving the stated proxy (the knob, the symptom) instead of the underlying objective.
