# 60-Second Demo Script

Screen recording of a terminal. **No voiceover needed** — the transcript
carries the story; on-screen text cards do the framing. Record against the
shipping build and verify the output shapes match
([ALPHA-EXIT-CRITERIA.md](../ALPHA-EXIT-CRITERIA.md), item 11) — never
staged output.

Recording setup: dark terminal, large monospace font (18pt+), window sized
16:9, typing at natural speed (use a replay tool; don't hand-type live).

---

**0:00–0:04 — Title card (text on black)**

> Fable Think
> Give any AI a better way to think.

**0:04–0:12 — The task**

Type:

```
fable-think think "Our plan is $100/mo. Marketing wants '30% off, plus an
extra 20% off for annual billing'. Finance says that's 50% off total.
Draft the pricing note."
```

Output scrolls: `recover_objective` (stated vs. actual — the real question
is whether 30% + 20% = 50%), the 4-step bounded program, `execute → draft-v1`.

**0:12–0:16 — Text card**

> The draft looks fine.
> Looking fine is not evidence.

**0:16–0:26 — Inspection finds the defects**

```
fable-think inspect draft-v1
```

Hold on the two findings:

```
FINDING [numeric]   compounded percentage asserted, not re-derived ("50% total")
FINDING [delivery]  missing final recommendation
verdict: REPAIR REQUIRED
```

**0:26–0:36 — Targeted repair**

```
fable-think repair draft-v1 --strategy rederive-numbers
```

Hold on the derivation — this is the money shot of the video:

```
$100 → 30% off → $70.00 → 20% off → $56.00
effective discount: 44%, not 50%
applied smallest justified repair: 2 edits
```

**0:36–0:42 — Verification**

```
fable-think verify draft-v2
```

```
arithmetic re-derived independently: 0.70 × 0.80 = 0.56 ✓ (44% effective)
verdict: PASS — evidence recorded
```

**0:42–0:50 — The abstention beat**

Text card (2s):

> And when the work is already correct?

```
fable-think inspect other-draft
```

```
no defects found at any layer
verdict: NO REPAIR NEEDED
```

Text card:

> Knowing when to do nothing is a capability.

**0:50–0:57 — Continuation**

```
fable-think loop --continue
```

Show: evidence preserved, model provenance recorded, budget `1 of 3 repair
cycles used`, next action.

**0:57–0:60 — Close card**

> fable-think · open source · MIT
> github.com/fable-think/fable-think
>
> Independent open-source project.
> Not affiliated with or endorsed by Anthropic.

---

## Cut checklist before publishing

- [ ] Output on screen is real CLI output from the shipping build
- [ ] The 44% derivation is legible at 1x speed on a phone screen
- [ ] Total runtime ≤ 62s
- [ ] Independence line present on the close card
- [ ] No paths, hostnames, or usernames visible in the prompt line
