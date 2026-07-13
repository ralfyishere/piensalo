"""Optimizer runtime: bounded expansion, safe fallback, ledger, provenance.

Uses a scripted fake adapter — no network, no provider, no real model.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from piensalo.adapters.base import ModelResponse
from piensalo.context import runtime
from piensalo.context.evaluate import evaluate
from piensalo.context.ingest import load_context_text

CONTEXT = """\
OBJECTIVE: Ship the beta.
CONSTRAINT [EXACT]: Deploy only with `make deploy ENV=staging TAG=beta`.
ARTIFACT: commit 4f2a9c1e7b3d5a20
STOP CONDITION: Stop on two consecutive failures.

Chatter about the summer offsite venue that helps nobody fix anything.

The secret rollout window is Tuesday 02:00 UTC according to the platform
calendar, agreed with SRE.

NEXT ACTION: Prepare the rollout.
"""

TASK = "State the rollout window and the commit. Fields: WINDOW and COMMIT."

EXPECT = {"must_contain": ["4f2a9c1e7b3d5a20"],
          "field_values": {"WINDOW": "Tuesday 02:00 UTC"}}

GOOD = "WINDOW: Tuesday 02:00 UTC\nCOMMIT: 4f2a9c1e7b3d5a20\n"
BAD = "WINDOW: unknown\nCOMMIT: 4f2a9c1e7b3d5a20\n"


class FakeAdapter:
    """Scripted adapter: returns queued texts, records prompts."""
    provider = "fake"

    def __init__(self, scripts: list[str], model: str = "fake-model-1"):
        self.scripts = list(scripts)
        self.requested_model = model
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> ModelResponse:
        self.prompts.append(prompt)
        text = self.scripts.pop(0)
        return ModelResponse(
            text=text, requested_model=self.requested_model,
            resolved_model=self.requested_model, provider=self.provider,
            tokens_in=max(1, len(prompt) // 4),
            tokens_out=max(1, len(text) // 4), wall_seconds=0.01)


def _items(text=CONTEXT):
    return load_context_text(text)


def _run(adapter, *, budget=1000, expectations=EXPECT, fallback="recommend",
         max_expansions=2, task=TASK):
    return runtime.run_optimized(
        task_text=task, items=_items(), budget=budget, adapter=adapter,
        expectations=expectations, max_expansions=max_expansions,
        fallback=fallback)


def test_accepts_when_verification_passes_first_try():
    adapter = FakeAdapter([GOOD])
    result = _run(adapter)
    assert result.outcome == "OPTIMIZED CONTEXT ACCEPTED"
    assert result.verification["status"] == "DETERMINISTIC TASK VERIFIED"
    assert [a.label for a in result.attempts] == ["optimized"]
    assert result.attempts[0].requested_model == "fake-model-1"
    assert result.attempts[0].resolved_model == "fake-model-1"


def test_bounded_expansion_recovers_omitted_fact():
    """The rollout window lives in a low-relevance chunk for a terse task;
    round 1 fails, expansion adds chunks, round 2 succeeds."""
    adapter = FakeAdapter([BAD, GOOD])
    result = _run(adapter)
    assert result.outcome == "OPTIMIZED CONTEXT ACCEPTED"
    labels = [a.label for a in result.attempts]
    assert labels == ["optimized", "expansion-1"]
    assert result.attempts[1].added_chunk_ids, "expansion must record chunks"
    assert result.ledger["expansions"] == 1
    # The expanded packet actually grew.
    assert len(adapter.prompts[1]) > len(adapter.prompts[0])


def test_expansion_limit_is_bounded_then_safe_fallback_recommended():
    adapter = FakeAdapter([BAD, BAD, BAD])
    result = _run(adapter, max_expansions=2)
    assert result.outcome == "SAFE FALLBACK (RECOMMENDED)"
    assert result.response_text is None  # never a silent failed success
    assert len(result.attempts) <= 3
    assert result.ledger["fallback"] is True


def test_full_context_fallback_executes_when_configured():
    # Optimized attempts fail; the full-context call succeeds.
    class SwitchingAdapter(FakeAdapter):
        def complete(self, prompt):
            self.scripts = [GOOD] if "# Full context" in prompt else [BAD]
            return super().complete(prompt)

    adapter = SwitchingAdapter([])
    result = _run(adapter, fallback="run", max_expansions=1)
    assert result.outcome == "SAFE FALLBACK (EXECUTED)"
    assert result.response_text == GOOD
    assert result.attempts[-1].label == "fallback-full"
    assert result.ledger["fallback_tokens"] > 0
    # A fallback is never counted as an optimized acceptance.
    assert result.outcome != "OPTIMIZED CONTEXT ACCEPTED"


def test_refusal_path_requires_expansion_or_full_context():
    adapter = FakeAdapter([GOOD])
    result = _run(adapter, budget=40)
    assert result.outcome == "OPTIMIZATION REJECTED — FULL CONTEXT REQUIRED"
    assert result.response_text is None
    assert adapter.prompts == []  # no model call happened


def test_unmeasured_acceptance_without_any_grader():
    adapter = FakeAdapter(["anything at all"])
    result = _run(adapter, expectations=None)
    assert result.outcome == "OPTIMIZED CONTEXT ACCEPTED"
    assert result.verification["behavioral_status"] == "UNMEASURED"
    assert result.verification["status"] == "UNMEASURED"


def test_token_ledger_completeness_and_separation():
    adapter = FakeAdapter([BAD, GOOD])
    ledger = _run(adapter).ledger
    for key in ("source_context_tokens_est", "optimized_context_tokens_est",
                "model_input_tokens", "model_output_tokens",
                "extraction_model_tokens", "verification_model_tokens",
                "expansion_tokens", "fallback_tokens",
                "benchmark_baseline_tokens", "gross_context_reduction",
                "runtime_token_cost", "runtime_net_savings_vs_full_est",
                "expansions", "fallback", "latency_seconds"):
        assert key in ledger, key
    assert ledger["benchmark_baseline_tokens"] is None  # runtime, not eval
    assert ledger["expansion_tokens"] > 0
    assert ledger["verification_model_tokens"] == 0


def test_runtime_never_runs_a_baseline():
    adapter = FakeAdapter([GOOD])
    _run(adapter)
    assert all("# Full context" not in p for p in adapter.prompts)


def test_run_requires_explicit_adapter():
    with pytest.raises(ValueError, match="called silently"):
        runtime.run_optimized(task_text=TASK, items=_items(), budget=1000,
                              adapter=None, expectations=EXPECT)


def test_run_to_dir_writes_all_artifacts(project_root):
    (project_root / "task.md").write_text(TASK, encoding="utf-8")
    (project_root / "ctx.txt").write_text(CONTEXT, encoding="utf-8")
    result = runtime.run_to_dir(
        task_path=str(project_root / "task.md"),
        context_path=str(project_root / "ctx.txt"), artifact_paths=[],
        budget=1000, adapter=FakeAdapter([GOOD]), contract_path=None,
        expectations_path=None, max_expansions=2, fallback="recommend",
        output_dir=str(project_root / "run"))
    for name in ("optimized-context.md", "response.md",
                 "selection-manifest.json", "verification.json",
                 "provenance.json", "token-ledger.json"):
        assert (project_root / "run" / name).is_file(), name
    prov = (project_root / "run" / "provenance.json").read_text("utf-8")
    assert '"requested_model": "fake-model-1"' in prov
    assert '"resolved_model": "fake-model-1"' in prov
    assert result.outcome == "OPTIMIZED CONTEXT ACCEPTED"


def test_deterministic_core_never_imports_adapters_or_network():
    """optimize (deterministic mode) in a clean interpreter must not load
    provider, adapter, or network modules."""
    # 'socket' is deliberately absent: importlib.metadata (the version
    # lookup in piensalo/__init__) imports email -> socket as a stdlib
    # side effect with no connection. Actual network use is blocked and
    # asserted by test_full_pipeline_with_no_credentials_and_no_network.
    code = (
        "import sys\n"
        "PREFIXES = ('piensalo.adapters', 'anthropic', 'openai', 'requests',"
        " 'httpx', 'urllib.request')\n"
        "sys.path.insert(0, 'src')\n"
        "from piensalo.context.ingest import load_context_text\n"
        "from piensalo.context.optimize import optimize\n"
        "items = load_context_text('DECISION: x.\\nNEXT ACTION: go.\\n')\n"
        "optimize(task_text='do x', items=items, budget=500)\n"
        "loaded = [m for m in sys.modules if m.startswith(PREFIXES)]\n"
        "assert not loaded, loaded\n"
        "print('CLEAN')\n"
    )
    proc = subprocess.run([sys.executable, "-c", code],
                          capture_output=True, text=True,
                          cwd=str(Path(__file__).resolve().parent.parent))
    assert proc.returncode == 0, proc.stderr
    assert "CLEAN" in proc.stdout


# ------------------------------------------------------------- evaluate
LONG_CONTEXT = CONTEXT + "\n" + "\n\n".join(
    f"Digression {i}: a very long unrelated anecdote about the office plants "
    "and who waters them on alternating weeks, which never affects any "
    "engineering decision at all." for i in range(40))


def test_evaluate_pairs_full_and_optimized_with_benchmark_separation():
    adapter = FakeAdapter([GOOD, GOOD])  # baseline, then optimized
    report = evaluate(task_text=TASK, items=_items(LONG_CONTEXT),
                      budgets=[1000], adapter=adapter, contract=None,
                      expectations=EXPECT)
    assert report["baseline_full_context"]["grade"]["passed"] is True
    assert "benchmark-only" in report["baseline_full_context"]["note"]
    b = report["budgets"][0]
    assert b["verdict"] == "MAINTAINED"
    assert b["outcome"] == "OPTIMIZED CONTEXT ACCEPTED"
    # Benchmark tokens never leak into the optimized arm's cost.
    baseline_prompt = report["baseline_full_context"]["prompt_tokens_est"]
    assert b["optimized_prompt_tokens_est_total"] < baseline_prompt
    assert b["runtime_net_input_savings_est"] > 0
    assert "billed" in b["savings_note"]
    assert report["target_resolved_model"] == "fake-model-1"


def test_evaluate_safe_fallback_verdict_when_optimized_never_passes():
    adapter = FakeAdapter([GOOD, BAD, BAD, BAD])
    report = evaluate(task_text=TASK, items=_items(), budgets=[1000],
                      adapter=adapter, contract=None, expectations=EXPECT)
    assert report["budgets"][0]["verdict"] == "SAFE FALLBACK"
    assert report["budgets"][0]["fallback"] is True
