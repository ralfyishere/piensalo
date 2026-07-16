"""Stage 2 — gateway CLI smoke tests (offline, no server run).

Covers argument parsing, the `gateway` read-side commands over a synthetic
ledger, and doctor/status exit codes. `serve` itself blocks, so it is exercised
by the server tests, not here.
"""
from __future__ import annotations

import json

from piensalo.cli.main import main
from piensalo.gateway.ledger import EventLedger, GatewayEvent


def _seed_ledger(dirpath):
    led = EventLedger(dirpath)
    led.append(GatewayEvent(request_id="a1", requested_model="m", router_decision="PASS_THROUGH"))
    led.append(GatewayEvent(request_id="b2", requested_model="m", router_decision="CHECK",
                            router_confidence=0.72, tool_calls=1, streamed=True))
    return led


def test_gateway_status_empty(tmp_path, capsys):
    rc = main(["gateway", "status", "--ledger-dir", str(tmp_path / "gw")])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["event_count"] == 0


def test_gateway_inspect_and_report(tmp_path, capsys):
    _seed_ledger(tmp_path / "gw")
    rc = main(["gateway", "inspect", "--ledger-dir", str(tmp_path / "gw")])
    assert rc == 0
    rows = json.loads(capsys.readouterr().out)
    assert len(rows) == 2
    assert rows[1]["router_decision"] == "CHECK"

    rc = main(["gateway", "report", "--ledger-dir", str(tmp_path / "gw")])
    assert rc == 0
    rep = json.loads(capsys.readouterr().out)
    assert rep["event_count"] == 2
    assert rep["shadow_would_intervene_rate"] == 0.5
    assert rep["additional_cortex_tokens"] == 0


def test_gateway_replay(tmp_path, capsys):
    _seed_ledger(tmp_path / "gw")
    rc = main(["gateway", "replay", "--ledger-dir", str(tmp_path / "gw"), "--request-id", "b2"])
    assert rc == 0
    row = json.loads(capsys.readouterr().out)
    assert row["request_id"] == "b2"


def test_gateway_replay_missing(tmp_path, capsys):
    _seed_ledger(tmp_path / "gw")
    rc = main(["gateway", "replay", "--ledger-dir", str(tmp_path / "gw"), "--request-id", "zzz"])
    assert rc == 1


def test_gateway_doctor_ok(tmp_path, capsys):
    rc = main([
        "gateway", "doctor",
        "--ledger-dir", str(tmp_path / "gw"),
        "--upstream-base-url", "http://127.0.0.1:11434/v1",
    ])
    out = json.loads(capsys.readouterr().out)
    assert out["ok"] is True
    assert rc == 0


def test_gateway_doctor_rejects_unsafe_upstream(tmp_path, capsys):
    rc = main([
        "gateway", "doctor",
        "--ledger-dir", str(tmp_path / "gw"),
        "--upstream-base-url", "http://169.254.169.254/v1",
    ])
    out = json.loads(capsys.readouterr().out)
    assert out["ok"] is False
    assert rc == 1


def test_serve_requires_upstream(capsys):
    rc = main(["serve"])
    assert rc == 2
    assert "upstream" in capsys.readouterr().out.lower()


def test_serve_rejects_non_loopback_bind_without_optin(capsys):
    rc = main(["serve", "--bind", "0.0.0.0", "--upstream-base-url", "http://127.0.0.1:11434/v1"])
    assert rc == 2
    assert "loopback" in capsys.readouterr().out.lower()
