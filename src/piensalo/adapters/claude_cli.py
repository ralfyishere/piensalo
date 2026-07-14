"""Adapter for the ``claude`` CLI (headless ``-p`` mode).

Shells out to ``claude -p --model <id> --output-format json`` and parses
the JSON result. The result's ``modelUsage`` map is asserted to contain
ONLY the requested model id — if any other model appears (quota fallback,
safeguard reroute), the adapter raises ``ModelFallbackError`` and the
output is discarded. NO fallback, ever: a cell produced under a
substituted model is invalid, not degraded.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import time

from piensalo.adapters.base import AdapterError, ModelAdapter, ModelResponse


class ClaudeCliAdapter(ModelAdapter):
    """Run one prompt through the ``claude`` CLI with pinned provenance."""

    provider = "claude-cli"

    def __init__(self, model: str, timeout: int = 600,
                 executable: str = "claude", tools: str = ""):
        super().__init__(model)
        self.timeout = timeout
        self.executable = executable
        # "" disables all tools: this adapter's contract is ONE prompt ->
        # ONE completion. Leaving tools on lets the model explore the
        # local machine, which both breaks that contract and contaminates
        # any context-limited comparison (the model can read the full
        # context off disk).
        self.tools = tools

    def complete(self, prompt: str) -> ModelResponse:
        if shutil.which(self.executable) is None:
            raise AdapterError(
                f"{self.executable!r} CLI not found on PATH — install it or use "
                "another adapter"
            )
        start = time.monotonic()
        proc = subprocess.run(
            [
                self.executable,
                "-p",
                "--model",
                self.requested_model,
                "--output-format",
                "json",
                "--tools",
                self.tools,
            ],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=self.timeout,
        )
        wall = time.monotonic() - start
        if proc.returncode != 0:
            raise AdapterError(
                f"claude CLI exited {proc.returncode}: {proc.stderr.strip()[:500]}"
            )
        try:
            result = json.loads(proc.stdout)
        except json.JSONDecodeError as e:
            raise AdapterError(f"claude CLI returned non-JSON output: {e}") from e

        usage_models = list((result.get("modelUsage") or {}).keys())
        resolved = usage_models[0] if len(usage_models) == 1 else ",".join(usage_models)
        for used in usage_models:
            if self.requested_model not in used:
                self.assert_no_fallback(used)
        if not usage_models:
            raise AdapterError("claude CLI result has no modelUsage — provenance unverifiable")

        usage = result.get("usage", {})
        # Total billed input: the CLI splits the prompt across
        # input_tokens and the cache-accounting buckets; reporting only
        # input_tokens (often ~9) silently understates real usage.
        tokens_in = (usage.get("input_tokens", 0)
                     + usage.get("cache_creation_input_tokens", 0)
                     + usage.get("cache_read_input_tokens", 0))
        return ModelResponse(
            text=result.get("result", ""),
            requested_model=self.requested_model,
            resolved_model=resolved,
            provider=self.provider,
            tokens_in=tokens_in,
            tokens_out=usage.get("output_tokens", 0),
            wall_seconds=wall,
            raw=result,
        )
