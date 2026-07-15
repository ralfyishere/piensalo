#!/bin/sh
# PIENSALO Context Optimizer — 60-second launch demo.
#
# Offline by default: no API key, no model call. Steps labeled LIVE are
# deterministic and reproduced on YOUR machine right now; steps labeled
# RECORDED replay the committed real model run (integrity-checked against
# the current inputs, never presented as live).
#
# Output is deterministic; tests/test_launch_demo_parity.py regenerates it
# and fails if this script and LAUNCH-TRANSCRIPT.md ever diverge.
set -eu
cd "$(dirname "$0")"

if command -v piensalo >/dev/null 2>&1; then PIENSALO="piensalo";
elif command -v uv >/dev/null 2>&1; then PIENSALO="uv run --quiet piensalo";
else PIENSALO="python3 -m piensalo"; fi

OUT=".launch-demo-out"
rm -rf "$OUT"

hr() { printf '%s\n' "----------------------------------------------------------------------"; }
say() { printf '%s\n' "$*"; }

hr
say "PIENSALO CONTEXT OPTIMIZER"
say "Use less context. Lose none of the intelligence."
say "(offline demo: LIVE steps run now, RECORDED steps replay a committed run)"
hr

say ""
say "[1] THE TASK"
say ""
sed 's/^/    /' task.md

say ""
say "[2] THE FULL CONTEXT AVAILABLE TO THE MODEL"
say ""
LINES=$(wc -l < context.txt | tr -d ' ')
CHARS=$(wc -c < context.txt | tr -d ' ')
TOKENS=$(( (CHARS + 3) / 4 ))
say "    context.txt: $LINES lines, ~$TOKENS tokens (chars/4 estimate)"
say "    A real engineering thread: decisions, constraints, exact commands,"
say "    one superseded decision — buried in 26 paragraphs of office chatter."

say ""
say "[3] OPTIMIZE  — LIVE, deterministic, no model call"
say ""
$PIENSALO context optimize \
    --task task.md --context context.txt \
    --budget 1500 --output "$OUT/optimize" | sed 's/^/    /'

say ""
say "[4] WHAT WAS KEPT — AND WHAT WAS LEFT OUT (every chunk has a reason)"
say ""
python3 - <<'EOF'
import json
m = json.load(open(".launch-demo-out/optimize/selection-manifest.json"))
counts = {}
for c in m["chunks"]:
    counts[c["disposition"]] = counts.get(c["disposition"], 0) + 1
for d in sorted(counts):
    print(f"    {d:<24} {counts[d]}")
kept = [c for c in m["chunks"] if c["disposition"] == "INCLUDED_MANDATORY"]
print()
print("    kept unconditionally (mandatory):")
for c in kept[:6]:
    first = c["id"].split("-")[0]
    print(f"      - {first}: {c['reason'].split(':')[0]}")
sup = [c for c in m["chunks"] if c["disposition"] == "OMITTED_SUPERSEDED"]
if sup:
    print("    superseded decision kept as history, never shown as current:")
    print(f"      - {sup[0]['id']} ({sup[0]['record_type']}, "
          f"superseded_by {sup[0]['superseded_by']})")
EOF

say ""
say "[5] SIZE: FULL vs OPTIMIZED"
say ""
python3 - <<'EOF'
import json
r = json.load(open(".launch-demo-out/optimize/optimization-report.json"))
print(f"    original context : {r['original_tokens_est']:>5} tokens (est)")
print(f"    optimized packet : {r['optimized_context_tokens']:>5} tokens (est)")
print(f"    gross reduction  : {r['gross_reduction']:>8.1%}")
print(f"    behavioral status: {r['behavioral_status']} (no model has run)")
EOF

say ""
say "[6] DID THE ANSWER SURVIVE?  — RECORDED committed model run"
say "    (claude-haiku-4-5-20251001 via claude-cli, single sample,"
say "     recorded 2026-07-14; replayed here, NOT generated live)"
say ""
python3 - <<'EOF'
import hashlib, json, sys
ev = json.load(open("generated/evaluation/evaluation.json"))
ctx = open("context.txt", encoding="utf-8").read()
live = hashlib.sha256(ctx.encode()).hexdigest()
if ev["source_context_hash"] != live:
    sys.exit("    INTEGRITY CHECK FAILED: recorded run does not match "
             "the current context.txt — do not trust this replay.")
print("    integrity: recorded run matches current context.txt "
      f"(sha256 {live[:16]}...)")
base, b = ev["baseline_full_context"], ev["budgets"][0]
def passed(g): return sum(1 for r in g["requirements"] if r["passed"])
def total(g): return len(g["requirements"])
bg, og = base["grade"], b["optimized_grade"]
print(f"    full context     -> {passed(bg)}/{total(bg)} deterministic requirements passed")
print(f"    optimized packet -> {passed(og)}/{total(og)} deterministic requirements passed")
print(f"    verdict          : {b['verdict']}")
print(f"    prompt tokens    : {base['prompt_tokens_est']} full -> "
      f"{b['optimized_prompt_tokens_est_total']} optimized "
      f"({b['runtime_net_input_savings_est']:.1%} input savings, est)")
print(f"    expansions: {b['expansions']}   fallback: {b['fallback']}")
EOF

say ""
say "[7] THE UNSAFE CASE  — LIVE: optimization is REFUSED, never truncated"
say ""
say "    40 binding rules, every one mandatory, budget 400 tokens:"
say ""
# Separate the streams: the "wrote ..." progress goes to stdout, the
# refusal verdict to stderr. Merging them through one pipe would let
# buffering reorder the lines, so we suppress stdout and print only the
# deterministic refusal message from stderr.
$PIENSALO context optimize \
    --task ../../evals/context-optimizer/tasks/08-fallback-required/task.md \
    --context ../../evals/context-optimizer/tasks/08-fallback-required/context.txt \
    --budget 400 --output "$OUT/refusal" >/dev/null 2>"$OUT/refusal.err" || true
sed 's/^/    /' "$OUT/refusal.err"
say ""
python3 - <<'EOF'
import json
s = json.load(open("../../evals/context-optimizer/results/summary.json"))
t8 = [t for t in s["tasks"] if t["task"].startswith("08")][0]
print("    RECORDED evaluation outcome for this task: "
      f"{t8['verdict']} ({t8['outcome']})")
EOF

say ""
hr
say "THE PREREGISTERED RESULT (8 paired tasks, committed under"
say "evals/context-optimizer/results/ — one Claude-family model, single"
say "samples, deterministic graders; replication pending):"
say ""
python3 - <<'EOF'
import json
s = json.load(open("../../evals/context-optimizer/results/summary.json"))
print(f"    median context reduction         : {s['median_gross_context_reduction']:.1%}")
print(f"    median runtime net input savings : {s['median_runtime_net_input_savings']:.1%}")
print(f"    optimizable tasks maintained     : {s['safely_optimized_count']}/7")
print(f"    deterministic regressions        : {len(s['critical_regressions'])}")
print(f"    designed unsafe case fell back   : "
      f"{'yes' if s['gate']['uncompressible_task_fell_back_safely'] else 'NO'}")
EOF
say ""
say "Run the model comparison LIVE against your own model:"
say "  piensalo context evaluate --task task.md --context context.txt \\"
say "    --adapter claude-cli --model <model> --contract contract.json \\"
say "    --expected expected.json --budgets 1500 --output my-eval"
hr
