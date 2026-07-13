"""Capsule-to-capsule diff: what changed between two compilations.

Records are identified by their deterministic content-derived ids, so a
changed record surfaces as removed + added — the diff never guesses that
two different texts are "the same decision, edited".
"""
from __future__ import annotations

from piensalo.context import schema

_DIFF_SECTIONS = (
    ("decisions", "decisions"),
    ("invariants", "invariants"),
    ("active_artifacts", "artifacts"),
    ("open_actions", "open_actions"),
    ("stop_conditions", "stop_conditions"),
    ("failed_approaches", "failed_approaches"),
)


def _by_id(capsule: dict, key: str) -> dict[str, dict]:
    return {r["id"]: r for r in capsule[key]}


def _entry(rec: dict) -> dict:
    return {"id": rec["id"], "status": rec["status"], "content": rec["content"]}


def diff_capsules(a: dict, b: dict) -> dict:
    """Structured, machine-readable diff of two valid capsules."""
    out: dict = {
        "capsule_a": a["capsule_id"],
        "capsule_b": b["capsule_id"],
        "sections": {},
    }
    for key, label in _DIFF_SECTIONS:
        ra, rb = _by_id(a, key), _by_id(b, key)
        added = [_entry(rb[i]) for i in rb if i not in ra]
        removed = [_entry(ra[i]) for i in ra if i not in rb]
        superseded = [_entry(rb[i]) for i in rb
                      if i in ra and ra[i]["status"] != "SUPERSEDED"
                      and rb[i]["status"] == "SUPERSEDED"]
        reactivated = [_entry(rb[i]) for i in rb
                       if i in ra and ra[i]["status"] == "SUPERSEDED"
                       and rb[i]["status"] != "SUPERSEDED"]
        status_changed = [
            {"id": i, "from": ra[i]["status"], "to": rb[i]["status"],
             "content": rb[i]["content"]}
            for i in rb
            if i in ra and ra[i]["status"] != rb[i]["status"]
            and not (ra[i]["status"] != "SUPERSEDED"
                     and rb[i]["status"] == "SUPERSEDED")
            and not (ra[i]["status"] == "SUPERSEDED"
                     and rb[i]["status"] != "SUPERSEDED")
        ]
        section = {}
        if added:
            section["added"] = sorted(added, key=lambda e: e["id"])
        if removed:
            section["removed"] = sorted(removed, key=lambda e: e["id"])
        if superseded:
            section["superseded"] = sorted(superseded, key=lambda e: e["id"])
        if reactivated:
            section["reactivated"] = sorted(reactivated, key=lambda e: e["id"])
        if status_changed:
            section["status_changed"] = sorted(status_changed,
                                               key=lambda e: e["id"])
        if section:
            out["sections"][label] = section
    if a["next_action"] != b["next_action"]:
        out["next_action"] = {"a": a["next_action"], "b": b["next_action"]}
    if a["mission"]["objective"] != b["mission"]["objective"]:
        out["objective"] = {"a": a["mission"]["objective"],
                            "b": b["mission"]["objective"]}
    oa = {(o.get("kind"), o.get("preview")) for o in a["known_omissions"]}
    ob = {(o.get("kind"), o.get("preview")) for o in b["known_omissions"]}
    if oa != ob:
        out["omissions"] = {
            "added": sorted(f"[{k}] {p}" for k, p in ob - oa),
            "removed": sorted(f"[{k}] {p}" for k, p in oa - ob),
        }
    if a["risk"]["notes"] != b["risk"]["notes"]:
        out["risk_notes"] = {"a": a["risk"]["notes"], "b": b["risk"]["notes"]}
    out["token_delta"] = {
        "original_tokens_est":
            b["metrics"]["original_tokens_est"] - a["metrics"]["original_tokens_est"],
        "resume_tokens_est":
            b["metrics"]["resume_tokens_est"] - a["metrics"]["resume_tokens_est"],
    }
    return out


def render_diff(diff: dict) -> str:
    """Human-readable terminal rendering of a diff."""
    lines = [f"capsule A: {diff['capsule_a']}", f"capsule B: {diff['capsule_b']}"]
    if not diff["sections"] and "next_action" not in diff \
            and "objective" not in diff and "omissions" not in diff:
        lines.append("no structural changes")
    for label, section in diff["sections"].items():
        lines.append(f"\n{label}:")
        for verb in ("added", "removed", "superseded", "reactivated"):
            for e in section.get(verb, []):
                first = e["content"].split("\n")[0]
                lines.append(f"  {verb:<12} [{e['id']}] {first}")
        for e in section.get("status_changed", []):
            first = e["content"].split("\n")[0]
            lines.append(f"  status       [{e['id']}] {e['from']} -> {e['to']}: {first}")
    if "objective" in diff:
        lines.append(f"\nobjective: {diff['objective']['a']!r} -> "
                     f"{diff['objective']['b']!r}")
    if "next_action" in diff:
        lines.append(f"\nnext action: {diff['next_action']['a']!r} -> "
                     f"{diff['next_action']['b']!r}")
    if "omissions" in diff:
        for o in diff["omissions"]["added"]:
            lines.append(f"  omission added   {o}")
        for o in diff["omissions"]["removed"]:
            lines.append(f"  omission removed {o}")
    td = diff["token_delta"]
    lines.append(f"\ntoken delta (estimates): original "
                 f"{td['original_tokens_est']:+d}, resume "
                 f"{td['resume_tokens_est']:+d}")
    return "\n".join(lines)


def diff_paths(path_a: str, path_b: str) -> dict:
    return diff_capsules(schema.load_capsule(path_a), schema.load_capsule(path_b))
