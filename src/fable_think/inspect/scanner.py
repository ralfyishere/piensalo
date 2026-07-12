"""Draft-grounded failure scanner + precision-first repair selector.

The thesis: attempt first, inspect the OBSERVABLE draft, repair only a
demonstrated defect — this replaces pre-task prescription. The scanner
checks a real draft for observable failure signatures and selects at most
ONE repair micro-skill (two only if the defects are independent and one
repair cannot cover both) using precision-first scoring::

    value = defect_confidence x expected_repair_effectiveness
            - distraction_risk - token_cost - negative_transfer_risk

It never defaults to a repair because all scores are weak. No observable
defect -> NO REPAIR NEEDED (correct abstention is a success, not a
penalty).

The activation constants are experimentally recalibrated: an earlier flat
penalty set summed exactly to the activation threshold and swallowed every
procedural defect's signal (the selector abstained on all of them).
Penalties were halved and the threshold lowered so a genuine mid-confidence
defect (conf ~0.55, repair ~0.65) fires while weak signals still abstain.

Pre-task triggers are DELIBERATELY narrow and high-precision (structural
patterns only, no semantic guessing); everything else waits for the draft.
"""
from __future__ import annotations

import re

from fable_think.verify import contract as _contract

# Recalibrated selector constants (validated on a development split).
DISTRACTION = 0.06
TOKEN_COST = 0.04
NEG_TRANSFER = 0.05
ACTIVATE = 0.15  # value must clear this to select a repair

# Stage 0 — unmistakable STRUCTURAL pre-task triggers only.
PRETASK = [
    (
        "rederive-the-numbers",
        r"compound|compounded|per (month|year|day).{0,40}(over|for)\s+\d+|"
        r"\d+\s*%.{0,30}\d+\s*%",
        "explicit compounding/multi-rate arithmetic",
    ),
    (
        "final-answer-completeness",
        r"exact format|must (be formatted|output|emit).{0,30}(line|field)|"
        r"column 0|verbatim",
        "explicit exact output schema",
    ),
    (
        "contradiction-resolution",
        r"conflict(ing|s)? (with|between)|contradict|"
        r"one (study|source|report) says.{0,60}(another|other)",
        "explicit conflicting evidence",
    ),
    (
        "boundary-case-check",
        r"edge case|boundary|extreme (input|value)|handle .* (empty|zero|negative|max)",
        "explicit boundary requirement",
    ),
    (
        "source-claim-verification",
        r"cite (your )?sources|verify (the )?claim|source-level",
        "explicit citation-verification requirement",
    ),
]

# Post-draft OBSERVABLE defect signatures -> repair skill. Each carries a
# detection-confidence prior and an expected-repair-effectiveness prior
# (evidence-backed repairs score higher).
DEFECTS = [
    {
        "id": "missing-deliverable",
        "skill": "final-answer-completeness",
        "detect": lambda t, d, c: bool(c) and not c.get("all_present"),
        "conf": 0.85,
        "repair": 0.8,
        "evidence": lambda t, d, c: [
            f"contract field missing: {m['field']}" for m in (c or {}).get("missing", [])
        ],
    },
    {
        "id": "number-without-derivation",
        "skill": "rederive-the-numbers",
        "detect": lambda t, d, c: bool(re.search(r"\d[\d,]*\.?\d*", d))
        and bool(re.search(r"compound|%|rate|per (month|year)", t, re.I))
        and not re.search(r"=|\*|step|comput|deriv|\bpython\b", d, re.I),
        "conf": 0.6,
        "repair": 0.7,
        "evidence": lambda t, d, c: [
            "asserts a figure with no visible derivation on a multi-rate task"
        ],
    },
    {
        "id": "unresolved-contradiction",
        "skill": "contradiction-resolution",
        "detect": lambda t, d, c: bool(
            re.search(r"conflict|contradict|one .* another|discrepan", t, re.I)
        )
        and not re.search(r"reconcil|resolv|because .* while|the discrepancy", d, re.I),
        "conf": 0.55,
        "repair": 0.7,
        "evidence": lambda t, d, c: [
            "task flags a contradiction; draft shows no reconciliation"
        ],
    },
    {
        "id": "unchecked-boundary",
        "skill": "boundary-case-check",
        "detect": lambda t, d, c: bool(
            re.search(r"boundary|edge|empty|zero|negative|maximum|all\b", t, re.I)
        )
        and not re.search(r"edge|boundary|empty|zero case|negative case|extreme", d, re.I),
        "conf": 0.5,
        "repair": 0.6,
        "evidence": lambda t, d, c: [
            "boundary-sensitive task; draft tests no extreme input"
        ],
    },
    {
        "id": "ignored-disqualifier",
        "skill": "disqualifier-scan",
        "detect": lambda t, d, c: bool(
            re.search(
                r"must not|cannot|disqualif|prohibited|ineligible|"
                r"(only|unless) .* (if|when)",
                t,
                re.I,
            )
        )
        and not re.search(r"disqualif|rules out|violat|ineligible|excluded because", d, re.I),
        "conf": 0.55,
        "repair": 0.65,
        "evidence": lambda t, d, c: [
            "task has a hard exclusion; draft does not check it"
        ],
    },
    {
        "id": "unsupported-certainty",
        "skill": "calibrated-uncertainty",
        "detect": lambda t, d, c: bool(
            re.search(r"\b(definitely|certainly|obviously|clearly the answer)\b", d, re.I)
        )
        and not re.search(r"uncertain|assum|caveat|however|depends on", d, re.I),
        "conf": 0.4,
        "repair": 0.5,
        "evidence": lambda t, d, c: [
            "confident conclusion with no stated assumption/uncertainty"
        ],
    },
    {
        "id": "analysis-past-done",
        "skill": "complete-the-delivery",
        "detect": lambda t, d, c: len(d) > 4000
        and not re.search(r"final|answer:|conclusion|deliver", d[-800:], re.I),
        "conf": 0.45,
        "repair": 0.6,
        "evidence": lambda t, d, c: [
            "long draft with no final answer near the end"
        ],
    },
]


def pretask_triggers(task: str) -> list[dict]:
    """Stage-0 scan of the task text alone. Returns high-precision
    structural triggers only; semantic judgment waits for the draft."""
    hits = []
    for skill, pattern, why in PRETASK:
        if re.search(pattern, task, re.I):
            hits.append({"skill": skill, "reason": why})
    return hits


def scan(task: str, draft: str, contract: dict | None = None, max_repairs: int = 1) -> dict:
    """Scan a draft for observable defects and select repairs.

    ``contract`` may be a contract-check RESULT (from ``verify.contract.check``),
    a raw contract dict (internal or task-contract form, checked here), or
    None. Returns the defect inventory with ``candidate_scores`` carrying
    per-candidate evidence, and ``no_repair_needed`` when nothing clears the
    activation threshold.
    """
    check_result = _as_check_result(contract, draft)
    cands = []
    for dfx in DEFECTS:
        try:
            if not dfx["detect"](task, draft, check_result):
                continue
        except Exception:
            continue
        conf, rep = dfx["conf"], dfx["repair"]
        value = conf * rep - DISTRACTION - TOKEN_COST - NEG_TRANSFER
        cands.append(
            {
                "skill": dfx["skill"],
                "defect": dfx["id"],
                "observable_evidence": dfx["evidence"](task, draft, check_result),
                "confidence": round(conf, 2),
                "expected_repair": rep,
                "negative_transfer_risk": NEG_TRANSFER,
                "value": round(value, 3),
                "selected": False,
            }
        )
    cands.sort(key=lambda c: -c["value"])
    chosen = [c for c in cands if c["value"] >= ACTIVATE][:max_repairs]
    # A second repair is only kept when it maps to a different skill than
    # the first (independent defects; one repair cannot cover both).
    if len(chosen) == 2 and chosen[1]["skill"] == chosen[0]["skill"]:
        chosen = chosen[:1]
    for c in chosen:
        c["selected"] = True
    return {
        "defects_detected": [c["defect"] for c in cands],
        "selected_repairs": [c["skill"] for c in chosen],
        "no_repair_needed": not chosen,
        "evidence_from_draft": [e for c in chosen for e in c["observable_evidence"]],
        "maximum_repairs": max_repairs,
        "verification_target": chosen[0]["defect"] if chosen else None,
        "candidate_scores": cands,
    }


def _as_check_result(contract: dict | None, draft: str) -> dict | None:
    """Accept a contract in any supported shape and return a check result.

    Raw contracts are converted through ``convert_task_contract`` first —
    skipping the conversion on a task-contract file would validate an empty
    field list and report ``all_present: true`` vacuously, silently
    disabling missing-deliverable detection.
    """
    if contract is None:
        return None
    if "all_present" in contract:  # already a check result
        return contract
    return _contract.check(_contract.convert_task_contract(contract), draft)
