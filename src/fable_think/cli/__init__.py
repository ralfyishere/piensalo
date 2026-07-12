"""fable_think.cli — the ``fable-think`` / ``fablethink`` command line.

All subcommands run offline by default; a model is only ever called when
an adapter is explicitly configured. See ``main`` for the subcommand map.
"""
from fable_think.cli.main import main

__all__ = ["main"]
