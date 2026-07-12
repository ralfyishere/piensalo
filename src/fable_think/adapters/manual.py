"""Manual adapter: the human is the transport.

Prints the prompt for the operator to paste into any model UI, then reads
the model's response back from a file (or stdin). Provenance is whatever
the operator attests: the model name given at construction is recorded as
both requested and resolved, since no provider is in the loop to verify
it. Useful for offline workflows and models with no API access.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

from fable_think.adapters.base import ModelAdapter, ModelResponse


class ManualAdapter(ModelAdapter):
    """Print prompt; read response from ``response_file`` or stdin."""

    provider = "manual"

    def __init__(self, model: str = "operator-attested", response_file: str | None = None):
        super().__init__(model)
        self.response_file = response_file

    def complete(self, prompt: str) -> ModelResponse:
        start = time.monotonic()
        print("=== PROMPT (paste into your model) ===")
        print(prompt)
        print("=== END PROMPT ===")
        if self.response_file:
            text = Path(self.response_file).read_text(encoding="utf-8")
        else:
            print("Paste the model response, then EOF (Ctrl-D):", file=sys.stderr)
            text = sys.stdin.read()
        return ModelResponse(
            text=text,
            requested_model=self.requested_model,
            resolved_model=self.requested_model,
            provider=self.provider,
            wall_seconds=time.monotonic() - start,
        )
