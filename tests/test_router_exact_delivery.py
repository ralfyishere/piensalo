"""EXACT_DELIVERY_CONTRACT router signal (NR-11 guard): full THINK is
suppressed on tasks demanding verbatim output shape."""
from __future__ import annotations

from piensalo.gateway.protocol import ContentBlock, Message, NormalizedRequest
from piensalo.gateway.router import CortexRouter, extract_features


def _req(text: str) -> NormalizedRequest:
    return NormalizedRequest(model="m", messages=[
        Message(role="user", content=[ContentBlock(type="text", text=text)])])


def test_exact_format_task_abstains_from_full_think():
    # Planning words AND an exact-output demand: THINK must be suppressed.
    text = ("Plan the schedule for five jobs step by step. "
            "Output exactly one line per job and nothing else:\n"
            "A: worker=<1|2> start=<h> end=<h>")
    d = CortexRouter().decide(_req(text))
    assert "THINK" not in d.decision
    assert any("EXACT_DELIVERY_CONTRACT" in r for r in d.reasons)


def test_planning_task_without_exact_contract_still_thinks():
    text = ("Plan the migration step by step and decompose the rollout "
            "into phases with dependencies and risks.")
    d = CortexRouter().decide(_req(text))
    assert "THINK" in d.decision


def test_feature_is_inspectable():
    f = extract_features(_req("Return the JSON only, no prose."))
    assert f["exact_delivery_contract"] is True
    assert f["exact_delivery_hits"] >= 1
    f2 = extract_features(_req("Tell me about the sea."))
    assert f2["exact_delivery_contract"] is False


def test_haiku_style_nothing_else_fires_signal():
    f = extract_features(_req(
        "Write a haiku about the sea. Output exactly three lines and "
        "nothing else."))
    assert f["exact_delivery_contract"] is True
