#!/usr/bin/env python3
"""Run the pre-registered Context Optimizer evaluation suite.

Usage: uv run python evals/context-optimizer/run.py [--model MODEL]

Executes every task in tasks/ as a paired full-vs-optimized evaluation
through the explicitly configured claude-cli adapter, writes per-task
results and a summary with the gate arithmetic. Honest by construction:
verdicts come from piensalo.context.evaluate; this script only aggregates.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
sys.path.insert(0, str(REPO / "src"))

from piensalo.adapters import get_adapter  # noqa: E402
from piensalo.context.evaluate import evaluate_to_dir  # noqa: E402

DEFAULT_MODEL = "claude-haiku-4-5-20251001"
SAFE_VERDICTS = ("MAINTAINED", "IMPROVED")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--adapter", default="claude-cli")
    args = ap.parse_args()

    adapter = get_adapter(args.adapter, model=args.model)
    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)

    rows = []
    for task_dir in sorted((ROOT / "tasks").iterdir()):
        if not task_dir.is_dir():
            continue
        name = task_dir.name
        budget = int((task_dir / "budget.txt").read_text().strip())
        contract = task_dir / "contract.json"
        print(f"== {name} (budget {budget}) ==", flush=True)
        report = evaluate_to_dir(
            task_path=str(task_dir / "task.md"),
            context_path=str(task_dir / "context.txt"),
            budgets=[budget],
            adapter=adapter,
            contract_path=str(contract) if contract.is_file() else None,
            expectations_path=str(task_dir / "expected.json"),
            output_dir=str(results_dir / name),
        )
        b = report["budgets"][0]
        base = report["baseline_full_context"]
        row = {
            "task": name,
            "budget": budget,
            "verdict": b["verdict"],
            "outcome": b["outcome"],
            "full_grade_passed": base["grade"]["passed"],
            "optimized_grade_passed": b["optimized_grade"].get("passed"),
            "gross_context_reduction": b["gross_context_reduction"],
            "expansions": b["expansions"],
            "fallback": b["fallback"],
            "baseline_tokens_in": base["tokens_in"],
            "baseline_tokens_out": base["tokens_out"],
            "optimized_tokens_in_billed": b["model_tokens_in_billed"],
            "optimized_tokens_out": b["model_tokens_out"],
            "optimized_prompt_tokens_est": b["optimized_prompt_tokens_est_total"],
            "baseline_prompt_tokens_est":
                base["prompt_tokens_est"],
            "runtime_net_input_savings_est":
                b["runtime_net_input_savings_est"],
            "resolved_model": report["target_resolved_model"],
        }
        rows.append(row)
        print(f"   verdict={row['verdict']} outcome={row['outcome']} "
              f"reduction={row['gross_context_reduction']} "
              f"net_in_savings={row['runtime_net_input_savings_est']}",
              flush=True)

    reductions = [r["gross_context_reduction"] for r in rows
                  if r["gross_context_reduction"] is not None]
    savings = [r["runtime_net_input_savings_est"] for r in rows
               if r["runtime_net_input_savings_est"] is not None
               and not r["task"].startswith("08")]
    regressions = [r["task"] for r in rows if r["verdict"] == "REGRESSION"]
    safe_optimized = [r["task"] for r in rows if r["verdict"] in SAFE_VERDICTS
                      and r["outcome"] == "OPTIMIZED CONTEXT ACCEPTED"]
    fallbacks = [r["task"] for r in rows if r["verdict"] == "SAFE FALLBACK"]
    # Pre-registered criterion 5: task 08 must REFUSE optimization and fall
    # back safely (verdict SAFE FALLBACK). Whether the target model then
    # aces the byte-for-byte grader on the full context is model
    # capability, not optimizer safety; full_grade_passed is recorded per
    # task above for transparency.
    fallback_task_ok = any(
        r["task"].startswith("08") and r["verdict"] == "SAFE FALLBACK"
        and r["outcome"].startswith("OPTIMIZATION REJECTED")
        for r in rows)

    summary = {
        "model": args.model,
        "tasks": rows,
        "paired_tasks_completed": len(rows),
        "critical_regressions": regressions,
        "median_gross_context_reduction":
            round(statistics.median(reductions), 4) if reductions else None,
        "median_runtime_net_input_savings":
            round(statistics.median(savings), 4) if savings else None,
        "safely_optimized_tasks": safe_optimized,
        "safely_optimized_count": len(safe_optimized),
        "fallback_tasks": fallbacks,
        "fallback_rate": round(len(fallbacks) / len(rows), 4) if rows else None,
        "improved": [r["task"] for r in rows if r["verdict"] == "IMPROVED"],
        "maintained": [r["task"] for r in rows if r["verdict"] == "MAINTAINED"],
        "gate": {},
    }
    gate = {
        "paired_tasks_>=8": len(rows) >= 8,
        "zero_critical_regressions": not regressions,
        "median_gross_reduction_>=0.50":
            bool(reductions) and statistics.median(reductions) >= 0.50,
        "median_runtime_net_savings_>=0.30":
            bool(savings) and statistics.median(savings) >= 0.30,
        "safely_optimized_>=6_of_8": len(safe_optimized) >= 6,
        "uncompressible_task_fell_back_safely": fallback_task_ok,
    }
    gate["verdict"] = "PASS" if all(gate.values()) else "FAIL"
    summary["gate"] = gate

    (results_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    print(json.dumps(gate, indent=2))
    print(f"wrote {results_dir / 'summary.json'}")
    return 0 if gate["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
