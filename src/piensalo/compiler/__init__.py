"""piensalo.compiler — turn a task into an executable cognitive program.

Given task text and a selection of core operations, the compiler produces
(a) concise prose instructions, (b) a structured JSON packet, and (c) a
rendered prompt suitable for manual copy/paste into any model. Compilation
is fully offline and deterministic — no model is called.
"""
from piensalo.compiler.program import compile_program, select_operations

__all__ = ["compile_program", "select_operations"]
