# Model Provenance

Every claim Piénsalo records is a claim about *some model's* behavior. If
the model identity is wrong, every downstream conclusion is wrong. This
document specifies how identity is recorded and why fallback is prohibited.

## The rule

**Silent model fallback is prohibited.** If the configured model is
unavailable — auth failure, endpoint down, model retired — the run stops with
an explicit error. The runtime never substitutes a "close enough" model.

This rule was paid for: a runtime that silently fell back corrupted an entire
evidence base by attributing one model's behavior to another
([NEGATIVE-RESULTS.md](../NEGATIVE-RESULTS.md), NR-6). Detection took real
time because nothing *looked* wrong — the runs completed, the outputs were
plausible, and the labels were lies.

## What gets recorded

Every model call writes a provenance record into the evidence trail
(`.piensalo/evidence/`):

```
model_requested:   the identity you configured
model_reported:    the identity the provider/adapter reported back
adapter:           which adapter carried the call
timestamp:         when
run_id:            which lifecycle run this belongs to
```

If `model_requested` and `model_reported` disagree, the run is marked
`PROVENANCE_MISMATCH` and its outputs are excluded from evidence by default.
A mismatch is not always an attack — providers version models behind stable
aliases — but it is always *recorded*, because unexplained attribution is
how NR-6 happened.

## Honest limits

- **We record what the provider reports.** If an API endpoint routes between
  model versions behind one name, provenance captures the reported name plus
  any version metadata the provider exposes — it cannot see deeper than the
  API contract (THREAT-MODEL.md, T9 residual risk).
- **Local models:** the Ollama and generic command adapters record the model
  file/tag and, where available, its digest — the strongest provenance in
  the system, since nothing is behind an alias.
- **Manual copy/paste:** there is no runtime in the loop, so provenance is
  whatever you write down. The skills layer includes a one-line habit for
  this: state the model in the artifact.

## Operational guidance

- Pin the most specific model identifier your provider offers; aliases trade
  provenance for convenience.
- Treat `PROVENANCE_MISMATCH` in `piensalo doctor` output as a
  measurement-invalidating event: fix the configuration, then re-run affected
  work rather than relabeling it.
- Never edit provenance records to "correct" them. Evidence is immutable;
  a wrong record is superseded by a new run, not amended.

## Why this is a security topic, not just a measurement topic

Fallback is a spoofing primitive: a compromised or misconfigured adapter that
can substitute models can substitute *behaviors* — including weaker safety
behavior — while your logs say otherwise. Prohibiting silent fallback closes
the gap between what you think is running and what is running. That gap is
where the worst debugging weeks of this project lived.
