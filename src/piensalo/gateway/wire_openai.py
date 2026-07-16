"""OpenAI Chat Completions protocol adapter (edge only).

This is the ONLY module that knows the OpenAI `/v1/chat/completions` wire shape.
It does two things:

1. ``parse_request`` — decode a request body into a provider-neutral
   :class:`NormalizedRequest` **for the router to reason about**. This is a
   read-only projection; observe mode never re-serializes the request. The
   original bytes are forwarded verbatim.

2. ``parse_response`` / ``parse_stream_metadata`` — read a *copy* of the
   upstream response to extract usage, resolved model, tool-call count, and
   finish reason for the ledger. The bytes the client receives are never
   produced here — observe mode streams the upstream bytes straight through.

Nothing here mutates traffic. Parsing is best-effort and defensive: a body we
cannot parse yields an empty/normalized shell, never an exception that would
break pass-through.
"""
from __future__ import annotations

import json

from .protocol import (
    ContentBlock,
    Message,
    NormalizedRequest,
    NormalizedResponse,
    ToolCall,
    ToolDef,
    Usage,
)

PROTOCOL = "openai.chat"


def parse_request(body: bytes, *, request_id: str | None = None) -> NormalizedRequest:
    """Project an OpenAI Chat Completions request body into a NormalizedRequest.
    Best-effort: unparseable bodies yield a shell with model=='' so the router
    simply passes through."""
    try:
        data = json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return NormalizedRequest(model="", protocol=PROTOCOL, request_id=request_id)
    if not isinstance(data, dict):
        return NormalizedRequest(model="", protocol=PROTOCOL, request_id=request_id)

    messages: list[Message] = []
    for m in data.get("messages", []) or []:
        if not isinstance(m, dict):
            continue
        role = str(m.get("role", "user"))
        blocks = _content_blocks(m.get("content"))
        # Tool calls on an assistant message are structured content too.
        for tc in m.get("tool_calls", []) or []:
            fn = (tc or {}).get("function", {}) if isinstance(tc, dict) else {}
            blocks.append(
                ContentBlock(
                    type="tool_use",
                    data={"name": fn.get("name", ""), "arguments": fn.get("arguments", "")},
                )
            )
        messages.append(Message(role=role, content=blocks, name=m.get("name")))

    tools: list[ToolDef] = []
    for t in data.get("tools", []) or []:
        if not isinstance(t, dict):
            continue
        fn = t.get("function", {}) if isinstance(t.get("function"), dict) else {}
        tools.append(
            ToolDef(
                name=fn.get("name", ""),
                description=fn.get("description", ""),
                parameters=fn.get("parameters", {}) or {},
            )
        )

    return NormalizedRequest(
        model=str(data.get("model", "")),
        messages=messages,
        tools=tools,
        stream=bool(data.get("stream", False)),
        max_tokens=data.get("max_tokens"),
        temperature=data.get("temperature"),
        protocol=PROTOCOL,
        request_id=request_id,
        raw=data,
    )


def _content_blocks(content) -> list[ContentBlock]:
    """Normalize the polymorphic OpenAI ``content`` field."""
    if content is None:
        return []
    if isinstance(content, str):
        return [ContentBlock(type="text", text=content)] if content else []
    blocks: list[ContentBlock] = []
    if isinstance(content, list):
        for part in content:
            if not isinstance(part, dict):
                continue
            ptype = part.get("type")
            if ptype == "text":
                blocks.append(ContentBlock(type="text", text=part.get("text", "")))
            elif ptype in ("image_url", "input_image", "image"):
                blocks.append(ContentBlock(type="image", data=part))
            else:
                blocks.append(ContentBlock(type="text", text=json.dumps(part, default=str)))
    return blocks


def parse_response(body: bytes, *, requested_model: str = "") -> NormalizedResponse:
    """Parse a non-streaming Chat Completions response body for ledger metadata.
    Best-effort; never raises."""
    resp = NormalizedResponse(requested_model=requested_model, streamed=False)
    try:
        data = json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return resp
    if not isinstance(data, dict):
        return resp
    resp.resolved_model = str(data.get("model", ""))
    usage = data.get("usage") or {}
    if isinstance(usage, dict):
        resp.usage = Usage(
            tokens_in=int(usage.get("prompt_tokens", 0) or 0),
            tokens_out=int(usage.get("completion_tokens", 0) or 0),
            measured=True,
        )
    choices = data.get("choices") or []
    if choices and isinstance(choices[0], dict):
        msg = choices[0].get("message", {}) or {}
        resp.text = msg.get("content") or ""
        resp.finish_reason = choices[0].get("finish_reason")
        for tc in msg.get("tool_calls", []) or []:
            fn = (tc or {}).get("function", {}) if isinstance(tc, dict) else {}
            resp.tool_calls.append(
                ToolCall(
                    id=str((tc or {}).get("id", "")),
                    name=fn.get("name", ""),
                    arguments_json=fn.get("arguments", "") or "",
                )
            )
    return resp


def parse_stream_metadata(chunks: list[bytes], *, requested_model: str = "") -> NormalizedResponse:
    """Reassemble metadata from a captured copy of the SSE stream.

    We do NOT reconstruct the exact client output — the client already received
    the raw bytes. We only tally resolved model, tool-call ids, finish reason,
    and usage (if the upstream sends a final usage chunk).
    """
    resp = NormalizedResponse(requested_model=requested_model, streamed=True)
    tool_ids: dict[int, ToolCall] = {}
    buf = b"".join(chunks)
    for line in buf.split(b"\n"):
        line = line.strip()
        if not line.startswith(b"data:"):
            continue
        payload = line[len(b"data:"):].strip()
        if payload == b"[DONE]" or not payload:
            continue
        try:
            evt = json.loads(payload.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            continue
        if not isinstance(evt, dict):
            continue
        if evt.get("model") and not resp.resolved_model:
            resp.resolved_model = str(evt["model"])
        usage = evt.get("usage")
        if isinstance(usage, dict):
            resp.usage = Usage(
                tokens_in=int(usage.get("prompt_tokens", 0) or 0),
                tokens_out=int(usage.get("completion_tokens", 0) or 0),
                measured=True,
            )
        for choice in evt.get("choices", []) or []:
            if not isinstance(choice, dict):
                continue
            if choice.get("finish_reason"):
                resp.finish_reason = choice["finish_reason"]
            delta = choice.get("delta", {}) or {}
            if isinstance(delta.get("content"), str):
                resp.text += delta["content"]
            for tc in delta.get("tool_calls", []) or []:
                if not isinstance(tc, dict):
                    continue
                idx = tc.get("index", 0)
                slot = tool_ids.setdefault(idx, ToolCall(id="", name=""))
                if tc.get("id"):
                    slot.id = str(tc["id"])
                fn = tc.get("function", {}) or {}
                if fn.get("name"):
                    slot.name += fn["name"]
                if fn.get("arguments"):
                    slot.arguments_json += fn["arguments"]
    resp.tool_calls = [tool_ids[k] for k in sorted(tool_ids)]
    return resp
