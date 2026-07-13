"""Deployable optimizer runtime: optimize -> run -> verify -> accept,
expand, or fall back.

Rules enforced here:
- a model is called ONLY through the explicitly configured adapter;
- requested and resolved model are recorded for every call;
- verification failure triggers bounded expansion (default 2 rounds),
  adding the highest-value omitted chunks, every addition recorded;
- after the expansion limit, the runtime runs or recommends the
  full-context fallback per operator configuration — a fallback is a
  SAFE FALLBACK outcome, never an optimized success;
- a failed optimized response is NEVER silently returned as success;
- the runtime never runs a full-context baseline just to serve one
  request (that is ``evaluate``'s job, ledgered as benchmark cost).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from piensalo.context import optimize as optimize_mod
from piensalo.context import quality, schema, select
from piensalo.context.tokens import ESTIMATOR, estimate_tokens
from piensalo.verify import contract as contract_mod

DEFAULT_MAX_EXPANSIONS = 2
_EXPANSION_BUDGET_FRACTION = 0.25   # extra tokens allowed per round

OUTCOMES = ("OPTIMIZED CONTEXT ACCEPTED",
            "SAFE FALLBACK (EXECUTED)",
            "SAFE FALLBACK (RECOMMENDED)",
            "OPTIMIZATION REJECTED — FULL CONTEXT REQUIRED")


@dataclass
class Attempt:
    label: str                    # optimized | expansion-1 | ... | fallback-full
    prompt_tokens_est: int
    added_chunk_ids: list[str]
    requested_model: str = ""
    resolved_model: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    wall_seconds: float = 0.0
    grade: dict = field(default_factory=dict)


@dataclass
class RunResult:
    outcome: str
    response_text: str | None
    attempts: list[Attempt]
    ledger: dict
    verification: dict
    provenance: dict
    selection: object = None      # the (possibly expanded) Selection
    packet: str = ""              # the final packet actually sent


def _envelope(packet: str, contract: dict | None) -> str:
    """Neutral prompt: the packet plus the task's own output contract.
    No provider-specific tricks belong here."""
    if not contract:
        return packet
    return packet + "\n" + contract_mod.emit(contract) + "\n"


def _full_context_prompt(task_text: str, source_text: str,
                         contract: dict | None) -> str:
    body = (f"# Task\n\n{task_text.strip()}\n\n# Full context\n\n"
            f"{source_text}\n")
    return _envelope(body, contract)


def run_optimized(*, task_text: str, items, budget: int, adapter,
                  contract: dict | None = None,
                  expectations: dict | None = None,
                  max_expansions: int = DEFAULT_MAX_EXPANSIONS,
                  fallback: str = "recommend",
                  source_path: str = "context",
                  mode: str = "deterministic",
                  extraction_adapter=None) -> RunResult:
    """Execute the full lifecycle against normalized context items."""
    if fallback not in ("run", "recommend"):
        raise ValueError(f"fallback must be run|recommend, got {fallback!r}")
    source_text = "\n\n".join(i.content for i in items)
    source_tokens = estimate_tokens(source_text)
    opt = optimize_mod.optimize(
        task_text=task_text, items=items, budget=budget,
        source_path=source_path, mode=mode,
        extraction_adapter=extraction_adapter)

    attempts: list[Attempt] = []
    started = datetime.now(timezone.utc).isoformat()

    def _ledger(outcome: str, fallback_tokens: int = 0) -> dict:
        model_in = sum(a.tokens_in for a in attempts)
        model_out = sum(a.tokens_out for a in attempts)
        expansion_in = sum(a.tokens_in for a in attempts
                           if a.label.startswith("expansion"))
        full_prompt_est = estimate_tokens(
            _full_context_prompt(task_text, source_text, contract))
        runtime_cost = model_in + model_out
        return {
            "token_estimator": ESTIMATOR,
            "source_context_tokens_est": source_tokens,
            "optimized_context_tokens_est":
                opt.report["optimized_context_tokens"],
            "model_input_tokens": model_in,
            "model_output_tokens": model_out,
            "extraction_model_tokens": 0 if mode == "deterministic" else
                "reported by extraction adapter provenance",
            "verification_model_tokens": 0,
            "expansion_tokens": expansion_in,
            "fallback_tokens": fallback_tokens,
            "benchmark_baseline_tokens": None,
            "gross_context_reduction": opt.report["gross_reduction"],
            "runtime_token_cost": runtime_cost,
            "full_context_prompt_tokens_est": full_prompt_est,
            "runtime_net_savings_vs_full_est": (
                None if not attempts else round(
                    1.0 - (sum(a.prompt_tokens_est for a in attempts)
                           / max(1, full_prompt_est)), 4)),
            "runtime_net_savings_note": (
                "estimate: prompt tokens actually sent (all attempts, incl. "
                "expansions/fallback) vs the full-context prompt this "
                "request would have sent. Adapter-billed totals are in "
                "model_input_tokens and may include constant harness "
                "overhead (e.g. the claude CLI system prompt) identical in "
                "either path. No baseline was executed for this request."),
            "expansions": sum(1 for a in attempts
                              if a.label.startswith("expansion")),
            "fallback": outcome.startswith("SAFE FALLBACK"),
            "latency_seconds": round(sum(a.wall_seconds for a in attempts), 2),
        }

    def _provenance(outcome: str) -> dict:
        return {
            "started_at": started,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "adapter": getattr(adapter, "provider", None) if adapter else None,
            "outcome": outcome,
            "task_hash": schema.sha256_text(task_text),
            "source_context_hash": schema.sha256_text(source_text),
            "attempts": [{
                "label": a.label,
                "requested_model": a.requested_model,
                "resolved_model": a.resolved_model,
                "prompt_tokens_est": a.prompt_tokens_est,
                "tokens_in": a.tokens_in, "tokens_out": a.tokens_out,
                "wall_seconds": round(a.wall_seconds, 2),
                "added_chunk_ids": a.added_chunk_ids,
                "grade_status": a.grade.get("status"),
                "grade_passed": a.grade.get("passed"),
            } for a in attempts],
        }

    if opt.refused:
        outcome = "OPTIMIZATION REJECTED — FULL CONTEXT REQUIRED"
        verification = {
            "status": "UNMEASURED",
            "outcome": outcome,
            "detail": opt.selection.refusal_reason,
            "behavioral_status": "UNMEASURED",
        }
        if fallback == "run" and adapter is not None:
            resp = adapter.complete(
                _full_context_prompt(task_text, source_text, contract))
            g = quality.grade(resp.text, contract=contract,
                              expectations=expectations)
            attempts.append(Attempt(
                label="fallback-full",
                prompt_tokens_est=estimate_tokens(
                    _full_context_prompt(task_text, source_text, contract)),
                added_chunk_ids=[], requested_model=resp.requested_model,
                resolved_model=resp.resolved_model, tokens_in=resp.tokens_in,
                tokens_out=resp.tokens_out, wall_seconds=resp.wall_seconds,
                grade=g))
            outcome = "SAFE FALLBACK (EXECUTED)"
            verification = {"status": g["status"], "outcome": outcome,
                            "grade": g, "behavioral_status":
                            "full-context response; optimization refused"}
            return RunResult(outcome, resp.text, attempts,
                             _ledger(outcome,
                                     fallback_tokens=attempts[-1].tokens_in),
                             verification, _provenance(outcome),
                             selection=opt.selection, packet="")
        return RunResult(outcome, None, attempts, _ledger(outcome),
                         verification, _provenance(outcome),
                         selection=opt.selection, packet="")

    if adapter is None:
        raise ValueError("context run requires an explicitly configured "
                         "adapter — no model is ever called silently")

    extra_ids: list[str] = []
    added_by_round: dict[int, list[str]] = {}
    queue = list(opt.selection.expansion_queue)
    by_id = {c.id: c for c in opt.selection.chunks}
    packet = opt.packet
    for round_no in range(max_expansions + 1):
        label = "optimized" if round_no == 0 else f"expansion-{round_no}"
        prompt = _envelope(packet, contract)
        resp = adapter.complete(prompt)
        g = quality.grade(resp.text, contract=contract,
                          expectations=expectations)
        attempts.append(Attempt(
            label=label, prompt_tokens_est=estimate_tokens(prompt),
            added_chunk_ids=added_by_round.get(round_no, []),
            requested_model=resp.requested_model,
            resolved_model=resp.resolved_model,
            tokens_in=resp.tokens_in, tokens_out=resp.tokens_out,
            wall_seconds=resp.wall_seconds, grade=g))
        if g["passed"] is True or g["passed"] is None:
            # None = no deterministic requirements exist; status stays
            # honest (UNMEASURED) — acceptance here is structural only.
            outcome = "OPTIMIZED CONTEXT ACCEPTED"
            verification = {
                "status": g["status"], "outcome": outcome, "grade": g,
                "expansions_used": round_no,
                "behavioral_status": g["status"] if g["passed"] else
                "UNMEASURED",
            }
            return RunResult(outcome, resp.text, attempts, _ledger(outcome),
                             verification, _provenance(outcome),
                             selection=opt.selection, packet=packet)
        if round_no == max_expansions:
            break
        added_now: list[str] = []
        extra_allowance = int(budget * _EXPANSION_BUDGET_FRACTION)
        while queue and extra_allowance > 0:
            cid = queue.pop(0)
            chunk = by_id[cid]
            added_now.append(cid)
            chunk.disposition = "INCLUDED_RELEVANT"
            chunk.reason += (f" | expanded in round {round_no + 1}: prior "
                             "attempt failed deterministic verification")
            extra_allowance -= chunk.tokens
        if not added_now:
            break  # nothing left to add; expansion cannot help
        extra_ids.extend(added_now)
        added_by_round[round_no + 1] = added_now
        packet = optimize_mod.render_packet(task_text, opt.selection,
                                            extra_chunk_ids=tuple(extra_ids))

    # All optimized attempts failed verification.
    last_grade = attempts[-1].grade
    if fallback == "run":
        resp = adapter.complete(
            _full_context_prompt(task_text, source_text, contract))
        g = quality.grade(resp.text, contract=contract,
                          expectations=expectations)
        attempts.append(Attempt(
            label="fallback-full",
            prompt_tokens_est=estimate_tokens(
                _full_context_prompt(task_text, source_text, contract)),
            added_chunk_ids=[], requested_model=resp.requested_model,
            resolved_model=resp.resolved_model, tokens_in=resp.tokens_in,
            tokens_out=resp.tokens_out, wall_seconds=resp.wall_seconds,
            grade=g))
        outcome = "SAFE FALLBACK (EXECUTED)"
        verification = {
            "status": g["status"], "outcome": outcome, "grade": g,
            "optimized_failure": last_grade,
            "behavioral_status": "full-context fallback response",
        }
        return RunResult(outcome, resp.text, attempts,
                         _ledger(outcome,
                                 fallback_tokens=attempts[-1].tokens_in),
                         verification, _provenance(outcome),
                         selection=opt.selection, packet=packet)
    outcome = "SAFE FALLBACK (RECOMMENDED)"
    verification = {
        "status": "REGRESSION-CANDIDATE", "outcome": outcome,
        "grade": last_grade,
        "detail": "optimized attempts failed deterministic verification "
                  "within the expansion limit; run with --fallback run or "
                  "use the full context directly",
        "behavioral_status": "UNMEASURED",
    }
    return RunResult(outcome, None, attempts, _ledger(outcome),
                     verification, _provenance(outcome),
                     selection=opt.selection, packet=packet)


def run_to_dir(*, task_path: str, context_path: str, artifact_paths: list,
               budget: int, adapter, contract_path: str | None,
               expectations_path: str | None, max_expansions: int,
               fallback: str, output_dir: str,
               mode: str = "deterministic",
               extraction_adapter=None) -> RunResult:
    from piensalo.context.ingest import load_artifacts, load_context_file
    task_text = Path(task_path).read_text(encoding="utf-8")
    items = load_context_file(context_path)
    arts = load_artifacts(artifact_paths or [])
    for a in arts:
        a.index += len(items)
    items = items + arts
    contract = contract_mod.load_task_contract(contract_path) \
        if contract_path else None
    expectations = quality.load_expectations(expectations_path) \
        if expectations_path else None

    result = run_optimized(
        task_text=task_text, items=items, budget=budget, adapter=adapter,
        contract=contract, expectations=expectations,
        max_expansions=max_expansions, fallback=fallback,
        source_path=context_path, mode=mode,
        extraction_adapter=extraction_adapter)

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "optimized-context.md").write_text(
        result.packet or "OPTIMIZATION REFUSED — FULL CONTEXT REQUIRED\n",
        encoding="utf-8")
    (out / "selection-manifest.json").write_text(
        schema.canonical_json(select.manifest(result.selection)),
        encoding="utf-8")
    (out / "response.md").write_text(
        result.response_text if result.response_text is not None
        else f"(no accepted response: {result.outcome})\n",
        encoding="utf-8")
    (out / "verification.json").write_text(
        schema.canonical_json(result.verification), encoding="utf-8")
    (out / "provenance.json").write_text(
        schema.canonical_json(result.provenance), encoding="utf-8")
    (out / "token-ledger.json").write_text(
        schema.canonical_json(result.ledger), encoding="utf-8")
    return result
