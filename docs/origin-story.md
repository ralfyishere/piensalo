# Origin Story

Rafael “Ralph” Peña ([@ralfyishere](https://github.com/ralfyishere)) began
Piénsalo as a preservation project, not a product. During development
it was internally codenamed "Fable Think"; it was renamed Piénsalo for public
release.

## Preserve first

The project started as an effort to preserve and study strong model behaviors
before access changed. When a model that reasons well may not always be
available — deprecations, pricing, access shifts — the question becomes
concrete: *can what makes it good be captured in a form that outlives it?*

The first hypothesis was the obvious one: write down everything the strong
model does well, hand it to other models as instructions, done.

## The obvious approaches failed, measurably

Because we measured from the start, the failures were specific rather than
vague — and each one is preserved in
[NEGATIVE-RESULTS.md](../NEGATIVE-RESULTS.md):

- **Giant prompts sometimes made weaker models worse.** More guidance
  competed with the task for attention, and easy-task performance dropped in
  controlled runs. More instruction is not more capability.
- **Full reasoning graphs added overhead.** Handing a weak model a complete
  knowledge structure regressed it — the cost of consuming the scaffolding
  exceeded its value.
- **Routing mistakes erased useful repairs.** A repair verified correct in
  isolation did nothing end-to-end, because a threshold defect and a schema
  defect routed it wrong. Correct components, corrupted outcome.
- **Output formatting destroyed correct work.** Models reached right answers
  and lost them at the delivery stage. Reasoning and delivery fail
  separately, so they must be inspected separately.
- **Silent model fallback corrupted attribution.** A runtime quietly
  substituted models, and every measurement from that period attributed one
  model's behavior to another. Evidence without provenance isn't evidence.

## The reframe

The pattern across all five failures: a monolith. One prompt, one pass, one
undifferentiated blob of "be smart" — with no way to see *where* things went
wrong, and therefore no way to fix anything smaller than everything.

So the project stopped trying to transplant intelligence and started building
an operating system for it: **thinking** separated from **inspection**,
inspection from **repair**, repair from **verification**, verification from
**evidence**, evidence from **continuation**. Each separation exists because
its absence produced a measured failure — that is the actual origin of the
architecture, and the reason the negative results stay published.

Two later discoveries completed the design. First, systems that always
intervene damage work that was already correct — abstention had to become a
first-class result (`NO REPAIR NEEDED`). Second, state that dies with a
context window forces every session to start over; evidence and continuation
had to persist.

## Where it stands

Piénsalo today is that operating system: a portable skills layer that
works with any model, and an optional runtime that adds state, bounds, and
measurement. The evidence base is young and says so plainly
([EVIDENCE.md](../EVIDENCE.md), README "Limitations").

Piénsalo is an independent open-source project. It is not affiliated with
or endorsed by Anthropic.
