"""Adapter for a local Ollama server (stdlib only).

POSTs to ``/api/generate`` on a local Ollama instance via ``urllib``. Only
used when explicitly configured; an unreachable server is a clear error.
Ollama echoes the model it ran — a mismatch with the requested model
raises ``ModelFallbackError``.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

from piensalo.adapters.base import AdapterError, ModelAdapter, ModelResponse


class OllamaAdapter(ModelAdapter):
    """Single-shot generation against a local Ollama server."""

    provider = "ollama"

    def __init__(self, model: str, base_url: str = "http://localhost:11434", timeout: int = 600):
        super().__init__(model)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def complete(self, prompt: str) -> ModelResponse:
        body = json.dumps(
            {"model": self.requested_model, "prompt": prompt, "stream": False}
        ).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        start = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise AdapterError(
                f"HTTP {e.code} from ollama: {e.read().decode('utf-8', 'replace')[:500]}"
            ) from e
        except urllib.error.URLError as e:
            raise AdapterError(
                f"cannot reach ollama at {self.base_url}: {e.reason} — is it running?"
            ) from e
        wall = time.monotonic() - start

        resolved = result.get("model", "")
        if resolved and resolved != self.requested_model:
            self.assert_no_fallback(resolved)
        return ModelResponse(
            text=result.get("response", ""),
            requested_model=self.requested_model,
            resolved_model=resolved or self.requested_model,
            provider=self.provider,
            tokens_in=result.get("prompt_eval_count", 0),
            tokens_out=result.get("eval_count", 0),
            wall_seconds=wall,
            raw=result,
        )
