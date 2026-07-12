"""piensalo.cli — the ``piensalo`` / ``fablethink`` command line.

All subcommands run offline by default; a model is only ever called when
an adapter is explicitly configured. See ``main`` for the subcommand map.
"""
from piensalo.cli.main import main

__all__ = ["main"]
