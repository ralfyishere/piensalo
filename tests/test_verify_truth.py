"""verify truth report: five buckets, and UNMEASURED never collapses to PASS."""
from __future__ import annotations

import json

from piensalo.cli.main import main

HEADINGS = (
    "DETERMINISTICALLY VERIFIED",
    "CONTRACT VERIFIED",
    "MODEL-ASSISTED CHECK",
    "UNMEASURED",
    "FAILED",
)
VERIFIED_HEADINGS = ("DETERMINISTICALLY VERIFIED", "CONTRACT VERIFIED", "MODEL-ASSISTED CHECK")

TASK = "Quote the total after a 20% then a 15% discount on 340.00. Output TOTAL: <value>."


def _fixtures(root, draft_text, expected="231.20"):
    task = root / "task.md"
    draft = root / "draft.md"
    contract = root / "contract.json"
    task.write_text(TASK, encoding="utf-8")
    draft.write_text(draft_text, encoding="utf-8")
    field = {"name": "TOTAL", "format": "number"}
    if expected is not None:
        field["expected"] = expected
    contract.write_text(
        json.dumps({"required_output_fields": [field]}), encoding="utf-8"
    )
    return task, draft, contract


def _run_verify(task, draft, contract, capsys):
    rc = main(["verify", "--task", str(task), "--draft", str(draft),
               "--contract", str(contract)])
    return rc, capsys.readouterr().out


def _sections(out: str) -> dict[str, list[str]]:
    """Parse the truth report into {heading: [content lines]}."""
    report = out.split("TRUTH REPORT", 1)[1]
    sections: dict[str, list[str]] = {}
    current = None
    for line in report.splitlines():
        if line.strip() in HEADINGS and not line.startswith(" "):
            current = line.strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return sections


def test_all_five_headings_present(project_root, capsys):
    fx = _fixtures(project_root, "TOTAL: 231.20\n")
    rc, out = _run_verify(*fx, capsys)
    assert rc == 0
    secs = _sections(out)
    for h in HEADINGS:
        assert h in secs, h


def test_correct_value_is_deterministically_verified(project_root, capsys):
    fx = _fixtures(project_root, "TOTAL: 231.20\n")
    rc, out = _run_verify(*fx, capsys)
    assert rc == 0
    secs = _sections(out)
    assert any("TOTAL: 231.20 == expected 231.20" in ln
               for ln in secs["DETERMINISTICALLY VERIFIED"])
    assert any("contract field present: TOTAL" in ln for ln in secs["CONTRACT VERIFIED"])
    assert all("(none)" in ln or not ln.strip() for ln in secs["FAILED"])


def test_wrong_value_lands_in_failed(project_root, capsys):
    fx = _fixtures(project_root, "TOTAL: 221.00\n")
    rc, out = _run_verify(*fx, capsys)
    assert rc == 1
    secs = _sections(out)
    assert any("TOTAL: 221.00 != expected 231.20" in ln for ln in secs["FAILED"])
    assert not any("221.00" in ln for ln in secs["DETERMINISTICALLY VERIFIED"])


def test_missing_contract_field_lands_in_failed(project_root, capsys):
    fx = _fixtures(project_root, "some prose with no required line\n")
    rc, out = _run_verify(*fx, capsys)
    assert rc == 1
    secs = _sections(out)
    assert any("contract field missing: TOTAL" in ln for ln in secs["FAILED"])
    assert not any("TOTAL" in ln for ln in secs["CONTRACT VERIFIED"])


def test_cognition_is_explicitly_unmeasured_never_a_pass(project_root, capsys):
    for draft in ("TOTAL: 231.20\n", "TOTAL: 221.00\n", "no line at all\n"):
        fx = _fixtures(project_root, draft)
        rc, out = _run_verify(*fx, capsys)
        secs = _sections(out)
        assert any(
            "cognition: UNMEASURED (no verifier configured — this is not a pass)" in ln
            for ln in secs["UNMEASURED"]
        )
        # UNMEASURED content never appears under any verified heading.
        for h in VERIFIED_HEADINGS:
            assert not any("UNMEASURED" in ln for ln in secs[h]), (h, draft)


def test_presence_only_contract_has_no_deterministic_claims(project_root, capsys):
    fx = _fixtures(project_root, "TOTAL: 999.99\n", expected=None)
    rc, out = _run_verify(*fx, capsys)
    assert rc == 0  # presence-only contract: nothing failed, value not judged
    secs = _sections(out)
    assert secs["DETERMINISTICALLY VERIFIED"][0].strip() == "(none)"
    assert any("contract field present: TOTAL" in ln for ln in secs["CONTRACT VERIFIED"])
