"""piensalo.evidence — mechanism records with honest evidence levels.

Every mechanism the pack ships (a rule, a skill, a selector constant) is
supposed to carry a record of what it is intended to do, how it was
tested, what confounds are known, and the next experiment that could kill
it. ``records`` defines the schema and a loader for EVIDENCE.md files
that embed the records as fenced JSON blocks.
"""
from piensalo.evidence.records import (
    EVIDENCE_LEVELS,
    MechanismRecord,
    load_evidence_file,
)

__all__ = ["MechanismRecord", "EVIDENCE_LEVELS", "load_evidence_file"]
