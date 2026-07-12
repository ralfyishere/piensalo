"""Adapter for OpenAI-compatible chat-completions endpoints (stdlib only).

Uses ``urllib`` — no SDK dependency. Only used when explicitly configured;
a missing API key is a clear, immediate error, never a silent no-op. The
response's ``model`` field is checked against the request: a substituted
model raises ``ModelFallbackError``.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

from piensalo.adapters.base import AdapterError, ModelAdapter, ModelResponse


class OpenAICompatAdapter(ModelAdapter):
    """POST to ``<base_url>/chat/completions`` with a bearer key."""

    provider = "openai-compat"

    def __init__(
        self,
        model: str,
        base_url: str = "https://api.openai.com/v1",
        api_key_env: str = "OPENAI_API_KEY",
        timeout: int = 300,
    ):
        super().__init__(model)
        self.base_url = base_url.rstrip("/")
        self.api_key_env = api_key_env
        self.timeout = timeout

    def complete(self, prompt: str) -> ModelResponse:
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise AdapterError(
                f"no API key: set {self.api_key_env} to use the {self.provider} adapter"
            )
        body = json.dumps(
            {
                "model": self.requested_model,
                "messages": [{"role": "user", "content": prompt}],
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        start = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise AdapterError(
                f"HTTP {e.code} from {self.base_url}: {e.read().decode('utf-8', 'replace')[:500]}"
            ) from e
        except urllib.error.URLError as e:
            raise AdapterError(f"cannot reach {self.base_url}: {e.reason}") from e
        wall = time.monotonic() - start

        resolved = result.get("model", "")
        # Providers may suffix a snapshot date; exact-prefix match is the
        # attribution boundary, anything else is a fallback.
        if not resolved.startswith(self.requested_model):
            self.assert_no_fallback(resolved)
        usage = result.get("usage", {})
        try:
            text = result["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise AdapterError(f"malformed completion response: {e}") from e
        return ModelResponse(
            text=text,
            requested_model=self.requested_model,
            resolved_model=resolved,
            provider=self.provider,
            tokens_in=usage.get("prompt_tokens", 0),
            tokens_out=usage.get("completion_tokens", 0),
            wall_seconds=wall,
            raw=result,
        )
