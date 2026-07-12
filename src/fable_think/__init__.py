"""fable_think — a cognitive operating layer for AI models.

The package provides a small, stdlib-only toolkit built around one thesis:
attempt first, inspect the observable draft, repair only a demonstrated
defect, and verify in layers. It ships a cognitive core (11 named
operations), a compiler that turns a task into an executable cognitive
program, a bounded loop controller with model provenance, an
observable-defect scanner with a precision-first repair selector, a repair
library of micro-skills, layered verification, and optional model adapters
that are never imported by the core.
"""

__version__ = "0.1.0.dev0"
