"""Adapter base contract: provenance-first model access, fallback prohibited.

``ModelAdapter`` defines the one method adapters implement (``complete``)
and the invariants every implementation must honor: the response records
the requested model, the resolved model the provider actually used, the
provider name, token counts, and wall time — and if resolved != requested,
the adapter raises ``ModelFallbackError`` instead of returning output.
Silently-substituted models poison provenance; a loud failure is the
feature.
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field


class AdapterError(Exception):
    """Base class for adapter failures (missing config, transport, parse)."""


class ModelFallbackError(AdapterError):
    """Raised when the provider resolved a different model than requested.

    Fallback is PROHIBITED: work produced under a substituted model must
    never be attributed to the requested one.
    """

    def __init__(self, requested: str, resolved: str):
        self.requested = requested
        self.resolved = resolved
        super().__init__(
            f"model fallback prohibited: requested {requested!r} but provider "
            f"resolved {resolved!r} — refusing to return misattributed output"
        )


@dataclass
class ModelResponse:
    """A completion plus its full provenance record."""

    text: str
    requested_model: str
    resolved_model: str
    provider: str
    tokens_in: int = 0
    tokens_out: int = 0
    wall_seconds: float = 0.0
    raw: dict = field(default_factory=dict)


class ModelAdapter(abc.ABC):
    """Abstract model adapter. Subclasses implement ``complete``."""

    provider: str = "unknown"

    def __init__(self, model: str):
        self.requested_model = model

    @abc.abstractmethod
    def complete(self, prompt: str) -> ModelResponse:
        """Run one completion. MUST populate provenance fields and MUST
        raise ``ModelFallbackError`` if the provider substituted a model."""

    def assert_no_fallback(self, resolved: str) -> None:
        """Shared invariant check for subclasses."""
        if resolved != self.requested_model:
            raise ModelFallbackError(self.requested_model, resolved)
