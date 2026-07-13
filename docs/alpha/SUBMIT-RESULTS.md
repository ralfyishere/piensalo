# Submit a Real-Task Result

The evidence PIÉNSALO needs most cannot be manufactured by its author:
independent results on real tasks. This guide takes ~5 minutes after you've
run one real task ([START-HERE.md](START-HERE.md)).

## The five outcomes we track — all equally welcome

| Outcome | Meaning |
|---|---|
| `HELPED` | inspect/repair found a real defect, and fixing it improved the result |
| `HARMED` | the intervention made a correct or acceptable draft worse |
| `NO REPAIR NEEDED` | it abstained on your draft — and abstention was the right call |
| `INVENTED A PROBLEM` | it flagged a defect that wasn't real |
| `FAILED TO INSTALL` | you couldn't get it running (platform, Python, tooling — tell us which) |

`NO REPAIR NEEDED` reports are success data, not absence of data — restraint
is the product's signature claim and it needs measuring. `INVENTED A
PROBLEM` reports are the most valuable thing you can send.

## How to submit

1. Fill the fields in [ALPHA-FEEDBACK-SCHEMA.json](ALPHA-FEEDBACK-SCHEMA.json)
   (environment, task domain, model used, outcome, the exact `inspect`/`verify`
   output, your own judgment of what was right).
2. Open a **GitHub Issue** on
   [ralfyishere/piensalo](https://github.com/ralfyishere/piensalo/issues)
   titled `alpha-report: <outcome> — <domain>` and paste the JSON.
3. Strip anything confidential from your task/draft first — or describe the
   shape of the task instead of pasting it.

Aggregated results are published in the open (anonymized); say so in the
issue if you don't want to be quoted. No fabricated entries will ever appear
in the tracker — an empty tracker is an honest tracker.
