"""Provider-neutral, SDK-free protocol types for the Cortex Gateway.

These types are the neutral boundary between wire protocols (OpenAI Chat
Completions today; Anthropic Messages / OpenAI Responses later) and the
cognitive core. They carry only what the router and ledger need to reason
about a request — never provider-specific serialization details.

Design rules:

- No provider SDK import. No wire serialization here.
- Everything is a plain dataclass so it is trivially inspectable and
  JSON-serializable for the ledger.
- Token counts are *estimates* unless a provider reports usage; estimates are
  labelled as such (``tokens_in_est``) and never presented as measured.

Token estimation is deliberately crude and deterministic (chars/4). It exists
to let the router compare request sizes against a configured threshold, not to
bill anyone. It is documented as an estimate everywhere it surfaces.
"""
from __future__ import annotations

from dataclasses import dataclass, field

# Roles the neutral core understands. Wire adapters map their own role names
# onto these; unknown roles are preserved verbatim in ``role`` but do not get
# special treatment.
ROLES = ("system", "developer", "user", "assistant", "tool")

# Content block types. ``data`` holds the block-specific payload so the core
# stays agnostic about provider shapes.
BLOCK_TYPES = ("text", "image", "tool_use", "tool_result", "reasoning")


def estimate_tokens(text: str) -> int:
    """Deterministic, provider-neutral token *estimate* (~4 chars/token).

    This is an estimate, never a measurement. It is used only to compare
    request sizes against configured thresholds. Empty/whitespace -> 0.
    """
    if not text:
        return 0
    # ceil(len/4) so a short non-empty string still counts as >=1.
    return (len(text) + 3) // 4


@dataclass
class ContentBlock:
    """One piece of message content. ``text`` for text/reasoning; ``data`` for
    structured blocks (image refs, tool_use args, tool_result payloads)."""

    type: str
    text: str = ""
    data: dict = field(default_factory=dict)

    def token_estimate(self) -> int:
        n = estimate_tokens(self.text)
        # Count a stable estimate for structured payloads too, so tool-heavy
        # requests are not treated as empty.
        if self.data:
            import json

            n += estimate_tokens(json.dumps(self.data, sort_keys=True, default=str))
        return n


@dataclass
class Message:
    """A single normalized message: a role plus a list of content blocks."""

    role: str
    content: list[ContentBlock] = field(default_factory=list)
    name: str | None = None

    def text(self) -> str:
        return "\n".join(b.text for b in self.content if b.type in ("text", "reasoning"))

    def token_estimate(self) -> int:
        return sum(b.token_estimate() for b in self.content)


@dataclass
class ToolDef:
    """A tool the client offered the model."""

    name: str
    description: str = ""
    parameters: dict = field(default_factory=dict)


@dataclass
class ToolCall:
    """A tool call the model emitted. ``arguments_json`` is the raw argument
    string exactly as the provider produced it (never re-serialized)."""

    id: str
    name: str
    arguments_json: str = ""


@dataclass
class Usage:
    """Token usage. ``measured`` is True only when a provider reported it;
    otherwise the counts are estimates and ``measured`` is False."""

    tokens_in: int = 0
    tokens_out: int = 0
    measured: bool = False


@dataclass
class NormalizedRequest:
    """A client request, reduced to what the router needs. ``raw`` holds the
    original decoded body for the wire adapter to forward verbatim; the ledger
    stores only hashes/metadata of it unless retention is explicitly enabled."""

    model: str
    messages: list[Message] = field(default_factory=list)
    tools: list[ToolDef] = field(default_factory=list)
    stream: bool = False
    max_tokens: int | None = None
    temperature: float | None = None
    protocol: str = "openai.chat"
    request_id: str | None = None
    raw: dict = field(default_factory=dict)

    # --- deterministic feature accessors used by the router ---

    def input_tokens_est(self) -> int:
        return sum(m.token_estimate() for m in self.messages)

    def message_count(self) -> int:
        return len(self.messages)

    def has_tools(self) -> bool:
        return bool(self.tools)

    def has_images(self) -> bool:
        return any(b.type == "image" for m in self.messages for b in m.content)

    def last_user_text(self) -> str:
        for m in reversed(self.messages):
            if m.role == "user":
                return m.text()
        return ""

    def all_text(self) -> str:
        return "\n".join(m.text() for m in self.messages)


@dataclass
class NormalizedResponse:
    """A model response, reduced to what the ledger records. Observe mode
    never constructs a response from the core — it parses a *copy* of the
    upstream bytes into this shape for metadata only."""

    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: str | None = None
    requested_model: str = ""
    resolved_model: str = ""
    usage: Usage = field(default_factory=Usage)
    streamed: bool = False
    raw: dict = field(default_factory=dict)

    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)
