"""piensalo.adapters — optional model adapters, imported lazily.

The core never imports these at module load; ``get_adapter`` resolves one
by name only when a caller explicitly configures execution. Every adapter
records requested vs. resolved model and PROHIBITS silent fallback: if the
provider substitutes a different model, the adapter raises instead of
returning misattributed output.
"""
from __future__ import annotations

_ADAPTERS = {
    "manual": ("piensalo.adapters.manual", "ManualAdapter"),
    "claude-cli": ("piensalo.adapters.claude_cli", "ClaudeCliAdapter"),
    "openai-compat": ("piensalo.adapters.openai_compat", "OpenAICompatAdapter"),
    "ollama": ("piensalo.adapters.ollama", "OllamaAdapter"),
}


def adapter_names() -> list[str]:
    """Names accepted by ``get_adapter``."""
    return sorted(_ADAPTERS)


def get_adapter(name: str, **kwargs):
    """Instantiate an adapter by name (lazy import)."""
    if name not in _ADAPTERS:
        raise KeyError(f"unknown adapter {name!r}; available: {', '.join(adapter_names())}")
    module_name, class_name = _ADAPTERS[name]
    import importlib

    module = importlib.import_module(module_name)
    return getattr(module, class_name)(**kwargs)
