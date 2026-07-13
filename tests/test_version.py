"""Version must come from package metadata, never a hardcoded string that can
drift from pyproject/PyPI (the 0.1.0-alpha.2 defect: CLI printed 0.1.0.dev0
while PyPI served 0.1.0a2). No tomllib — this test must run on Python 3.10."""
import pathlib
import re
import subprocess
import sys


def _pyproject_version() -> str:
    text = (pathlib.Path(__file__).resolve().parents[1] / "pyproject.toml").read_text()
    # first `version = "..."` under [project]
    m = re.search(r'(?ms)^\[project\].*?^version\s*=\s*"([^"]+)"', text)
    assert m, "could not find [project] version in pyproject.toml"
    return m.group(1)


def test_version_matches_pyproject():
    import piensalo
    assert piensalo.__version__ == _pyproject_version(), (
        f"__version__ {piensalo.__version__} != pyproject {_pyproject_version()} "
        "(version must derive from installed metadata)"
    )


def test_version_command_prints_real_version():
    import piensalo
    out = subprocess.run(
        [sys.executable, "-m", "piensalo", "version"],
        capture_output=True, text=True, check=True).stdout.strip()
    assert out == f"piensalo {piensalo.__version__}"
    assert "dev0" not in out
