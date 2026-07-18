# Cortex Gateway — The Cortex Router

One inspectable, **deterministic** policy layer decides whether the cortex
*would* intervene. In observe mode the decision is **shadow only** — recorded,
never acted on. There is no opaque classifier: every decision carries the exact
reasons and features it was computed from, and the same request always yields
the same decision.

## Decisions

`PASS_THROUGH · THINK · CONTEXT · CHECK · THINK_AND_CONTEXT · CONTEXT_AND_CHECK ·
FULL_CORTEX · ABSTAIN · FALLBACK`

`PASS_THROUGH` is the default and a **successful** outcome. The router must not
recommend intervention merely because it is available (abstention-first).

## Signals (deterministic, from the normalized request)

| Signal | Source | Used for |
|---|---|---|
| `input_tokens_est` | sum of message token estimates | CONTEXT threshold |
| `contract_signal_hits` | regex over text (`json`, `must …`, `exactly`, `format`, …) | CHECK |
| `numbered_requirements` | count of numbered/bulleted lines | CHECK |
| `planning_signal_hits` | regex (`plan`, `step by step`, `decompose`, …) | THINK |
| `ambiguity_signal_hits` | regex (`maybe`, `unclear`, `figure out`, …) | recorded |
| `has_tools` / `tool_count` / `has_images` | request fields | recorded |
| `stream` | request field | recorded |
| `exact_delivery_contract` | regex (`output only`, `nothing else`, `exactly N lines`, `verbatim`, …) | **suppresses THINK** |

**EXACT_DELIVERY_CONTRACT.** When a task demands verbatim output shape (JSON
only, code only, exact line counts, fixed anchors, no commentary), the full
THINK program is suppressed and the suppression reason is recorded — attaching
plan scaffolding to such tasks was measured to cause exact-format regressions
on a competent local 7B (NR-11, repaired and re-verified on the frozen rerun).
Known limitations, deliberately documented and pinned by tests: the lexical
trigger set is not exhaustive (a novel phrasing means THINK applies as
before), and exact-format wording *quoted inside source material* fires the
signal (THINK is skipped — abstention, not damage). No model-assisted
classification in this layer.

Thresholds live in `RouterPolicy` (inspectable, operator-overridable):
`context_token_threshold` (4000), `check_requirement_threshold` (3),
`trivial_token_ceiling` (200).

## Decision rule (in order)

1. **Trivial-and-clear** (`input ≤ trivial_ceiling`, no signal) → `PASS_THROUGH`.
2. Otherwise compute `wants_context`, `wants_check`, `wants_think` from
   thresholds and **combine**:
   - all three → `FULL_CORTEX`
   - context+check → `CONTEXT_AND_CHECK`; think+context → `THINK_AND_CONTEXT`
   - single → `THINK` / `CONTEXT` / `CHECK`
   - none cleared → `PASS_THROUGH`
3. Confidence is a bounded heuristic: `min(0.6 + 0.12·n_signals, 0.95)`.

## Example decision (recorded shape)

```json
{
  "decision": "CONTEXT_AND_CHECK",
  "reasons": [
    "input estimate 5210 tokens >= context threshold 4000",
    "4 deterministic output requirement(s) detected (>= threshold 3)"
  ],
  "confidence": 0.84,
  "intervention_budget": {"max_extra_latency_ms": 2500, "max_extra_tokens": 1200, "max_attempts": 2},
  "features": { "...": "the exact signals above" },
  "shadow": true
}
```

## Observe-mode honesty

`gateway report` reports a **shadow would-intervene rate**, never an
"intervention rate" — because nothing was intervened on. Acting on decisions is
a later-stage capability, each gated on evidence. Model-assisted routing is out
of scope here; if added, its recommendation stays bounded, recorded, and
overridable.
