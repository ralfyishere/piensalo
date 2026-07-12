# Piénsalo — Technical Report (skeleton)

> **Status: SKELETON.** Sections marked TODO are unwritten or awaiting data.
> This file deliberately ships in skeleton form rather than being padded with
> unsupported prose — an empty section is honest; a confident empty claim is
> not. Numbers appear here only after they exist in [EVIDENCE.md](../EVIDENCE.md).

## Abstract

TODO — after v0.1 results are frozen. Will state: the problem (monolithic
prompting fails in measurable, layered ways), the approach (a cognitive OS
separating thinking / inspection / repair / verification / evidence /
continuation), and the measured outcomes *with their evidence levels and
sample sizes*, favorable and not.

## 1. Motivation

Summary available now in [origin-story.md](origin-story.md): the project
began as behavior preservation; five measured failures of the obvious
approaches (oversized prompts, full reasoning graphs, unrouted repairs,
delivery-stage corruption, silent fallback) forced the architecture.

TODO — expand with the quantitative form of each motivating failure, once
the corresponding entries in EVIDENCE.md are finalized.

## 2. System description

Available now: [architecture.md](architecture.md) (lifecycle, 11 operations,
two layers, state model, adapters).

TODO — formal definitions of each failure layer used by `classify_failure`;
worked example traces from real runs (pending consent/scrubbing review).

## 3. Evaluation methodology

Available now: [methodology.md](methodology.md) and
[evidence-levels.md](evidence-levels.md).

TODO — the concrete v0.1 evaluation: task suite composition, grader
specification, pre-registration record, exclusion rules as applied (not just
as designed).

## 4. Results

TODO — this section intentionally contains **no numbers** until they can be
copied from EVIDENCE.md with their levels attached. Planned tables:

- 4.1 Per-mechanism effects (paired comparisons, counts + intervals)
- 4.2 Abstention: `NO REPAIR NEEDED` accuracy on already-correct inputs
- 4.3 Negative transfer: where the system hurt, by how much
- 4.4 Cross-model portability deltas
- 4.5 Grader error analysis (both directions)

## 5. Negative results

Available now: [NEGATIVE-RESULTS.md](../NEGATIVE-RESULTS.md) (NR-1 … NR-8).

TODO — integrate with quantitative detail where publishable.

## 6. Limitations

Available now in README ("Limitations") and methodology ("Known
methodological limits"): young evidence base, small n, DESIGNED-only
mechanisms, one most-tested model family, author-built task suites.

TODO — update against v0.1 final state; add anything discovered in alpha.

## 7. Related work

TODO — honest positioning against: prompt-engineering frameworks, agent
frameworks, self-refine/self-correction literature, LLM-as-judge literature.
Requires a careful pass; placeholder citations would be worse than none.

## 8. Reproduction

TODO — exact commands, pinned versions, expected artifacts. Gate: a third
party must have actually reproduced before this section claims
reproducibility ([ALPHA-EXIT-CRITERIA.md](../ALPHA-EXIT-CRITERIA.md), item 4).

---

*Piénsalo is an independent open-source project. It is not affiliated
with or endorsed by Anthropic.*
