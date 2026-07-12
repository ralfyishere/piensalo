# Launch Plan

Internal playbook for taking Fable Think public. The rule that governs
everything below: **we launch when the alpha gate passes, not when the
narrative is ready.** Claims made in public materials may not exceed what
EVIDENCE.md supports on launch day.

## The narrative (accurate version)

This project began as an effort to preserve and study strong model behaviors
before access changed. The obvious approaches failed, measurably:

- Giant prompts sometimes made weaker models **worse**, not better.
- Full reasoning graphs added overhead that regressed a weak model.
- A correct repair was erased by routing mistakes (a threshold and a schema
  defect) before it could help.
- Correct reasoning was destroyed at the delivery stage by output formatting.
- Silent model fallback corrupted attribution across an entire evidence base.

Each failure forced a separation: thinking apart from inspection, inspection
apart from repair, repair apart from verification, verification apart from
evidence, evidence apart from continuation. That separation *is* the product.
The full story: [docs/origin-story.md](docs/origin-story.md). The failures
themselves, preserved: [NEGATIVE-RESULTS.md](NEGATIVE-RESULTS.md).

What we say and don't say:

- **Say:** "changed measured outcomes in our runs", "evidence levels",
  "published negative results", "abstention is a first-class result".
- **Never say:** guaranteed improvement, works for every model, endorsed by
  anyone. Every public artifact carries: *"Fable Think is an independent
  open-source project. It is not affiliated with or endorsed by Anthropic."*

## Launch gate (must all be checked)

The full checklist with measurement details is
[ALPHA-EXIT-CRITERIA.md](ALPHA-EXIT-CRITERIA.md). Summary:

- [ ] Fresh clone → working install via one command, on a machine that never
      saw the project
- [ ] One-command install verified for all three paths (uvx / pipx / skills)
- [ ] Runs demonstrated on **3 model families** (incl. one local/offline)
- [ ] The published benchmark **reproduces from the public repo alone**
- [ ] Negative transfer measured and published; abstention rate measured and
      published
- [ ] `skill scan` + secret scans pass on the repo itself; no private
      identifiers anywhere in history
- [ ] **10 independent alpha users** completed the feedback loop
      ([ALPHA-PLAN.md](ALPHA-PLAN.md), schema:
      [ALPHA-FEEDBACK-SCHEMA.json](ALPHA-FEEDBACK-SCHEMA.json))
- [ ] **5 case studies** published with full evidence trails
- [ ] Docs complete: README, SECURITY, THREAT-MODEL, evidence-levels,
      CONTRIBUTING all reviewed against actual behavior
- [ ] 60-second demo recorded and checked against the real CLI output
- [ ] CODE_OF_CONDUCT enforcement contact finalized

## Launch sequence

1. **T-7 days** — freeze claims. Every capability statement in README/social
   gets checked against EVIDENCE.md; anything unsupported is cut or
   downgraded to its honest level.
2. **T-3 days** — final security pass: secret scan on full history, skill
   scan on shipped skills, license/notice review.
3. **T-0, morning** — tag `v0.1.0`, publish package, verify
   `uvx piensalo doctor` works from the public index on a clean machine.
4. **T-0** — Show HN ([social/show-hn.md](social/show-hn.md)), X thread
   ([social/x-thread.md](social/x-thread.md)), LinkedIn
   ([social/linkedin.md](social/linkedin.md)). Demo per
   [social/demo-script.md](social/demo-script.md).
5. **T+1 to T+7** — answer everything; file every reported defect as an
   issue; publish a "week one, including what broke" note. Negative feedback
   gets the same visibility as praise.

## Failure handling

If a launch-day claim turns out wrong, the correction gets posted in the same
channels with the same prominence as the original claim, and propagated to
every document that restated it. That policy is part of the product.
