# Alpha Tester Instructions — PIÉNSALO

Time budget: ~45 minutes total. Everything runs offline on your machine.

## Setup
1. Unpack/clone the repository you received privately.
2. Follow `ALPHA-START-HERE.md` steps 1–2 (install + flagship demo).
3. If anything in setup fails, STOP and report that alone — a failed
   install on your platform is a complete, valuable alpha result.

## The one-real-task protocol
1. Choose one real task from your own work (not a toy).
2. Produce a draft answer with whatever model/workflow you normally use.
3. Run: `piensalo inspect --task <task-file> --draft <draft-file>`
   (add `--contract <contract.json>` only if you wrote an output contract).
4. If a repair was selected, optionally run `piensalo repair ...` and apply
   its guidance with your model, then `piensalo verify ...` the result.
5. Judge the outcome yourself. You are the grader, not the tool.

## What to record (per ALPHA-FEEDBACK-SCHEMA.json)
- environment: OS, Python version, install method (uv/pip), exit codes
- task_domain: coding / math / research / strategy / writing / other
- model_used: name + how invoked (the tool never sees your API keys)
- outcome, one of:
  - HELPED — found a real defect / repair improved the result
  - HARMED — repair or advice made the result worse
  - ABSTAINED_CORRECTLY — said no intervention needed, and that was right
  - ABSTAINED_WRONGLY — said no intervention needed, but a real defect existed
  - INVENTED_PROBLEM — flagged a defect that wasn't real
  - TOOL_FAILURE — crash, confusing output, unusable UX
- evidence: the exact inspect/verify output (paste), and what YOU judged
- friction: anything that slowed or confused you, however small
- would_use_again: yes / no / only-if (say what)

## Rules of honesty (ours and yours)
- Do not try to make the tool look good. ABSTAINED_CORRECTLY and
  INVENTED_PROBLEM reports are worth more than HELPED reports.
- Report exact commands and exit codes, not impressions of them.
- Your feedback may be quoted (anonymized) in public evidence documents;
  say so if you don't want that.

## Returning results
Send the filled JSON (or the markdown tracker row from
`ALPHA-RESULT-TRACKER.md`) back through the private channel you received
this repository from. Do not post publicly during the alpha.
