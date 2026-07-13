"""Real-world context ingestion: normalize any source into neutral items.

Accepted sources: plain text, the explicit-marker transcript format,
generic JSONL messages, generic chat JSON (a list of messages or a
``{"messages": [...]}`` object), tool-call records, and repository/file
artifacts. Everything becomes a ``NormalizedItem`` — a provider-neutral
unit carrying role, content, optional timestamp/tool/model metadata, and a
content-hashed source reference. The optimizer core operates ONLY on this
normalized form; provider-specific shapes stop at this boundary.

Deterministic and offline: no clock, no network, no model call.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from piensalo.context import schema

ROLES = ("system", "user", "assistant", "tool", "artifact", "text")

# Directory ingestion bounds (documented, not silent): text-ish files only.
_TEXT_SUFFIXES = (
    ".py", ".md", ".txt", ".json", ".jsonl", ".toml", ".yaml", ".yml",
    ".cfg", ".ini", ".sh", ".js", ".ts", ".css", ".html", ".rst",
)
_MAX_ARTIFACT_BYTES = 262_144  # 256 KiB per file
_SKIP_DIR_NAMES = {".git", "__pycache__", "node_modules", ".venv", "venv",
                   "dist", "build", ".pytest_cache", ".ruff_cache"}


class IngestError(ValueError):
    """Honest, specific ingestion failure."""


@dataclass
class NormalizedItem:
    role: str
    content: str
    source_artifact: str          # e.g. "context", "artifact:src/x.py"
    source_location: str          # e.g. "lines:3-9", "message:4", "file"
    source_hash: str = ""
    timestamp: str | None = None
    tool_name: str | None = None
    artifact_ref: str | None = None
    model_provenance: str | None = None
    index: int = 0                # global order for recency scoring

    def __post_init__(self):
        if self.role not in ROLES:
            raise IngestError(f"unknown role {self.role!r}")
        if not self.source_hash:
            self.source_hash = schema.sha256_text(self.content)

    def source_reference(self) -> dict:
        return {
            "artifact_id": self.source_artifact,
            "location": self.source_location,
            "content_type": "text/plain",
            "content_hash": self.source_hash,
            "access_policy": "local",
        }


_MESSAGE_ROLE_MAP = {
    "system": "system", "user": "user", "human": "user",
    "assistant": "assistant", "model": "assistant", "ai": "assistant",
    "tool": "tool", "function": "tool", "tool_result": "tool",
}


def _model_provenance(obj: dict) -> str | None:
    for key in ("model", "source_model", "model_id"):
        val = obj.get(key)
        if isinstance(val, str) and val:
            return val
    return None


def _normalize_message(obj: dict, where: str, index: int) -> NormalizedItem:
    role = _MESSAGE_ROLE_MAP.get(str(obj.get("role", "")).lower())
    if role is None:
        raise IngestError(f"{where}: unknown message role {obj.get('role')!r}")
    content = obj.get("content")
    if isinstance(content, list):  # content-block style messages
        parts = []
        for block in content:
            if isinstance(block, dict) and isinstance(block.get("text"), str):
                parts.append(block["text"])
            elif isinstance(block, str):
                parts.append(block)
        content = "\n".join(parts)
    if not isinstance(content, str):
        raise IngestError(f"{where}: message content must be text")
    return NormalizedItem(
        role=role, content=content, source_artifact="context",
        source_location=where, timestamp=obj.get("timestamp"),
        tool_name=obj.get("tool_name") or obj.get("name"),
        model_provenance=_model_provenance(obj), index=index)


def _normalize_tool_record(obj: dict, where: str, index: int) -> NormalizedItem:
    tool = obj.get("tool") or obj.get("tool_name") or obj.get("tool_use")
    body_keys = [k for k in ("output", "result", "content", "stdout", "input")
                 if isinstance(obj.get(k), str)]
    body = "\n".join(obj[k] for k in body_keys) if body_keys \
        else json.dumps(obj, sort_keys=True, ensure_ascii=False)
    return NormalizedItem(
        role="tool", content=body, source_artifact="context",
        source_location=where, timestamp=obj.get("timestamp"),
        tool_name=str(tool), model_provenance=_model_provenance(obj),
        index=index)


def _normalize_object(obj: dict, where: str, index: int) -> NormalizedItem:
    if "role" in obj:
        return _normalize_message(obj, where, index)
    if any(k in obj for k in ("tool", "tool_name", "tool_use")):
        return _normalize_tool_record(obj, where, index)
    if "type" in obj and isinstance(obj.get("content"), str):
        # Existing typed-record JSONL shape: pass through as marker text so
        # the chunker's marker parser classifies it exactly once.
        marker = str(obj["type"]).upper().replace("_", " ")
        text = f"{marker}: {obj['content']}"
        if obj.get("status"):
            text = f"{marker} [{obj['status']}]: {obj['content']}"
        return NormalizedItem(role="text", content=text,
                              source_artifact="context",
                              source_location=where, index=index)
    # Unknown object shape: preserved verbatim, never reinterpreted.
    return NormalizedItem(
        role="text",
        content=json.dumps(obj, sort_keys=True, ensure_ascii=False),
        source_artifact="context", source_location=where, index=index)


def load_context_text(text: str, *, name: str = "context",
                      fmt: str = "auto") -> list[NormalizedItem]:
    """Normalize a context document already read into memory."""
    stripped = text.lstrip()
    if fmt == "auto":
        if stripped.startswith("{") or stripped.startswith("["):
            fmt = "jsonl" if _looks_jsonl(text) else "json"
        else:
            fmt = "text"
    if fmt == "text":
        return [NormalizedItem(role="text", content=text,
                               source_artifact=name, source_location="file",
                               index=0)]
    if fmt == "jsonl":
        items: list[NormalizedItem] = []
        for lineno, line in enumerate(text.split("\n"), 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise IngestError(f"line {lineno}: invalid JSON: {e}") from e
            if not isinstance(obj, dict):
                raise IngestError(
                    f"line {lineno}: each JSONL line must be an object")
            items.append(_normalize_object(obj, f"line:{lineno}", len(items)))
        return items
    if fmt == "json":
        try:
            doc = json.loads(text)
        except json.JSONDecodeError as e:
            raise IngestError(f"invalid JSON context: {e}") from e
        if isinstance(doc, dict) and isinstance(doc.get("messages"), list):
            doc = doc["messages"]
        if not isinstance(doc, list):
            raise IngestError(
                "JSON context must be a message list or {'messages': [...]}")
        items = []
        for i, obj in enumerate(doc):
            if not isinstance(obj, dict):
                raise IngestError(f"message {i}: must be an object")
            items.append(_normalize_object(obj, f"message:{i}", len(items)))
        return items
    raise IngestError(f"unknown context format {fmt!r} (text|json|jsonl|auto)")


def _looks_jsonl(text: str) -> bool:
    lines = [ln for ln in text.split("\n") if ln.strip()]
    if len(lines) < 2:
        return False
    try:
        json.loads(lines[0])
        json.loads(lines[1])
        return True
    except json.JSONDecodeError:
        return False


def load_context_file(path: str) -> list[NormalizedItem]:
    p = Path(path)
    if not p.is_file():
        raise IngestError(f"context file not found: {path}")
    text = p.read_text(encoding="utf-8")
    suffix = p.suffix.lower()
    fmt = {"": "auto", ".txt": "text", ".md": "text", ".log": "text",
           ".jsonl": "jsonl", ".ndjson": "jsonl", ".json": "json"}.get(
        suffix, "auto")
    return load_context_text(text, name=str(path), fmt=fmt)


def load_artifacts(paths: list[str]) -> list[NormalizedItem]:
    """Ingest file/directory artifacts as referenceable context items."""
    items: list[NormalizedItem] = []
    for raw in paths:
        p = Path(raw)
        if p.is_file():
            files = [p]
        elif p.is_dir():
            files = sorted(
                f for f in p.rglob("*")
                if f.is_file() and f.suffix.lower() in _TEXT_SUFFIXES
                and not any(part in _SKIP_DIR_NAMES for part in f.parts))
        else:
            raise IngestError(f"artifact not found: {raw}")
        for f in files:
            if f.stat().st_size > _MAX_ARTIFACT_BYTES:
                items.append(NormalizedItem(
                    role="artifact",
                    content=f"(artifact too large to inline: {f}, "
                            f"{f.stat().st_size} bytes — referenced only)",
                    source_artifact=f"artifact:{f}", source_location="file",
                    artifact_ref=str(f), index=len(items)))
                continue
            items.append(NormalizedItem(
                role="artifact", content=f.read_text(encoding="utf-8",
                                                     errors="replace"),
                source_artifact=f"artifact:{f}", source_location="file",
                artifact_ref=str(f), index=len(items)))
    return items
