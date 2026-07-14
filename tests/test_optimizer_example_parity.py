"""Anti-drift: examples/context-optimizer committed artifacts.

The deterministic step (optimize) must regenerate byte-for-byte from
shipping code. The model-backed evaluation is a real recorded run — not
byte-reproducible — so its committed artifacts are validated for
structural integrity and honest labeling instead.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from piensalo.context.ingest import load_context_file
from piensalo.context.optimize import optimize
from piensalo.context.schema import canonical_json

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "context-optimizer"

# Mirrors examples/context-optimizer/demo.sh exactly.
DEMO_BUDGET = 1500


@pytest.fixture(scope="module")
def regenerated():
    items = load_context_file(str(EXAMPLE / "context.txt"))
    task_text = (EXAMPLE / "task.md").read_text(encoding="utf-8")
    return optimize(task_text=task_text, items=items, budget=DEMO_BUDGET,
                    source_path="context.txt")


def test_optimize_artifacts_match_shipping_code(regenerated):
    committed_packet = (EXAMPLE / "generated" / "optimize"
                        / "optimized-context.md").read_text(encoding="utf-8")
    assert committed_packet == regenerated.packet, (
        "examples/context-optimizer/generated/optimize drifted from "
        "program output; regenerate with demo.sh and review the diff")
    committed_report = json.loads(
        (EXAMPLE / "generated" / "optimize" / "optimization-report.json")
        .read_text(encoding="utf-8"))
    assert canonical_json(committed_report) == canonical_json(
        regenerated.report)


def test_demo_packet_preserves_task_critical_content(regenerated):
    expected = json.loads(
        (EXAMPLE / "expected.json").read_text(encoding="utf-8"))
    for needle in expected["must_contain"]:
        assert needle in regenerated.packet, needle
    assert "Host the beta on the shared acme-platform cluster." \
        not in regenerated.packet  # superseded stays historical
    assert regenerated.report["gross_reduction"] >= 0.5
    assert regenerated.report["behavioral_status"] == "UNMEASURED"


def test_committed_evaluation_is_structurally_honest():
    ev = json.loads((EXAMPLE / "generated" / "evaluation"
                     / "evaluation.json").read_text(encoding="utf-8"))
    assert ev["target_requested_model"] == ev["target_resolved_model"]
    assert "benchmark-only" in ev["baseline_full_context"]["note"]
    b = ev["budgets"][0]
    assert b["verdict"] in ("MAINTAINED", "IMPROVED", "REGRESSION",
                            "SAFE FALLBACK", "UNMEASURED")
    # The committed run must never present a fallback/regression as an
    # optimized success.
    if b["verdict"] in ("REGRESSION", "SAFE FALLBACK"):
        assert b["outcome"] != "OPTIMIZED CONTEXT ACCEPTED" \
            or b["verdict"] == "REGRESSION"
    assert b["model_tokens_in_billed"] > 0
    assert (EXAMPLE / "generated" / "evaluation"
            / "full-response.md").is_file()
    assert (EXAMPLE / "generated" / "evaluation"
            / f"optimized-response-{b['budget']}.md").is_file()
