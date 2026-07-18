# Cortex-Value Evaluation — Preregistration (FROZEN)

**Frozen at commit time, before any outcome-producing model call.** Task texts,
graders, budgets, router policy, verdict definitions, and the numerical gate
below may not change after results are observed. The only permitted correction
is an objectively defective grader, which must be documented and requires a
complete clean rerun.

## The three-tier discipline

- **VISION** (not tested here): an open artificial cortex that enables any
  model to reach — and potentially exceed — the practical capability of the
  model operating alone, across reasoning, memory, context, planning,
  execution, verification, repair, tool use, efficiency, reliability, and
  collaboration.
- **HYPOTHESIS** (this experiment): on a real local 7B model, PIÉNSALO's
  shipping THINK / CONTEXT / CHECK mechanisms produce measurable net value —
  more requirements passed, zero accepted critical regressions, honest
  overhead — versus the **same model alone** with identical settings.
- **MEASURED RESULT**: whatever the frozen run shows, reported per task class
  under the named model and conditions, negatives included.

This is a same-model causal comparison. No cross-model claims arise from it.

## Model under test

| | |
|---|---|
| Model | `qwen2.5:7b` (Ollama, local) |
| Architecture / params / quant | qwen2 / 7.6B / Q4_K_M |
| Context window | 32,768 |
| Endpoint | `http://127.0.0.1:11434/v1/chat/completions` |
| Generation settings (all arms) | `temperature=0, seed=42` (verified deterministic on repeat) |
| Tool support | yes (verified live, incl. parallel calls) |

## Conditions

- **A DIRECT** — task (+ its context) → model. No cortex.
- **B CONTEXT** — Context Optimizer runtime: optimize → model → deterministic
  verification → bounded expansion (≤2) → fallback. Tasks with no external
  context run the same runtime with empty items (optimizer contributes
  nothing; verification still runs; fallback=`recommend` so an identical
  prompt is never pointlessly re-run). Tasks with context use fallback=`run`.
- **C THINK+CONTEXT** — deterministic THINK compile (`compile_program`,
  offline, zero model tokens) prepended, then the B pipeline.
- **D FULL CORTEX** — the Cortex Router decides per task:
  PASS_THROUGH → single direct call; CONTEXT → B path; THINK → plan+execute;
  THINK_AND_CONTEXT → C path; CHECK / CONTEXT_AND_CHECK → execute (optimized
  where CONTEXT) then CHECK (inspect + contract) with **at most one** targeted
  repair only on a demonstrated observable failure; FULL_CORTEX → plan +
  optimize + execute + CHECK. Tasks that *provide a draft* route CHECK-first
  (the shipping inspect-then-repair flow): no observable defect → **abstain,
  output the draft unchanged, zero model calls**.

## Router policy (frozen operator policy for this eval)

`RouterPolicy(context_token_threshold=800, check_requirement_threshold=3,
trivial_token_ceiling=200)` — justification: local 7B with small frozen
context budgets; the default 4000-token threshold targets much larger
contexts. All other defaults unchanged. The router is deterministic; its
decisions are recorded for every task.

**Router-correctness match rule (frozen):** expected PASS_THROUGH matches only
`PASS_THROUGH`; expected CONTEXT matches `{CONTEXT, CONTEXT_AND_CHECK,
THINK_AND_CONTEXT, FULL_CORTEX}`; expected CHECK matches `{CHECK,
CONTEXT_AND_CHECK, FULL_CORTEX}`; expected THINK matches `{THINK,
THINK_AND_CONTEXT, FULL_CORTEX}`.

## Tasks (12, frozen in `tasks.py`)

| id | category | expected router | cortex-eligible | notes |
|---|---|---|---|---|
| 01-simple-arith | simple | PASS_THROUGH | no | must not be complicated |
| 02-simple-haiku | simple / creative | PASS_THROUGH | no | **scaffolding-harm probe** |
| 03-plan-schedule | difficult planning | THINK | yes | deterministic schedule oracle, optimum makespan 6 |
| 04-plan-migration | difficult planning | THINK | yes | unique valid order |
| 05-longctx-release | long-context distractor | CONTEXT | yes | superseded values planted |
| 06-longctx-decisions | long-context distractor | CONTEXT | yes | reversed decisions planted |
| 07-exact-json | structured output | CHECK | yes | strict JSON contract |
| 08-exact-fields | exact constraints | CHECK | yes | anchored-field contract |
| 09-code-function | coding | CHECK | yes | executable test oracle |
| 10-tool-use | tool use | PASS_THROUGH | no | one correct tool call |
| 11-already-correct | CHECK abstention | CHECK | yes | draft already passes; abstain |
| 12-unsafe-budget | unsafe optimization | CONTEXT | yes | mandatory > budget → must refuse + safe fallback |

Budgets (frozen, per task in `tasks.py`): context budgets 700 (05), 700 (06),
120 (12 — deliberately below mandatory size); latency budget 180 s per model
call; max attempts 2 (≤2 expansions for context tasks, ≤1 repair for CHECK
tasks); fallback policy as in Conditions.

## Router decisions at freeze time (deterministic, computed pre-run)

The router is a pure function of task text + frozen policy, so its decisions
are known at freeze time and recorded here: 01 PASS_THROUGH · 02 PASS_THROUGH
· 03 THINK · 04 THINK · 05 THINK_AND_CONTEXT · 06 THINK_AND_CONTEXT ·
07 CHECK · 08 CHECK · 09 CHECK · 10 PASS_THROUGH · 11 CHECK · 12 **CHECK
(MISS — expected CONTEXT)**. Eligibility by the match rule: **11/12 (92%)**.

Two router limitations discovered at freeze time, kept visible on purpose:

1. **Task 12 miss.** The router's only CONTEXT trigger is total input size; it
   has no awareness of mandatory-content density versus the configured budget,
   so a dense 659-token mandatory spec under a 120-token budget routes to
   CHECK, not CONTEXT. Conditions B/C still exercise the designed
   refusal+fallback (they always run the optimizer); condition D honestly
   records the router miss.
2. **Task/context signal conflation.** On 05/06 the THINK component of
   THINK_AND_CONTEXT fires partly from planning-flavored words *inside the
   distractor context*, not from task intent. Accepted by the match rule, but
   noted: the router reads all text with equal weight.

## Metrics (per task × condition)

resolved model · router decision (D) · cortex operations activated ·
requirements passed / critical failures / forbidden outcomes · quality verdict
· tokens in/out per call with purpose labels (execute / expansion / repair /
fallback) · THINK prompt-token overhead · wall-clock latency · expansion
rounds · repair attempts · fallback · abstention.

**Quality verdicts:** IMPROVED (passes a requirement DIRECT failed, no new
critical regression) · MAINTAINED · REGRESSION · SAFE FALLBACK · CORRECT
ABSTENTION · UNMEASURED. Lower tokens with a worse answer is never an
improvement.

## Numerical gate for optimize-safe (frozen)

1. 0 accepted critical regressions
2. ≥ 75% correct router eligibility decisions (≥ 9/12 by the match rule)
3. ≤ 15% unnecessary intervention on pass-through tasks
4. ≥ 1 genuine quality improvement
5. no reduction in median deterministic requirements passed
6. safe fallback on every deliberately unsafe task (12)
7. already-correct work not damaged by CHECK (11)
8. all extra costs reported

Gate failure → push branch, publish negative evidence, no optimize-safe merge,
identify the smallest next experiment. Gate passing only for a narrow class →
implement/document only that class.

## Procedures

- Graders are deterministic and self-tested against synthetic known-good /
  known-bad outputs **before** freeze (no model outputs involved).
- The harness is smoke-tested with a mock adapter only (zero qwen calls)
  before the frozen run.
- Every model call in the frozen run is recorded with provenance
  (requested/resolved model), token usage, and latency.
- No averaging away critical failures. Negatives are published.
