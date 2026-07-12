"""Mechanism-record schema and EVIDENCE.md loader.

A mechanism record is the unit of honesty in this project: any shipped
mechanism (rule, skill, constant, prompt fragment) carries a structured
statement of what it claims to do and what evidence backs the claim —
including negative-transfer observations, known confounds, and the next
experiment that could falsify it. Records live in EVIDENCE.md files as
front-embedded fenced JSON blocks (```json ... ```), so the same file is
readable prose and machine-loadable data.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

EVIDENCE_LEVELS = (
    "DESIGNED",  # derived from documented failure modes; untested
    "ANECDOTAL",  # observed working, no controlled comparison
    "DEV_VALIDATED",  # validated on a development split only
    "EXPERIMENTALLY_TESTED",  # controlled experiment, n stated in trials
    "REPLICATED",  # independently reproduced
)

_JSON_BLOCK = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)


@dataclass
class MechanismRecord:
    """One mechanism's claim + evidence, in full."""

    mechanism: str
    version: str
    intended_effect: str
    trigger: str
    counterindications: list[str] = field(default_factory=list)
    models_tested: list[str] = field(default_factory=list)
    task_classes: list[str] = field(default_factory=list)
    trials: int = 0
    result: str = ""
    negative_transfer: str = ""
    cost: str = ""
    known_confounds: list[str] = field(default_factory=list)
    evidence_level: str = "DESIGNED"
    verdict: str = ""
    next_kill_test: str = ""

    def __post_init__(self):
        if self.evidence_level not in EVIDENCE_LEVELS:
            raise ValueError(
                f"evidence_level must be one of {EVIDENCE_LEVELS}, "
                f"got {self.evidence_level!r}"
            )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "MechanismRecord":
        known = {f for f in cls.__dataclass_fields__}
        unknown = set(d) - known
        if unknown:
            raise ValueError(f"unknown mechanism-record fields: {sorted(unknown)}")
        return cls(**d)


def load_evidence_file(path: str | Path) -> list[MechanismRecord]:
    """Parse all front-embedded ```json blocks in an EVIDENCE.md file.

    Each block must be a mechanism record object or a list of them.
    Malformed JSON raises immediately — an evidence file that cannot be
    machine-checked is a defect, not a formatting choice.
    """
    text = Path(path).read_text(encoding="utf-8")
    records: list[MechanismRecord] = []
    for m in _JSON_BLOCK.finditer(text):
        data = json.loads(m.group(1))
        items = data if isinstance(data, list) else [data]
        for item in items:
            records.append(MechanismRecord.from_dict(item))
    return records
