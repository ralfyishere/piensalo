"""fable_think.inspect — observable-defect scanning of real drafts.

Implements the post-draft half of the core thesis: inspect what was
actually produced and repair only what is demonstrably wrong. See
``scanner`` for the defect inventory and the precision-first selector.
"""
from fable_think.inspect.scanner import pretask_triggers, scan

__all__ = ["scan", "pretask_triggers"]
