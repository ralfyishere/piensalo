"""Context MVP: model-independence acceptance gate.

The deterministic core must run with no provider SDK, no credential, no
network, and no model call — and its artifacts must be provider-neutral.
"""
from __future__ import annotations

import re
import socket
import sys
from pathlib import Path

import pytest

from piensalo.context import diff as diff_mod
from piensalo.context import verify
from piensalo.context.compiler import compile_to_dir

CONTEXT_SRC = Path(__file__).resolve().parent.parent / "src" / "piensalo" / "context"

FORBIDDEN_IMPORTS = re.compile(
    r"^\s*(?:import|from)\s+(anthropic|openai|google|genai|mistralai|cohere|"
    r"ollama|litellm|langchain\w*|boto3|requests|httpx|aiohttp|urllib|"
    r"http\b|socket|ssl)",
    re.MULTILINE,
)

CREDENTIAL_ENV_VARS = (
    "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY",
    "XAI_API_KEY", "MISTRAL_API_KEY", "COHERE_API_KEY", "AWS_ACCESS_KEY_ID",
    "OLLAMA_HOST",
)

TRANSCRIPT = """\
OBJECTIVE: Ship the widget.
DECISION: Use sqlite for storage.
CONSTRAINT: Never force-push to main.
STOP CONDITION: Stop after two consecutive failures.
NEXT ACTION: Run `uv run pytest -q`.
"""


def test_context_source_imports_no_provider_or_network_module():
    assert CONTEXT_SRC.is_dir()
    for py in sorted(CONTEXT_SRC.glob("*.py")):
        text = py.read_text(encoding="utf-8")
        m = FORBIDDEN_IMPORTS.search(text)
        assert m is None, f"{py.name} imports forbidden module {m.group(1)!r}"


def test_context_runtime_loads_no_provider_or_adapter_module(project_root):
    """Runs in a fresh interpreter: pytest collection itself imports
    piensalo.adapters (fake-adapter tests), so in-process sys.modules
    cannot measure what the context core loads."""
    import subprocess
    src = project_root / "t.txt"
    src.write_text(TRANSCRIPT, encoding="utf-8")
    code = (
        "import sys\n"
        f"sys.path.insert(0, {str(CONTEXT_SRC.parent.parent)!r})\n"
        "from piensalo.context.compiler import compile_to_dir\n"
        "from piensalo.context import verify\n"
        "compile_to_dir('t.txt', 'out', goal='g', token_budget=5000)\n"
        "verify.verify_dir('out')\n"
        "loaded = [m for m in sys.modules if m.startswith(("
        "'anthropic', 'openai', 'requests', 'httpx', 'piensalo.adapters'))]\n"
        "assert not loaded, loaded\n"
        "print('CLEAN')\n"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True,
                          text=True, cwd=str(project_root))
    assert proc.returncode == 0, proc.stderr
    assert "CLEAN" in proc.stdout


def test_full_pipeline_with_no_credentials_and_no_network(project_root,
                                                          monkeypatch):
    for var in CREDENTIAL_ENV_VARS:
        monkeypatch.delenv(var, raising=False)

    def _no_network(*a, **k):
        raise AssertionError("context core attempted a network connection")

    monkeypatch.setattr(socket, "socket", _no_network)
    monkeypatch.setattr(socket, "create_connection", _no_network)

    src = project_root / "t.txt"
    src.write_text(TRANSCRIPT, encoding="utf-8")
    r1 = compile_to_dir(str(src), str(project_root / "a"), goal="g",
                        token_budget=5000)
    compile_to_dir(str(src), str(project_root / "b"), goal="g",
                   token_budget=5000)
    report = verify.verify_dir(str(project_root / "a"))
    d = diff_mod.diff_paths(str(project_root / "a"), str(project_root / "b"))
    assert report["verdict"] != "UNSAFE TO RESUME"
    assert d["sections"] == {}
    assert not r1.refused


def test_capsule_and_resume_are_provider_neutral(project_root):
    src = project_root / "t.txt"
    src.write_text(TRANSCRIPT, encoding="utf-8")
    result = compile_to_dir(str(src), str(project_root / "out"), goal="g",
                            token_budget=5000)
    # No required field names any provider; model fields are null by default.
    cf = result.capsule["compiled_for"]
    assert cf["source_model"] is None and cf["target_model"] is None
    blob = (result.resume_md + str(sorted(result.capsule))).lower()
    for provider in ("anthropic", "openai", "claude", "gpt-", "gemini",
                     "fable", "opus"):
        assert provider not in blob, (
            f"provider term {provider!r} leaked into a neutral artifact")


def test_cross_model_flow_source_and_consumer_may_differ(project_root):
    """A transcript attributed to one model compiles into a capsule that is
    identical in substance for any consumer; provenance is metadata only."""
    src = project_root / "t.txt"
    src.write_text(TRANSCRIPT, encoding="utf-8")
    a = compile_to_dir(str(src), str(project_root / "a"), goal="g",
                       token_budget=5000, source_model="model-alpha")
    b = compile_to_dir(str(src), str(project_root / "b"), goal="g",
                       token_budget=5000, source_model="model-beta",
                       target_model="model-gamma")
    assert a.capsule["decisions"] == b.capsule["decisions"]
    assert a.capsule["mission"] == b.capsule["mission"]
    assert a.capsule["next_action"] == b.capsule["next_action"]
    assert a.resume_md == b.resume_md  # the packet itself is model-independent


def test_behavioral_equivalence_stays_unmeasured_everywhere(project_root):
    src = project_root / "t.txt"
    src.write_text(TRANSCRIPT, encoding="utf-8")
    result = compile_to_dir(str(src), str(project_root / "out"), goal="g",
                            token_budget=5000)
    assert result.capsule["risk"]["behavioral_equivalence"] == "UNMEASURED"
    assert result.verification["behavioral_equivalence"] == "UNMEASURED"
    assert "UNMEASURED" in result.resume_md
    report = verify.verify_dir(str(project_root / "out"))
    assert report["checks"]["behavioral_equivalence"]["status"] == "UNMEASURED"


@pytest.mark.parametrize("style,path", [
    ("posix", "src/pkg/module.py"),
    ("windows", "C:\\repo\\src\\module.py"),
])
def test_paths_survive_both_styles(project_root, style, path):
    src = project_root / "t.txt"
    src.write_text(f"ARTIFACT: {path}\nNEXT ACTION: open it.\n",
                   encoding="utf-8")
    result = compile_to_dir(str(src), str(project_root / style), goal="g",
                            token_budget=5000)
    assert path in result.resume_md
    arts = [r["content"] for r in result.capsule["active_artifacts"]]
    assert arts == [path]
