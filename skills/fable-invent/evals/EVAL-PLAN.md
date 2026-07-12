# Eval plan: fable-invent

Status: stub. No eval has been run against the packaged skill (see BENCHMARK.md — current status DESIGNED).

## Conditions
- **skill-on:** the model runs the task with fable-invent loaded.
- **no-skill baseline:** the same model runs the same task with no skill loaded.
- Same model, same tasks, same tool access in both conditions; outputs graded blind to condition.

## Grader
Behavior-signal rubric scored by an LLM judge, plus deterministic checks where a signal is mechanically checkable (e.g. "quantitative requirements stated before candidates", "prior-art section present with recorded queries"). No grader keys ship with the skill.

## Task classes
1. **Constrained physical mechanism design** — e.g. "Design a mechanism that waters a houseplant for 30 days unattended, no electricity, under $20 in parts."
   Signals: extracts quantitative requirements (flow rate, reservoir volume) before ideating; checks prior art and does not claim novelty for standard mechanisms; candidates differ in operating principle; kills candidates with numbers, not vibes; fail-safe behavior analyzed.
2. **Novel algorithm/protocol proposal with honest positioning** — e.g. "Propose a novel way to deduplicate near-identical support tickets in real time, and honestly position it against existing approaches."
   Signals: prior-art positioning is explicit and specific; feasibility attacked with concrete resource estimates; novelty claims are scoped to what actually differs.
