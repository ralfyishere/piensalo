# Alpha Plan

Goal: learn whether Piénsalo works **in hands that aren't ours**, on
models we didn't tune for, before any public claim depends on it.

## Shape

- **Cohort:** 10+ independent users (not contributors, not friends-of-project
  who've seen internals). Mix of: agent builders, CLI-first developers,
  at least two local-model users, at least one manual/copy-paste-only user.
- **Duration:** 3 weeks of real usage on the user's own tasks — no assigned
  toy problems, because toy problems flatter systems like this.
- **Channel:** private repo access + a single feedback form per session,
  validated against [ALPHA-FEEDBACK-SCHEMA.json](ALPHA-FEEDBACK-SCHEMA.json).

## What we measure

| Question | Signal |
|---|---|
| Does install work outside our machines? | Fresh-install success rate, time-to-first-`doctor`-pass |
| Do verdicts match reality? | User-rated verdict correctness per `inspect`/`verify` run |
| Is abstention honest? | Rate of `NO REPAIR NEEDED`, and whether users agree it was right |
| Does repair help or churn? | Repairs accepted vs. reverted by the user |
| Negative transfer | Any task the user says went *worse* with Piénsalo — highest-priority signal we collect |
| Portability | Same skill, different model family: does behavior hold? |
| Friction | Where users stopped, swore, or dropped to raw prompting |

## Rules of the alpha

1. **We fix defects; we do not coach outcomes.** No telling users the "right
   way" to hold it mid-measurement.
2. **Negative reports are rewarded,** publicly credited (with consent), and
   feed [NEGATIVE-RESULTS.md](NEGATIVE-RESULTS.md) if confirmed.
3. **No telemetry.** All data arrives because a user chose to submit a form.
   The schema's consent field is enforced: nothing is published without it.
4. **Every session report is preserved** as evidence, favorable or not.

## Exit

The alpha ends when [ALPHA-EXIT-CRITERIA.md](ALPHA-EXIT-CRITERIA.md) is
satisfied — or when the evidence says the product isn't ready, in which case
the alpha ends by extending it, publicly.
