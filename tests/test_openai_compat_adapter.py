"""OpenAICompatAdapter: extra_body generation settings (deterministic runs).

The adapter accepts optional request extras (temperature/seed/max_tokens…) for
reproducible evaluation runs. Invariants: extras merge into the body, cannot
override model/messages, and omitting them leaves the request unchanged.
"""
from __future__ import annotations

import json

import pytest

from piensalo.adapters.base import AdapterError
from piensalo.adapters.openai_compat import OpenAICompatAdapter


class _FakeResp:
    def __init__(self, payload: dict):
        self._data = json.dumps(payload).encode()

    def read(self):
        return self._data

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _ok_payload(model="m"):
    return {
        "model": model,
        "choices": [{"message": {"content": "hi"}}],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1},
    }


def _run_with_captured_body(adapter, monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["body"] = json.loads(req.data.decode())
        return _FakeResp(_ok_payload(adapter.requested_model))

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    adapter.complete("prompt text")
    return captured["body"]


def test_extra_body_merged(monkeypatch):
    a = OpenAICompatAdapter("m", extra_body={"temperature": 0, "seed": 42})
    body = _run_with_captured_body(a, monkeypatch)
    assert body["temperature"] == 0 and body["seed"] == 42
    assert body["model"] == "m"
    assert body["messages"][0]["content"] == "prompt text"


def test_extra_body_cannot_override_model_or_messages():
    with pytest.raises(AdapterError):
        OpenAICompatAdapter("m", extra_body={"model": "other"})
    with pytest.raises(AdapterError):
        OpenAICompatAdapter("m", extra_body={"messages": []})


def test_no_extra_body_leaves_request_unchanged(monkeypatch):
    a = OpenAICompatAdapter("m")
    body = _run_with_captured_body(a, monkeypatch)
    assert set(body.keys()) == {"model", "messages"}
