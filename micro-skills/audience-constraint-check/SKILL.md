---
name: audience-constraint-check
description: "Check a deliverable against its actual consumer: who reads it, what they do next, what format and register they need, and what they will assert downstream on its basis. Activate when the deliverable has a named audience beyond the requester, or its text will be forwarded, announced, or acted on by someone absent from the conversation."
license: MIT
---

# audience-constraint-check

**Trigger (observable):** The deliverable has a named audience other than the requester-as-peer — execs, customers, a board, an on-call engineer, a handoff recipient, a public reader — or its text will be forwarded, announced, or acted on by someone absent from this session.

**When NOT to activate:** Working notes for the requester themselves; audience constraints already gathered and applied this session; interactive conversation where the consumer is present and can push back.

## Procedure
1. Name the consumer and their next action: what will this person do within minutes of reading (decide, forward, execute, announce)?
2. List the constraints that consumer imposes: length ceiling, format (memo, runbook, table), expertise level and jargon budget, and political/PII/confidentiality boundaries for where it travels.
3. Identify what the consumer will assert downstream on the strength of this deliverable — and scope every claim to survive that assertion (an unverified item they'll announce as fact is your failure, not theirs).
4. Check the draft against each constraint; the answer's first two sentences must carry what the consumer needs for their next action.
5. Strip content serving the author rather than the reader — methodology tours, hedging walls, internal jargon.

## Required output
A consumer statement (who + next action), a constraint list with per-item draft compliance, and claims scoped to what the consumer will assert downstream.

## Verification
- The named consumer's stated next action is answerable from the deliverable's first two sentences.
- No claim in the deliverable exceeds what the consumer can safely assert downstream; unverified items are marked as such.

**Known risk:** Over-fitting to an imagined audience and stripping technical content the real reader needed. Mitigation: constraints must come from the task or known facts about the consumer, not stereotype.

**Max intended cost:** ≤250 added output tokens; one pass over the draft.

**Evidence status:** DESIGNED — specified from documented reasoning-failure modes; not yet executed as a packaged skill.

**Lineage:** Derived from an evidence-backed completion-integrity repair pattern (scoping claims to the promise the consumer will actually rely on) and a documented reasoning-failure mode: presenting confidence at a level the evidence does not support.
