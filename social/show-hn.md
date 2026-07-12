# Show HN post

## Title

Show HN: Piénsalo – an open cognitive OS for AI models (publishes its own negative results)

*(78 chars. Alternates if too long or taken:*
*"Show HN: Piénsalo – give any AI a separate inspect/repair/verify loop";*
*"Show HN: Piénsalo – a cognitive OS for LLMs that knows when to do nothing")*

## URL

https://github.com/piensalo/piensalo

## First comment (post immediately after submitting)

Hi HN — author here.

Piénsalo is an open cognitive operating system for AI models and agents:
it separates thinking, inspection, repair, verification, evidence, and
continuation into distinct operations. Six CLI modes (think / inspect /
repair / verify / loop / skill), plus a portable skills layer that's plain
text and works in any agent — or pasted into any chat, no runtime needed.

Why it exists: the project started as an attempt to preserve strong model
behaviors by writing them down and handing them to other models. That failed
in measurable ways — a big instruction block made a competent model *worse*
at easy tasks; a full reasoning graph regressed a weak model; one correct
repair was erased by a routing bug; correct answers got destroyed at the
formatting stage; and at one point silent model fallback corrupted a whole
evidence base by attributing one model's behavior to another. Each failure
forced a separation, and the separations became the product. The failures are
permanently published in NEGATIVE-RESULTS.md.

Things I'd want to know before trying it:

- **It knows when to do nothing.** "NO REPAIR NEEDED" is a first-class
  verdict — in our runs, abstention beat intervention on already-correct
  work, so we grade abstention like any other capability.
- **Every capability has an evidence level** (DESIGNED → SMOKE_TESTED →
  EXPERIMENTALLY_TESTED → REPLICATED → PROMOTED, plus NARROW/REJECTED). Some
  mechanisms are still DESIGNED-only and the docs say which. I will not claim
  guaranteed improvement, here or anywhere.
- **Honest limits:** young evidence base, small n, one model family
  most-tested so far. Cross-model claims are weaker than same-family claims
  until the adapters mature.
- **Boring security posture:** core runs offline, zero telemetry, no network
  without an explicit adapter, no silent model fallback (hard stop instead),
  skills are inert text with a scanner (`piensalo skill scan`), and
  destructive actions always require approval.

The contribution I most want from HN: adversarial reproduction. Run the
benchmark, try to break the abstention behavior, find a configuration where
it makes results worse — negative-transfer reports get published with
credit. MIT licensed.

Piénsalo is an independent open-source project. It is not affiliated with
or endorsed by Anthropic.

Happy to answer anything, including about the failures.
