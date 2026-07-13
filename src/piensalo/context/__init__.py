"""PIENSALO Context: verified semantic context compilation.

Turn a long coding-agent or research-agent session into the smallest
task-specific continuation packet that preserves critical decisions,
constraints, rejected approaches, exact artifacts, stop conditions, and
the valid next action — then verify that preservation deterministically.

Core principle: AI does not need to remember every word. It needs to
preserve every consequence.

Model-independent by design: the deterministic core (parse, compile,
inspect, verify, diff) requires no model provider, no API key, no network,
and no SDK. Transcripts from any model become capsules consumable by any
model. Behavioral equivalence is UNMEASURED in this MVP — the later
adapter-backed behavioral probes are a separate, optional stage.
"""
from piensalo.context.compiler import CompileError, CompileResult, compile_capsule
from piensalo.context.parser import ParseError
from piensalo.context.schema import (
    DECISION_STATUSES,
    EXACTNESS_CLASSES,
    SCHEMA_VERSION,
    load_capsule,
    validate_capsule,
)

__all__ = [
    "SCHEMA_VERSION",
    "DECISION_STATUSES",
    "EXACTNESS_CLASSES",
    "CompileError",
    "CompileResult",
    "ParseError",
    "compile_capsule",
    "load_capsule",
    "validate_capsule",
]
