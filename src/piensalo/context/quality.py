"""Quality verification for optimizer responses.

Strength ladder (strongest available wins, weaker never upgrades):
exact output contract -> deterministic oracle (expected strings/values/
prohibitions) -> executable grader hooks -> blind adapter-backed
comparison -> UNMEASURED. A response is never called quality-preserving
because the optimized prompt "looks good", and a target model judging its
own answer unblinded is labeled weak evidence, never proof.

Verification statuses: STRUCTURALLY VERIFIED · CONTRACT VERIFIED ·
DETERMINISTIC TASK VERIFIED · MODEL-ASSISTED COMPARISON · BEHAVIORALLY
NON-INFERIOR · BEHAVIORALLY IMPROVED · UNMEASURED · REGRESSION.
"""
from __future__ import annotations

import json
from pathlib import Path

from piensalo.context import schema
from piensalo.verify import contract as contract_mod

STATUSES = (
    "STRUCTURALLY VERIFIED",
    "CONTRACT VERIFIED",
    "DETERMINISTIC TASK VERIFIED",
    "MODEL-ASSISTED COMPARISON",
    "BEHAVIORALLY NON-INFERIOR",
    "BEHAVIORALLY IMPROVED",
    "UNMEASURED",
    "REGRESSION",
)


def load_expectations(path: str) -> dict:
    """Load a deterministic oracle file: must_contain / must_not_contain /
    field_values (anchored ``NAME: value`` lines) — all optional."""
    p = Path(path)
    if not p.is_file():
        raise ValueError(f"expectations file not found: {path}")
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"expectations is not valid JSON: {e}") from e
    unknown = set(d) - {"must_contain", "must_not_contain", "field_values",
                        "comment"}
    if unknown:
        raise ValueError(f"unknown expectation keys: {sorted(unknown)}")
    return d


def _values_equal(got, expected) -> bool:
    try:
        return abs(float(str(got).replace(",", ""))
                   - float(str(expected).replace(",", ""))) < 1e-9
    except (ValueError, TypeError):
        return str(got).strip() == str(expected).strip()


def grade(response: str, *, contract: dict | None = None,
          expectations: dict | None = None) -> dict:
    """Deterministic grading. Returns per-requirement results so verdicts
    can compare requirement-by-requirement, never by a single average."""
    requirements: list[dict] = []

    if contract:
        result = contract_mod.check(contract, response)
        for pres in result["present"]:
            requirements.append({"id": f"contract:{pres['field']}",
                                 "kind": "contract", "passed": True})
        for miss in result["missing"]:
            requirements.append({"id": f"contract:{miss['field']}",
                                 "kind": "contract", "passed": False,
                                 "detail": "required field missing"})
    if expectations:
        for needle in expectations.get("must_contain", []):
            requirements.append({
                "id": f"must_contain:{needle[:60]}", "kind": "oracle",
                "passed": needle in response,
                "detail": None if needle in response else
                "required exact content absent"})
        for needle in expectations.get("must_not_contain", []):
            requirements.append({
                "id": f"must_not_contain:{needle[:60]}", "kind": "oracle",
                "passed": needle not in response,
                "detail": None if needle not in response else
                "forbidden content present"})
        from piensalo.verify import layered
        for name, expected in expectations.get("field_values", {}).items():
            got, _ = layered.parse_anchored(response, name)
            ok = got is not None and _values_equal(got, expected)
            requirements.append({
                "id": f"value:{name}", "kind": "oracle", "passed": ok,
                "detail": None if ok else
                f"expected {expected!r}, parsed {got!r}"})

    passed = all(r["passed"] for r in requirements) if requirements else None
    if not requirements:
        status = "UNMEASURED"
    elif not passed:
        status = "REGRESSION-CANDIDATE"  # caller decides vs. counterpart
    elif expectations and any(r["kind"] == "oracle" for r in requirements):
        status = "DETERMINISTIC TASK VERIFIED"
    else:
        status = "CONTRACT VERIFIED"
    return {"passed": passed, "status": status,
            "requirements": requirements,
            "method": "deterministic contract + oracle (no model judge)"}


def compare_verdict(full_grade: dict, optimized_grade: dict,
                    *, optimized_accepted: bool) -> str:
    """Requirement-level comparison. One critical regression is a
    REGRESSION verdict regardless of anything else — never averaged away."""
    if not optimized_accepted:
        return "SAFE FALLBACK"
    if full_grade["passed"] is None or optimized_grade["passed"] is None:
        return "UNMEASURED"
    full_by_id = {r["id"]: r["passed"] for r in full_grade["requirements"]}
    opt_by_id = {r["id"]: r["passed"] for r in optimized_grade["requirements"]}
    regressions = [i for i, p in full_by_id.items()
                   if p and opt_by_id.get(i) is False]
    if regressions:
        return "REGRESSION"
    improvements = [i for i, p in full_by_id.items()
                    if not p and opt_by_id.get(i)]
    new_failures = [i for i, p in opt_by_id.items()
                    if p is False and full_by_id.get(i) is False]
    if improvements and optimized_grade["passed"]:
        return "IMPROVED"
    if optimized_grade["passed"]:
        return "MAINTAINED"
    if new_failures and not improvements:
        # Both failed the same things: not a regression vs full, but not
        # an acceptable optimized success either.
        return "MAINTAINED" if full_grade["passed"] is False else "REGRESSION"
    return "REGRESSION"


JUDGE_PROMPT = """\
You are comparing two anonymous responses to the same task. You do not
know how either was produced. Judge ONLY task quality and correctness.

TASK:
{task}

RESPONSE 1:
{first}

RESPONSE 2:
{second}

Reply with exactly one line: VERDICT: 1 | VERDICT: 2 | VERDICT: TIE
"""


def _parse_judge(text: str) -> str | None:
    for line in text.strip().splitlines():
        line = line.strip().upper()
        if line.startswith("VERDICT:"):
            v = line.split(":", 1)[1].strip()
            if v in ("1", "2", "TIE"):
                return v
    return None


def blind_compare(judge_adapter, *, task: str, full_response: str,
                  optimized_response: str) -> dict:
    """Blind, order-swapped model comparison (weak evidence, labeled).

    The judge never learns which response is which; both orderings run and
    a disagreement between orderings is recorded as such rather than
    resolved silently. Result is MODEL-ASSISTED COMPARISON evidence only —
    it never overrides a deterministic result.
    """
    order_a = judge_adapter.complete(JUDGE_PROMPT.format(
        task=task.strip(), first=full_response, second=optimized_response))
    order_b = judge_adapter.complete(JUDGE_PROMPT.format(
        task=task.strip(), first=optimized_response, second=full_response))
    va, vb = _parse_judge(order_a.text), _parse_judge(order_b.text)
    # Map to full/optimized identity per ordering.
    map_a = {"1": "full", "2": "optimized", "TIE": "tie"}
    map_b = {"1": "optimized", "2": "full", "TIE": "tie"}
    ra = map_a.get(va or "")
    rb = map_b.get(vb or "")
    agreed = ra == rb and ra is not None
    return {
        "kind": "MODEL-ASSISTED COMPARISON",
        "blinded": True,
        "orderings_run": 2,
        "judge_requested_model": judge_adapter.requested_model,
        "judge_resolved_model": order_a.resolved_model,
        "ordering_1_winner": ra,
        "ordering_2_winner": rb,
        "agreed": agreed,
        "winner": ra if agreed else "disagreement",
        "note": "weak evidence: model judgment, not a deterministic oracle; "
                "never overrides deterministic grading",
        "judge_tokens": (order_a.tokens_in + order_a.tokens_out
                         + order_b.tokens_in + order_b.tokens_out),
        "responses_hash": {
            "full": schema.sha256_text(full_response),
            "optimized": schema.sha256_text(optimized_response),
        },
    }
