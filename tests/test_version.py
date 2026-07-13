"""Version must come from package metadata, never a hardcoded string that
can drift from pyproject/PyPI (the v0.1.0-alpha.2 defect: CLI printed
0.1.0.dev0 while PyPI served 0.1.0a2)."""
import subprocess
import sys
import tomllib
import pathlib


def test_version_matches_pyproject():
    root = pathlib.Path(__file__).resolve().parents[1]
    pyproj = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
    import piensalo
    assert piensalo.__version__ == pyproj, (
        f"__version__ {piensalo.__version__} != pyproject {pyproj} "
        "(version must derive from installed metadata)"
    )


def test_version_command_prints_real_version():
    import piensalo
    out = subprocess.run(
        [sys.executable, "-m", "piensalo", "version"],
        capture_output=True, text=True, check=True).stdout.strip()
    assert out == f"piensalo {piensalo.__version__}"
    assert "dev0" not in out
