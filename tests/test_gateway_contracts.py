"""Stage 1 — provider-neutral gateway contract tests.

These cover the SDK-free core: normalized protocol types, the deterministic
Cortex Router, the config/security validator (SSRF + binds), and the event
ledger's redaction/hashing. No network, no server.
"""
from __future__ import annotations

import pytest

from piensalo.gateway.config import ConfigError, GatewayConfig
from piensalo.gateway.ledger import EventLedger, GatewayEvent, content_hash, redact_headers
from piensalo.gateway.protocol import (
    ContentBlock,
    Message,
    NormalizedRequest,
    ToolDef,
    estimate_tokens,
)
from piensalo.gateway.router import CortexRouter, RouterPolicy


# --- protocol ---------------------------------------------------------------


def test_estimate_tokens_deterministic_and_ceil():
    assert estimate_tokens("") == 0
    assert estimate_tokens("a") == 1  # ceil(1/4)
    assert estimate_tokens("abcd") == 1
    assert estimate_tokens("abcde") == 2
    # deterministic
    assert estimate_tokens("hello world") == estimate_tokens("hello world")


def _req(text: str, **kw) -> NormalizedRequest:
    return NormalizedRequest(
        model=kw.pop("model", "provider/m"),
        messages=[Message(role="user", content=[ContentBlock(type="text", text=text)])],
        **kw,
    )


def test_request_feature_accessors():
    req = _req("hi there", tools=[ToolDef(name="search")], stream=True)
    assert req.has_tools() is True
    assert req.stream is True
    assert req.input_tokens_est() > 0
    assert req.last_user_text() == "hi there"
    assert req.has_images() is False


def test_image_block_detected():
    req = NormalizedRequest(
        model="m",
        messages=[Message(role="user", content=[ContentBlock(type="image", data={"url": "x"})])],
    )
    assert req.has_images() is True


# --- router -----------------------------------------------------------------


def test_router_passthrough_on_trivial_request():
    r = CortexRouter()
    d = r.decide(_req("hi"))
    assert d.decision == "PASS_THROUGH"
    assert d.shadow is True
    assert d.intervention_budget == {}
    assert d.reasons


def test_router_context_on_large_input():
    r = CortexRouter(RouterPolicy(context_token_threshold=50))
    big = "word " * 100  # ~500 chars -> ~125 tokens > 50
    d = r.decide(_req(big))
    assert "CONTEXT" in d.decision
    assert d.intervention_budget["max_attempts"] == 2


def test_router_check_on_deterministic_requirements():
    r = CortexRouter()
    text = "Return JSON. It must include a name. Output exactly this format. Only return the table."
    d = r.decide(_req(text))
    assert "CHECK" in d.decision


def test_router_full_cortex_when_all_signals_fire():
    # NOTE: deliberately avoids exact-delivery wording ("output exactly",
    # "nothing else", …) — that suppresses THINK by design (NR-11 guard),
    # which test_router_exact_delivery.py covers.
    r = CortexRouter(RouterPolicy(context_token_threshold=10, check_requirement_threshold=2))
    text = (
        "Plan step by step how to approach this. "
        "The result must be valid JSON following the schema format. "
        + ("filler " * 30)
    )
    d = r.decide(_req(text))
    assert d.decision == "FULL_CORTEX"
    assert 0.0 < d.confidence <= 0.95


def test_router_exact_delivery_suppresses_think_in_combined_signals():
    # The same request WITH an exact-delivery demand must drop the THINK
    # component (NR-11: plan scaffolding measurably harms exact formats).
    r = CortexRouter(RouterPolicy(context_token_threshold=10, check_requirement_threshold=2))
    text = (
        "Plan step by step how to approach this. "
        "The result must be valid JSON following the schema format. "
        "Output exactly this format and nothing else. "
        + ("filler " * 30)
    )
    d = r.decide(_req(text))
    assert d.decision == "CONTEXT_AND_CHECK"
    assert any("EXACT_DELIVERY_CONTRACT" in reason for reason in d.reasons)


def test_router_is_deterministic():
    r = CortexRouter()
    text = "Plan step by step. Must return JSON exactly. " + "x " * 50
    a = r.decide(_req(text)).to_dict()
    b = r.decide(_req(text)).to_dict()
    assert a == b


def test_router_reasons_are_present_for_every_decision():
    r = CortexRouter(RouterPolicy(context_token_threshold=10))
    d = r.decide(_req("word " * 50))
    assert d.reasons  # never an unexplained decision


# --- config / SSRF ----------------------------------------------------------


def test_config_defaults_are_safe():
    cfg = GatewayConfig.build()
    assert cfg.bind_host == "127.0.0.1"
    assert cfg.no_store is True
    assert cfg.redact is True
    assert "auth_token" not in cfg.public_summary()


def test_config_rejects_non_loopback_bind_without_optin():
    with pytest.raises(ConfigError):
        GatewayConfig.build(bind_host="0.0.0.0")


def test_config_allows_non_loopback_bind_with_optin():
    cfg = GatewayConfig.build(bind_host="0.0.0.0", allow_non_loopback_bind=True)
    assert cfg.public_summary()["loopback_only"] is False


def test_config_rejects_bad_upstream_scheme():
    with pytest.raises(ConfigError):
        GatewayConfig.build(upstream_base_url="ftp://example.com/v1")


def test_config_blocks_link_local_metadata_upstream():
    # 169.254.169.254 is the classic cloud-metadata SSRF target.
    with pytest.raises(ConfigError) as e:
        GatewayConfig.build(upstream_base_url="http://169.254.169.254/v1")
    assert "link-local" in str(e.value).lower() or "blocked" in str(e.value).lower()


def test_config_allows_loopback_upstream():
    cfg = GatewayConfig.build(upstream_base_url="http://127.0.0.1:11434/v1")
    assert cfg.upstream_base_url.endswith("/v1")


def test_config_allowlist_prefix_enforced():
    with pytest.raises(ConfigError):
        GatewayConfig.build(
            upstream_base_url="http://127.0.0.1:9/v1",
            allowed_upstream_prefixes=("http://127.0.0.1:11434",),
        )


def test_config_full_retention_conflicts_with_no_store():
    with pytest.raises(ConfigError):
        GatewayConfig.build(retention="full", no_store=True)


# --- ledger -----------------------------------------------------------------


def test_content_hash_stable():
    assert content_hash("abc") == content_hash(b"abc")
    assert content_hash("abc").startswith("sha256:")


def test_redact_headers_drops_secrets():
    headers = {"Authorization": "Bearer sk-secret", "User-Agent": "claude-code", "X-Api-Key": "k"}
    red = redact_headers(headers, redact=True)
    assert red["authorization"] == "<redacted>"
    assert red["x-api-key"] == "<redacted>"
    assert red["user-agent"] == "<present>"
    assert "sk-secret" not in str(red)


def test_redact_headers_keeps_values_when_not_redacting_but_still_hides_secrets():
    headers = {"Authorization": "Bearer sk", "User-Agent": "x"}
    red = redact_headers(headers, redact=False)
    assert red["authorization"] == "<redacted>"  # secrets always dropped
    assert red["user-agent"] == "x"


def test_ledger_roundtrip(tmp_path):
    led = EventLedger(tmp_path / "gw")
    ev = GatewayEvent(request_id="r1", requested_model="m", router_decision="PASS_THROUGH")
    led.append(ev)
    ev2 = GatewayEvent(request_id="r2", requested_model="m", router_decision="CHECK")
    led.append(ev2)
    allrows = led.read_all()
    assert len(allrows) == 2
    assert led.read_last(1)[0]["request_id"] == "r2"
    assert led.find("r1")["router_decision"] == "PASS_THROUGH"
    # ts auto-populated
    assert allrows[0]["ts"].endswith("Z")


def test_ledger_never_writes_bodies_by_default(tmp_path):
    led = EventLedger(tmp_path / "gw")
    ev = GatewayEvent(request_id="r1", request_hash=content_hash("secret prompt"))
    led.append(ev)
    row = led.read_all()[0]
    assert "request_body" not in row  # None fields dropped
    assert row["request_hash"].startswith("sha256:")
    assert "secret prompt" not in led.path.read_text()
