"""piensalo — a cognitive operating layer for AI models.

The package provides a small, stdlib-only toolkit built around one thesis:
attempt first, inspect the observable draft, repair only a demonstrated
defect, and verify in layers. It ships a cognitive core (11 named
operations), a compiler that turns a task into an executable cognitive
program, a bounded loop controller with model provenance, an
observable-defect scanner with a precision-first repair selector, a repair
library of micro-skills, layered verification, and optional model adapters
that are never imported by the core.
"""

try:  # single source of truth: the installed package metadata (pyproject)
    from importlib.metadata import PackageNotFoundError, version as _version

    __version__ = _version("piensalo")
except (ImportError, PackageNotFoundError):  # not installed (e.g. raw source tree)
    __version__ = "0.0.0+unknown"
