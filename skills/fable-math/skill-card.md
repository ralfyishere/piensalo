# Skill card: fable-math

## What it does
Produces proved-or-refuted quantitative results with independent derivations and explicit proved-vs-computed labeling: formal restatement, honest small cases, two genuinely different derivation routes, boundary probes, dimensional analysis, counterexample search. A code or CAS tool for brute-force checks and numeric verification is recommended, not required. Fully local: reads only its own bundled files and the user's task, sends nothing anywhere.

## Trigger
'prove', 'compute', 'closed form', 'what are the odds', 'derive'.

## Counterindications
- Trivial arithmetic with one obvious route and an instantly checkable answer - two independent derivations are ceremony there.
- Tasks where no calculation tool is available AND hand arithmetic is impractical - the numeric-check steps degrade to unverified claims.
- Purely conceptual math questions ("what is a group?") with no quantity to derive.

## Negative-transfer risk
- Larger prompts can harm already-strong models: the extra scaffolding competes with the derivation itself for attention.
- The independent-derivation requirement can be gamed by paraphrased rather than genuinely different routes - agreement between paraphrases replicates the same error and manufactures false confidence.
- On simple problems the full output contract (symbol tables, agreement matrix) buries a one-line answer.

## Evidence level
DESIGNED - see BENCHMARK.md. The micro-skills this domain skill composes carry their own evidence levels; the composed skill has not been executed as a packaged unit.
