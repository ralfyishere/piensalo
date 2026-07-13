# PIÉNSALO

## Give any AI a better way to think.

**Piénsalo is an open cognitive operating system for AI models and agents.**
It helps models understand the real objective, structure difficult work,
inspect their output, repair specific failures, verify the result, and
continue across sessions. Not a giant system prompt. Not a model replacement.
An artificial cortex you can install, inspect, test, and extend.

Piénsalo — "think it through." Pronounced: pee-EN-sa-lo.

Most AI tooling makes models *produce more*. Piénsalo makes them *think better*:
it separates thinking, inspection, repair, verification, evidence, and continuation
into distinct, inspectable operations — and it knows when the right move is to do
**nothing** (`NO REPAIR NEEDED` is a first-class result).

---

## 60 seconds, start to finish

```text
$ piensalo think "Our plan is $100/mo. Marketing wants '30% off, plus an
  extra 20% off for annual billing'. Finance says that's 50% off total.
  Draft the pricing note."

▸ recover_objective
    stated:  draft the pricing note
    actual:  determine what the stacked discount really is, then draft a
             note finance can sign off on
    load-bearing uncertainty: does 30% + 20% actually stack to 50%?

▸ cognitive program (bounded, 4 steps)
    1. re-derive the stacked discount from first principles
    2. compare against the 50% claim
    3. draft the note with the derived number
    4. verify arithmetic and completeness before delivery

▸ execute → draft-v1 produced

$ piensalo inspect draft-v1

  FINDING [numeric]    compounded percentage asserted, not re-derived ("50% total")
  FINDING [delivery]   missing final recommendation — note ends mid-analysis
  verdict: REPAIR REQUIRED   (layers: numeric, delivery)

$ piensalo repair draft-v1 --strategy rederive-numbers

  $100 → 30% off → $70.00 → 20% off → $56.00
  effective discount: 44%, not 50%
  applied smallest justified repair: 2 edits
    · corrected the effective-discount figure
    · added the missing final recommendation

$ piensalo verify draft-v2

  arithmetic re-derived independently: 0.70 × 0.80 = 0.56  ✓  (44% effective)
  completeness: final recommendation present               ✓
  verdict: PASS — evidence recorded

$ piensalo inspect other-draft        # a draft that was already correct

  no defects found at any layer
  verdict: NO REPAIR NEEDED              # abstention is a first-class result

$ piensalo loop --continue

  state:      1 task verified · evidence preserved in .piensalo/evidence/
  provenance: model declared and recorded — silent fallback prohibited
  budget:     1 of max 3 repair cycles used (bounded loop)
  next:       deliver draft-v2, or stop
```

That's the whole lifecycle: **user goal → recover actual intent → bounded
cognitive program → execute → inspect the observable result → identify the
failure layer → smallest justified repair → verify → preserve evidence and
state → next action or stop.**

## Install

```bash
# Run without installing
uvx piensalo doctor

# Or install the CLI
pipx install piensalo

# Or add only the portable Agent Skills (no runtime required)
npx skills add piensalo
```

Run `piensalo doctor` first — it checks your environment and tells you exactly
what will and won't work, offline.

## Why this is different

**An open artificial cortex for AI models and agents.**

| Typical approach | Piénsalo |
|---|---|
| One giant prompt does everything | Thinking, inspection, repair, verification are **separate operations** with separate outputs |
| "Try again" on failure | Failure is **classified by layer** (objective, plan, numeric, delivery…), then given the **smallest justified repair** |
| Model output is the end state | Every run leaves **inspectable evidence**; the next action starts from evidence, not vibes |
| Always intervenes | Knows when to **abstain** — `NO REPAIR NEEDED` on already-correct work is a success, not a no-op |
| Unbounded agent loops | Loops are **bounded**, with recorded model provenance; silent model fallback is prohibited |
| Tied to one vendor | **Portable skills** work in any agent; the optional runtime adds state, adaptivity, and measurement |

## The cognitive core: 11 operations

| # | Operation | What it does |
|---|---|---|
| 1 | `recover_objective` | Recover what the user actually needs, not just what was typed |
| 2 | `identify_constraints` | Make budgets, formats, and hard limits explicit before work starts |
| 3 | `decompose_problem` | Break the task into units small enough to verify individually |
| 4 | `locate_load_bearing_uncertainty` | Find the unknown that, if wrong, invalidates everything downstream |
| 5 | `select_cheapest_discriminating_test` | Choose the cheapest check that can actually falsify the uncertainty |
| 6 | `execute` | Run the bounded cognitive program |
| 7 | `inspect_result` | Examine the observable output — not the intention behind it |
| 8 | `classify_failure` | Assign each defect to a layer so repair targets the right thing |
| 9 | `apply_targeted_repair` | Smallest justified change; never a rewrite when an edit suffices |
| 10 | `verify` | Independently re-derive and check — a separate capability, not a re-read |
| 11 | `deliver` | Ship the result with its evidence trail, or abstain and say so |

## Two layers

1. **Portable Agent Skills** — plain instruction files that work in any agent
   that reads skills. No runtime, no dependencies, copy-paste friendly.
2. **Optional runtime** — the `piensalo` CLI adds persistent state, bounded
   adaptive loops, model provenance tracking, and measurement.

### Portable skills

| Skill | Trigger | What it adds |
|---|---|---|
| `objective-recovery` | Any non-trivial request | Separates stated ask from actual need before work begins |
| `cheapest-test` | A load-bearing unknown exists | Picks the cheapest check that can falsify it |
| `failure-classification` | An output has defects | Assigns each defect to a layer before any fix |
| `targeted-repair` | A classified failure | Applies the smallest justified change |
| `independent-verify` | Before delivery | Re-derives numbers and claims independently of the draft |
| `abstention-check` | Reviewing existing work | Returns `NO REPAIR NEEDED` when the work is already correct |
| `evidence-ledger` | Any completed step | Records what was checked and what remains unverified |
| `loop-continuation` | Multi-session work | Resumes from preserved state instead of re-deriving context |

The current evidence status of each skill is tracked per-skill in
[EVIDENCE.md](EVIDENCE.md) — statuses are earned, not asserted (see next section).

## Evidence philosophy

**Every capability ships with receipts.** Each mechanism in Piénsalo carries
an explicit evidence level:

`DESIGNED → SMOKE_TESTED → EXPERIMENTALLY_TESTED → REPLICATED → PROMOTED`
(with `NARROW` and `REJECTED` as honest terminal states).

Nothing gets promoted without passing the gates: dev validation, a fresh
held-out test, regression on prior wins, cost accounting, a negative-transfer
check, and a paired no-harm comparison. Definitions and gates:
[docs/evidence-levels.md](docs/evidence-levels.md). Current claims and their
receipts: [EVIDENCE.md](EVIDENCE.md). Things that failed and stay published:
[NEGATIVE-RESULTS.md](NEGATIVE-RESULTS.md).

## Model support

| Interface | How | Network required |
|---|---|---|
| Manual copy/paste | Portable skills as plain text — works with any model, anywhere | No |
| Claude / Claude Code | Native skills + runtime adapter | Only for the model call |
| OpenAI-compatible APIs | Runtime adapter (any endpoint speaking the API) | Only for the model call |
| Ollama / local models | Runtime adapter, fully offline | No |
| Generic command adapter | Pipe any CLI-invocable model through stdin/stdout | No (unless your command does) |

> **Testing status (honest):** the offline core and manual mode are fully
> tested. Live-model runs so far cover the **Claude family only** (see
> [BENCHMARKS.md](BENCHMARKS.md)). The OpenAI-compatible, Ollama, and
> generic adapters are unit-tested but not yet exercised against live
> providers — treat them as **experimental** until reproduced.

The core works **offline** with **zero telemetry**. Model identity is recorded
on every run; if a configured model is unavailable, Piénsalo stops and says
so — **silent model fallback is prohibited** ([docs/model-provenance.md](docs/model-provenance.md)).

## Obsidian Studio (optional)

An optional companion vault that renders your cognitive programs, inspection
traces, and evidence ledger as linked, navigable notes in Obsidian. Strictly
read-your-own-files: it points at `.piensalo/` state, adds nothing to the
core, and the core never depends on it.

<!-- assets/obsidian-studio.png — screenshot placeholder, added when Studio ships -->

## Security defaults

Off by default, forever: telemetry, network access without an explicit adapter,
uploads, silent model fallback, destructive actions without approval, arbitrary
shell from untrusted skill text, secrets in logs, hidden persistence,
auto-publish. `piensalo skill scan` vets third-party skills before install;
`piensalo doctor` audits your configuration. Details:
[SECURITY.md](SECURITY.md) · [THREAT-MODEL.md](THREAT-MODEL.md) ·
[docs/operator-boundaries.md](docs/operator-boundaries.md).

## Limitations (read this)

We would rather undersell than overclaim:

- **The evidence base is young.** Sample sizes are small; confidence intervals
  are wide. Treat every number in [EVIDENCE.md](EVIDENCE.md) as provisional.
- **Some mechanisms are DESIGNED-only.** They are engineered from failure
  analysis but not yet experimentally tested — their evidence level says so.
- **One model family is most-tested.** Cross-model claims are weaker than
  same-family claims until adapters mature.
- **No guarantees.** Piénsalo changed measured outcomes in our runs; it may
  not in yours. It has also *hurt* performance in specific configurations —
  those results are published in [NEGATIVE-RESULTS.md](NEGATIVE-RESULTS.md).

## Contributing

New skills, verifiers, model adapters, tasks, benchmark reproductions, and
negative-result reports are all first-class contributions — see
[CONTRIBUTING.md](CONTRIBUTING.md) and
[docs/good-first-issues.md](docs/good-first-issues.md). Every new skill needs
an observable trigger, a stop condition, and an evaluation plan; we don't merge
vibes.

## Roadmap

- **v0.1 (alpha)** — cognitive core, portable skills, CLI, evidence discipline
- **v0.2** — model adapters hardened, public case studies
- **v0.3** — public benchmark season: reproducible tasks, third-party runs

Full detail: [ROADMAP.md](ROADMAP.md).

## Citation

If Piénsalo is useful in your research, please cite it — see
[CITATION.cff](CITATION.cff).

## Independence

Piénsalo is an independent open-source project. It is not affiliated with or
endorsed by Anthropic.

## License

[MIT](LICENSE) © 2026 Piénsalo contributors

---

*Think through hard work. Verify what matters. Know when to stop.*
