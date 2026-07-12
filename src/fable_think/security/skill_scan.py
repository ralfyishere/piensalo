"""Static hygiene scan for skill directories.

Checks a skill directory (markdown instructions plus any assets) for:

- **absolute private paths** — machine-specific paths that leak the
  author's environment and break on every other machine;
- **shell-exec instructions in untrusted text** — skill prose that tells
  the executing model to pipe remote content into a shell, run privileged
  commands, or disable safety checks;
- **URL exfiltration patterns** — instructions to send local data to a
  remote endpoint, or URLs carrying credential-shaped query parameters;
- **symlinks** — a skill directory should be self-contained; links can
  smuggle content from outside the reviewed tree;
- **path traversal** — ``../`` references escaping the skill directory.

The scan is heuristic and precision-oriented: a finding is a reason for a
human to look, not an automatic verdict. Exposed on the CLI as
``fable-think skill scan PATH`` (non-zero exit on findings).
"""
from __future__ import annotations

import re
from pathlib import Path

# Machine-specific absolute path prefixes (POSIX and Windows).
ABS_PATH = re.compile(r"(?<![\w./-])(/Users/[\w.-]+|/home/[\w.-]+|[A-Za-z]:\\Users\\[\w.-]+)")

SHELL_EXEC = [
    (re.compile(r"curl[^\n|]*\|\s*(sudo\s+)?(ba)?sh"), "pipes remote content into a shell"),
    (re.compile(r"wget[^\n|]*\|\s*(sudo\s+)?(ba)?sh"), "pipes remote content into a shell"),
    (re.compile(r"\bsudo\s+rm\b|\brm\s+-rf\s+[/~]"), "destructive privileged delete"),
    (
        re.compile(r"(disable|skip|bypass)[^\n.]{0,40}(sandbox|safety|permission|approval)", re.I),
        "instructs disabling a safety mechanism",
    ),
    (
        re.compile(r"(eval|exec)\s*\(\s*(input|request|response|fetch)", re.I),
        "evaluates untrusted input",
    ),
]

URL_EXFIL = [
    (
        re.compile(r"https?://\S*[?&](token|key|secret|password|credential|auth)=", re.I),
        "URL carries credential-shaped query parameter",
    ),
    (
        re.compile(
            r"(send|post|upload|transmit)[^\n.]{0,60}"
            r"(env|environment variable|credential|secret|api.?key|\.ssh|token)"
            r"[^\n.]{0,60}https?://",
            re.I,
        ),
        "instruction to send local secrets to a remote endpoint",
    ),
]

TRAVERSAL = re.compile(r"(?:^|[\s\"'(=])\.\./(?:\.\./)*")

_TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".py", ".sh"}


def _finding(rel: Path, lineno: int, category: str, detail: str, excerpt: str = "") -> dict:
    return {
        "file": str(rel),
        "line": lineno,
        "category": category,
        "detail": detail,
        "excerpt": excerpt,
    }


def scan_skill_dir(path: str | Path) -> list[dict]:
    """Scan one skill directory; return a list of finding dicts.

    Each finding: ``{"file", "line", "category", "detail", "excerpt"}``.
    An empty list means no findings (not a guarantee of safety).
    """
    root = Path(path)
    if not root.exists():
        raise FileNotFoundError(f"skill path does not exist: {root}")
    findings: list[dict] = []

    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if p.is_symlink():
            findings.append(_finding(rel, 0, "symlink", f"symlink to {p.resolve()}"))
            continue
        if not p.is_file() or p.suffix.lower() not in _TEXT_SUFFIXES:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            excerpt = line.strip()[:160]
            m = ABS_PATH.search(line)
            if m:
                findings.append(
                    _finding(
                        rel, lineno, "absolute-path",
                        f"machine-specific path: {m.group(0)}", excerpt,
                    )
                )
            for pat, why in SHELL_EXEC:
                if pat.search(line):
                    findings.append(_finding(rel, lineno, "shell-exec", why, excerpt))
            for pat, why in URL_EXFIL:
                if pat.search(line):
                    findings.append(_finding(rel, lineno, "url-exfil", why, excerpt))
            if TRAVERSAL.search(line):
                findings.append(
                    _finding(
                        rel, lineno, "path-traversal",
                        "reference escapes the skill directory", excerpt,
                    )
                )
    return findings
