"""Contract-gated repair acceptance: the strongest independent verifier —
never the detector that proposed the repair — judges whether a repair ships.

Root cause (NR-10): repair acceptance keyed on the scanner's own defect count
accepted a "repair" that kept every value intact but fenced the output and
echoed instruction text — delivery damage the output contract saw instantly.

Rules enforced here (deterministic, provider-neutral):

- Before repair, capture the full contract state of the original: missing
  required fields, delivery-format status (extra lines / fences under an
  exact-format contract).
- If the original already fully passes the strongest contract, the repair is
  rejected outright and the verdict is CORRECT_ABSTENTION — the original is
  returned unchanged, byte for byte.
- A repair candidate is accepted only when ALL hold:
    1. at least one demonstrated failure is corrected;
    2. no previously passing required field regresses;
    3. no new delivery violation appears (fences, extra lines under
       exact_format);
    4. the contract verdict strictly improves.
- With no contract available there is no independent verifier: the candidate
  is rejected and the verdict is UNMEASURED (a detector must never be the
  sole judge of its own repair).
"""
from __future__ import annotations

import re

from piensalo.verify import contract as contract_mod

VERDICTS = ("ACCEPTED", "CORRECT_ABSTENTION", "REJECTED_NO_IMPROVEMENT",
            "REJECTED_REGRESSION", "REJECTED_DELIVERY_DAMAGE", "UNMEASURED")

_FENCE = re.compile(r"```")


def _contract_state(contract: dict, text: str) -> dict:
    """Deterministic contract snapshot for one candidate text."""
    res = contract_mod.check(contract, text)
    present = {p["field"] for p in res["present"]}
    missing = {m["field"] for m in res["missing"]}
    state = {"present": present, "missing": missing,
             "fenced": bool(_FENCE.search(text or ""))}
    if contract.get("exact_format"):
        # search(), not match(): mirrors contract.check's own matching so a
        # custom unanchored pattern classifies lines identically here.
        field_pats = [re.compile(f["pattern"]) for f in contract.get("fields", [])]
        extra = 0
        for ln in (text or "").strip().splitlines():
            ln = ln.strip()
            if not ln:
                continue
            if not any(p.search(ln) for p in field_pats):
                extra += 1
        state["extra_lines"] = extra
    else:
        state["extra_lines"] = 0
    state["violations"] = (len(missing) + state["extra_lines"]
                           + (1 if state["fenced"] else 0))
    return state


def evaluate_repair(contract: dict | None, original: str,
                    repaired: str) -> dict:
    """Judge a repair candidate against the original under the contract.

    Returns {"accept", "verdict", "output", "before", "after", "reason"} —
    ``output`` is the text that must ship (the original whenever the repair
    is not accepted).
    """
    if not contract:
        return {
            "accept": False, "verdict": "UNMEASURED", "output": original,
            "before": None, "after": None,
            "reason": ("no independent verifier available: a detector must "
                       "never be the sole judge of its own repair"),
        }
    before = _contract_state(contract, original)
    if before["violations"] == 0:
        return {
            "accept": False, "verdict": "CORRECT_ABSTENTION",
            "output": original,
            "before": _plain(before), "after": None,
            "reason": "original already fully passes the strongest contract",
        }
    after = _contract_state(contract, repaired)
    newly_missing = after["missing"] & before["present"]
    new_delivery = ((after["fenced"] and not before["fenced"])
                    or after["extra_lines"] > before["extra_lines"])
    fixed_something = (len(after["missing"]) < len(before["missing"])
                       or after["extra_lines"] < before["extra_lines"]
                       or (before["fenced"] and not after["fenced"]))
    strictly_better = after["violations"] < before["violations"]

    if newly_missing:
        verdict, accept = "REJECTED_REGRESSION", False
        reason = f"previously passing field(s) regressed: {sorted(newly_missing)}"
    elif new_delivery:
        verdict, accept = "REJECTED_DELIVERY_DAMAGE", False
        reason = "repair introduced fencing or extra lines under the contract"
    elif not fixed_something or not strictly_better:
        verdict, accept = "REJECTED_NO_IMPROVEMENT", False
        reason = "repair does not strictly improve the contract verdict"
    else:
        verdict, accept = "ACCEPTED", True
        reason = (f"violations {before['violations']} -> {after['violations']}; "
                  "no field or delivery regression")
    return {"accept": accept, "verdict": verdict,
            "output": repaired if accept else original,
            "before": _plain(before), "after": _plain(after),
            "reason": reason}


def _plain(state: dict) -> dict:
    return {"missing": sorted(state["missing"]),
            "present": sorted(state["present"]),
            "extra_lines": state["extra_lines"], "fenced": state["fenced"],
            "violations": state["violations"]}
