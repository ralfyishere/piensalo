---
name: fable-write
description: "Writing and content-creation program: build the claim ledger and constraint checklist first, draft divergently, run separate argument/accuracy/style critic passes, compress without losing ledger items. Use for high-stakes prose - announcements, notices, abstracts, memos, docs - where every claim must be defensible and omissions are costly. Trigger phrases: 'draft', 'write the announcement/memo/notice', 'tighten this'."
license: MIT
---

# fable-write

A structured reasoning program for writing and content creation, distilled from curated expert reasoning traces. Work the numbered steps in order; each step's output feeds the next. Do not skip steps silently - if one does not apply, say so in one line.

## Primary workflow
1. **Recover real objective** - Per intent-clarity: decode what the requester actually needs before optimizing anything. Distinguish the literal words from the mission; if the request was corrected or rephrased, the delta between versions IS the intent.
2. **Separate objective from proxy** - Per intent-clarity's symptom-vs-mission rule and product-thinking: split the measurable proxy (the metric, the named fix, the requested feature) from the underlying goal it stands for.
3. **Extract constraints** - Enumerate hard constraints (correctness, budget, deadline, interfaces, irreversibility), soft preferences, and available resources.
4. **Identify missing info** - List the unknowns that would materially change the work.
5. **Audience objective model** - Model the reader before writing a word: who they are, what they already know, what they will DO after reading, and under what attention budget.
6. **Constraint ledger** - Compile the writing constraint ledger: length ceiling, register/voice, must-include facts, must-not-say items (confidentiality, legal, publication-hygiene boundaries), house style, format requirements.
7. **Structural alternatives** - Per divergent-ideation applied to form: generate 3-5 genuinely different structures BEFORE drafting — inverted pyramid, narrative arc, problem/solution, FAQ, comparison table, letter — different skeletons, not one outline with renamed headings.
8. **Select structure** - Choose the structure by one criterion above all: which gets the reader to reader_action fastest with the least attention spent (structured-reasoning: name the frame — this is a tradeoff between completeness and speed-to-action, and the reader's priority order beats the order you thought of things in).
9. **Draft divergence** - Draft 2-3 versions with judgment OFF (divergent-ideation's divergence phase, applied to prose): vary the opening move, the voice temperature, and what gets compressed vs dwelt on.
10. **Critic passes** - Switch from author to attacker (adversarial-verify, for prose). Run distinct passes, in order, per ruthless-editor: (1) STRUCTURE — lede first, one point per paragraph, kill the on-ramp ('In today's fast-moving landscape...'); (2) ARGUMENT — does the text establish what it claims, and does the opening promise only what the body delivers; (3) ACCURACY — check every factual claim against the ledger and recompute numbers independently; (4) STYLE — register, voice, passive constructions, hedge stacks.
11. **Compression pass** - Per ruthless-editor's cut-and-strengthen passes: delete repetition, filler ('it's worth noting that', 'in order to'), hedge stacks (pick one hedge or none), and scaffolding sentences that only announce other sentences.
12. **Independent final verification** - Verify the FINAL artifact, not the plan: execute every bound check method from determine_verifiables against the refined solution.
13. **Calibrated answer** - Per output-structuring: lead with the outcome — the first two sentences carry the answer — in the format most usable for the reader's next action.

## Conditional moves
- When argument-pass failure: substance wrong, not style: return to **Draft divergence** and rework from there.
- When compression altered meaning or dropped a ledger item: return to **Critic passes** and rework from there.
- When final check found an unverified factual claim: return to **Critic passes** and rework from there.

## Output contract
A finished piece that opens with its point, fits the constraint ledger exactly (length, voice, must-include, must-not-say), carries evidence-level labels on factual claims, plus the critique log and the structural alternatives considered.

## Delivery notes (small-model packets)
If delegating steps to a smaller model, follow the small-model packet rules: one bounded objective per packet, all inputs named explicitly, facts separated from instructions, uncertainty marked 'UNCERTAIN: ...' rather than invented away.

## Before answering
Check the draft against references/failure-checks.md (the failure-mode catalog) and references/verification.md (domain verification criteria). Repair procedures live in references/contracts.md.
