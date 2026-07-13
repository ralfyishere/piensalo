"""Paired full-context vs optimized-context evaluation (evidence command).

Runs the SAME task, target model, settings, contract, and deterministic
grader against (A) the full context and (B) the optimized context at each
requested budget, then compares requirement-by-requirement:

- MAINTAINED: optimized passes every deterministic requirement the full
  response passed;
- IMPROVED: optimized passes a requirement the full response failed,
  without introducing any regression;
- REGRESSION: full passes a requirement the accepted optimized response
  fails (one critical regression is never averaged away);
- SAFE FALLBACK: optimization refused or verification never accepted an
  optimized response — the fallback path is the outcome.

The full-context baseline exists ONLY for evidence and calibration; its
cost is ledgered separately as benchmark cost, never counted as
deployable runtime cost.
"""
from __future__ import annotations

from pathlib import Path

from piensalo.context import quality, runtime, schema
from piensalo.context.ingest import load_context_file
from piensalo.context.tokens import estimate_tokens
from piensalo.verify import contract as contract_mod


def evaluate(*, task_text: str, items, budgets: list[int], adapter,
             contract: dict | None, expectations: dict | None,
             max_expansions: int = runtime.DEFAULT_MAX_EXPANSIONS,
             source_path: str = "context",
             deterministic_settings: dict | None = None) -> dict:
    """Run one paired evaluation; returns the full report dict."""
    source_text = "\n\n".join(i.content for i in items)
    full_prompt = runtime._full_context_prompt(task_text, source_text,
                                               contract)
    full_resp = adapter.complete(full_prompt)
    full_grade = quality.grade(full_resp.text, contract=contract,
                               expectations=expectations)
    baseline = {
        "prompt_tokens_est": estimate_tokens(full_prompt),
        "tokens_in": full_resp.tokens_in,
        "tokens_out": full_resp.tokens_out,
        "requested_model": full_resp.requested_model,
        "resolved_model": full_resp.resolved_model,
        "wall_seconds": round(full_resp.wall_seconds, 2),
        "grade": full_grade,
        "note": "benchmark-only baseline; not part of deployable runtime cost",
    }

    budget_results = []
    for budget in budgets:
        run = runtime.run_optimized(
            task_text=task_text, items=items, budget=budget,
            adapter=adapter, contract=contract, expectations=expectations,
            max_expansions=max_expansions, fallback="recommend",
            source_path=source_path)
        accepted = run.outcome == "OPTIMIZED CONTEXT ACCEPTED"
        opt_grade = run.attempts[-1].grade if run.attempts else {
            "passed": None, "status": "UNMEASURED", "requirements": []}
        verdict = quality.compare_verdict(full_grade, opt_grade,
                                          optimized_accepted=accepted)
        optimized_in = sum(a.tokens_in for a in run.attempts)
        opt_prompt_sum = sum(a.prompt_tokens_est for a in run.attempts)
        budget_results.append({
            "budget": budget,
            "outcome": run.outcome,
            "verdict": verdict,
            "optimized_grade": opt_grade,
            "expansions": run.ledger["expansions"],
            "fallback": run.ledger["fallback"],
            "gross_context_reduction": run.ledger["gross_context_reduction"],
            "optimized_context_tokens_est":
                run.ledger["optimized_context_tokens_est"],
            "source_context_tokens_est":
                run.ledger["source_context_tokens_est"],
            "optimized_prompt_tokens_est_total": opt_prompt_sum,
            "model_tokens_in_billed": optimized_in,
            "model_tokens_out": sum(a.tokens_out for a in run.attempts),
            "runtime_net_input_savings_est": (
                None if not run.attempts else round(
                    1.0 - opt_prompt_sum
                    / max(1, baseline["prompt_tokens_est"]), 4)),
            "savings_note": (
                "prompt-token estimate: what PIENSALO controls. Billed "
                "adapter totals include constant harness overhead (e.g. "
                "claude CLI system prompt) identical in both arms; see "
                "model_tokens_in_billed vs baseline tokens_in."),
            "attempts": run.provenance["attempts"],
            "response_hash": (schema.sha256_text(run.response_text)
                              if run.response_text else None),
            "response_text": run.response_text,
        })

    return {
        "task": task_text.strip(),
        "source_context_hash": schema.sha256_text(source_text),
        "target_requested_model": full_resp.requested_model,
        "target_resolved_model": full_resp.resolved_model,
        "deterministic_settings": deterministic_settings or {
            "note": "adapter exposes no temperature/seed control; "
                    "single-sample comparison, recorded as such"},
        "grader": "deterministic contract + oracle (identical for both arms)",
        "baseline_full_context": baseline,
        "full_response_text": full_resp.text,
        "budgets": budget_results,
    }


def evaluate_to_dir(*, task_path: str, context_path: str, budgets: list[int],
                    adapter, contract_path: str | None,
                    expectations_path: str | None, output_dir: str,
                    max_expansions: int = runtime.DEFAULT_MAX_EXPANSIONS) -> dict:
    task_text = Path(task_path).read_text(encoding="utf-8")
    items = load_context_file(context_path)
    contract = contract_mod.load_task_contract(contract_path) \
        if contract_path else None
    expectations = quality.load_expectations(expectations_path) \
        if expectations_path else None
    report = evaluate(task_text=task_text, items=items, budgets=budgets,
                      adapter=adapter, contract=contract,
                      expectations=expectations,
                      max_expansions=max_expansions,
                      source_path=context_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "evaluation.json").write_text(schema.canonical_json(report),
                                         encoding="utf-8")
    (out / "full-response.md").write_text(report["full_response_text"],
                                          encoding="utf-8")
    for b in report["budgets"]:
        if b["response_text"] is not None:
            (out / f"optimized-response-{b['budget']}.md").write_text(
                b["response_text"], encoding="utf-8")
    return report
