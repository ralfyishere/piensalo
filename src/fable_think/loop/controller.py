"""Bounded loop controller: bookkeeper + gatekeeper, never a model caller.

Commands (via ``fable-think loop ...``)::

    start GOAL.md          initialize loop state from a goal contract
    session-start [--model MODEL_ID]
                           new-session transition: resets ONLY session-local
                           counters; preserves cycles/queue/traces; --model is
                           an operator-approved attributed handoff
    session-end [reason] [--checkpointed]
                           end the session; regenerate the handoff prompt at
                           the final state
    status                 state + stop-condition evaluation
    step                   open ONE bounded evidence cycle (prints the packet)
    step close OUTCOME.json
                           close the open cycle (gates, traces, next prompt)
    inspect                current cycle + recent traces + candidate archive
    resume                 regenerate + print the execution prompt
    verify-handoff         fail if the prompt's recorded state fingerprint is
                           stale relative to the state file on disk
    stop [reason]          checkpoint and halt the loop

Every action must pass the prompt gate before a cycle opens: it needs a
verifier, a bounded stop condition, success criteria, and must be
evidence-producing and non-duplicative. Model provenance is recorded at
every transition, and a resolved-model switch is a hard stop
(MODEL_SWITCH_STOP): work done under a silently-substituted model is never
counted.

This port is git-free by design: state transitions write JSON checkpoint
snapshots (see ``state.py``) instead of relying on clean-tree gates, and
handoff staleness is detected via a state-file fingerprint instead of a
commit hash.
"""
from __future__ import annotations

import json
import re
import sys

from fable_think.loop.state import (
    LoopPaths,
    jload,
    jsave,
    now,
    provenance_line,
    resolved_model,
    state_fingerprint,
    write_checkpoint,
)

BUDGET_TOKENS = 400_000
BUDGET_WALL_MIN = 90
MAX_CYCLES_PER_SESSION = 3
MAX_PROMOTIONS_PER_SESSION = 1


class LoopError(Exception):
    """Raised for user-facing loop failures; the CLI maps it to exit 1."""


def _die(msg: str) -> None:
    raise LoopError(msg)


# ------------------------------------------------------------- stop checks
def check_stops(paths: LoopPaths, st: dict, at: str) -> list[tuple[str, str]]:
    """Return (id, detail) for every stop condition that is TRUE."""
    hits = []
    if resolved_model(paths) != st.get("driving_model"):
        hits.append(
            (
                "model-switch",
                f"session {resolved_model(paths)} != loop {st.get('driving_model')}",
            )
        )
    if st.get("session_cycles", 0) >= MAX_CYCLES_PER_SESSION and at in ("open", "status"):
        hits.append(("session-cycle-cap", f"{st['session_cycles']} cycles this session"))
    cyc = st.get("open_cycle")
    if cyc and at == "close":
        spent = cyc.get("outcome", {}).get("tokens_spent", 0)
        if spent > cyc.get("budget_tokens", BUDGET_TOKENS):
            hits.append(("cycle-budget-exhausted", f"tokens {spent}"))
    return hits


# ------------------------------------------------------------- prompt gate
def prompt_gate(action: dict, ledger: dict | None) -> tuple[bool, list[str]]:
    """Deterministic checks first, declared answers second."""
    fails = []
    consumed = set()
    for ts in (ledger or {}).get("task_sets", []):
        if ts.get("status") in ("CONSUMED", "BURNED"):
            consumed.add(ts["set"])
    for used in action.get("uses_task_sets", []):
        if used in consumed:
            fails.append(f"relies on consumed task set: {used}")
    for field, msg in [
        ("verifier", "no verifier"),
        ("stop_condition", "no bounded stop condition"),
        ("success_criteria", "no success criteria"),
    ]:
        if not action.get(field):
            fails.append(msg)
    if not action.get("evidence_producing", True):
        fails.append("not evidence-producing")
    if action.get("duplicates_completed"):
        fails.append("duplicates completed work")
    if action.get("requires_held_out"):
        # Held-out actions must ship a COMPLETE executable packet.
        for f in ("uses_task_sets", "read_first", "commands"):
            if not action.get(f):
                fails.append(f"held-out action with empty {f}")
        set_status = {
            ts.get("set"): ts.get("status") for ts in (ledger or {}).get("task_sets", [])
        }
        for u in action.get("uses_task_sets", []):
            if set_status.get(u) != "HELD_OUT":
                fails.append(
                    f"declared task set {u} is not HELD_OUT (status: {set_status.get(u)})"
                )
    return (not fails, fails)


def blocked_reason(st: dict, action: dict, ledger: dict | None) -> str | None:
    """Why a pending action cannot run yet, or None if it can."""
    if action.get("requires_held_out"):
        rem = (ledger or {}).get("held_out_remaining", {})
        needed = action.get("requires_held_out")
        classes = needed if isinstance(needed, list) else list(rem.keys())
        # ALL required classes must have remaining tasks.
        exhausted = [c for c in classes if rem.get(c, 0) <= 0]
        if exhausted:
            return (
                "needs held-out tasks in ALL required classes; exhausted: "
                + ",".join(exhausted)
            )
    for dep in action.get("depends_on", []):
        if not any(a["id"] == dep and a.get("status") == "done" for a in st.get("queue", [])):
            return f"depends on {dep} (not done)"
    return None


# ------------------------------------------------------------- next prompt
def generate_next_prompt(paths: LoopPaths, st: dict) -> str:
    """Regenerate the handoff prompt from canonical state; returns path."""
    ledger = jload(paths.ledger, {})
    q = st.get("queue", [])
    nxt = next(
        (
            a
            for a in q
            if a.get("status") == "pending" and not blocked_reason(st, a, ledger)
        ),
        None,
    )
    blocked = [
        (a["id"], blocked_reason(st, a, ledger))
        for a in q
        if a.get("status") == "pending" and blocked_reason(st, a, ledger)
    ]
    done = [a["id"] for a in q if a.get("status") == "done"]
    fp = state_fingerprint(paths)
    lines: list[str] = []
    add = lines.append
    add(f"# NEXT PROMPT — generated {now()} by fable-think loop from canonical state")
    add("")
    add("## Goal contract")
    add(f"- {st.get('goal')}")
    add("")
    add("## Model requirement")
    add(
        f"- The driving session MUST be {st.get('driving_model')}; record the resolved "
        "model in .fable-think/session-provenance.json BEFORE work."
    )
    add(
        "- If any safeguard/quota/fallback switches the session model: MODEL_SWITCH_STOP — "
        "save state, write the continuation command, report, exit. Never present "
        "fallback-model work as the driving model's work."
    )
    add("")
    add("## Position")
    add(f"- state-fingerprint: {fp} · loop cycle count: {st.get('cycle_count', 0)}")
    add("")
    add("## Completed queue items (do NOT repeat)")
    for d in done:
        add(f"- {d}")
    add("")
    if nxt:
        add("## NEXT ACTION (selected from the queue, gate-checked)")
        add(f"- id: {nxt['id']}")
        add(f"- title: {nxt.get('title', '')}")
        add(f"- verifier: {nxt.get('verifier')}")
        add(f"- success criteria: {nxt.get('success_criteria')}")
        add(f"- stop condition: {nxt.get('stop_condition')}")
        add("")
        add("### Full execution packet (verbatim queue entry)")
        add("```json")
        add(json.dumps(nxt, indent=2))
        add("```")
    else:
        add("## NEXT ACTION")
        add("- NONE ELIGIBLE. Blocked items and reasons:")
        for bid, why in blocked:
            add(f"  - {bid}: {why}")
    add("")
    add("## Bounds")
    add(
        f"- ONE atomic cycle per `fable-think loop step`; <={MAX_CYCLES_PER_SESSION} "
        f"cycles/session; <={MAX_PROMOTIONS_PER_SESSION} promotion/session; cycle budget "
        f"{BUDGET_TOKENS // 1000}k tokens / {BUDGET_WALL_MIN} min."
    )
    add("")
    add("## Resume command")
    add("```")
    add("fable-think loop resume")
    add("```")
    paths.next_prompt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(paths.next_prompt)


# ---------------------------------------------------------------- commands
def cmd_start(paths: LoopPaths, goal_path: str) -> None:
    existing = jload(paths.state, {})
    if existing.get("open_cycle"):
        _die("a cycle is open; close or stop first")
    from pathlib import Path

    if not Path(goal_path).exists():
        _die(f"goal contract not found: {goal_path}")
    paths.ensure()
    st = {
        "started": now(),
        "goal": goal_path,
        "driving_model": resolved_model(paths),
        "cycle_count": 0,
        "session_cycles": 0,
        "promotions_this_session": 0,
        "open_cycle": None,
        "stopped": None,
        "queue": (jload(paths.queue, {}) or {}).get("queue", []),
    }
    jsave(paths.state, st)
    write_checkpoint(paths, st, "start")
    provenance_line(paths, "loop-start", {"goal": st["goal"], "fingerprint": state_fingerprint(paths)})
    generate_next_prompt(paths, st)
    print(
        f"loop started · driving model {st['driving_model']} · queue "
        f"{len(st['queue'])} items · next-prompt written"
    )


def cmd_session_start(paths: LoopPaths, args: list[str]) -> None:
    """Safe new-session transition: resets ONLY session-local counters.
    Preserves cycle_count, queue statuses, traces, candidates, history.
    Never recreates the queue from queue.json."""
    model_override = None
    if "--model" in args:
        model_override = args[args.index("--model") + 1]
    st = jload(paths.state)
    if not st:
        _die("no loop state — run: fable-think loop start GOAL.md")
    if st.get("open_cycle"):
        _die(
            f"cycle {st['open_cycle']['id']} is open — close or checkpoint it "
            "before session-start"
        )
    prov = jload(paths.session_provenance, {})
    sid = prov.get("session_id", "unknown-session")
    resolved = prov.get("resolved_model", "UNKNOWN")
    if model_override and model_override != resolved:
        _die(
            f"handoff refused: --model {model_override} approved but the session's "
            f"resolved model is {resolved} — never silently switch; fix provenance "
            "or the flag"
        )
    if st.get("session_id") == sid:
        if st.get("session_cycles", 0) == 0:
            generate_next_prompt(paths, st)
            print(
                f"session-start idempotent: session {sid} already initialized at "
                "0 cycles · next-prompt regenerated"
            )
            return
        _die(
            f"refusing to reset a LIVE session: {sid} already has "
            f"{st['session_cycles']} cycle(s) this session"
        )
    prior = st.get("driving_model")
    driving = model_override or resolved
    handoff = driving != prior
    st["session_id"] = sid
    st["driving_model"] = driving
    st["session_cycles"] = 0
    st["promotions_this_session"] = 0
    st["session_started"] = now()
    jsave(paths.state, st)
    write_checkpoint(paths, st, "session-start")
    provenance_line(
        paths,
        "session-start",
        {
            "session_id": sid,
            "requested_model": model_override or prov.get("requested_model", resolved),
            "driving_model": driving,
            "handoff": handoff,
            "prior_driving_model": prior,
        },
    )
    generate_next_prompt(paths, st)
    print(
        f"session {sid} started · driving model {driving}"
        f"{' · HANDOFF (attributed)' if handoff else ''} · counters reset "
        f"(global cycles preserved: {st.get('cycle_count', 0)}) · next-prompt regenerated"
    )


def cmd_session_end(paths: LoopPaths, args: list[str]) -> None:
    reason = " ".join(a for a in args if a != "--checkpointed") or "session end"
    st = jload(paths.state)
    if not st:
        _die("no loop state")
    if st.get("open_cycle") and "--checkpointed" not in args:
        _die(
            f"cycle {st['open_cycle']['id']} still open — close it, or pass "
            "--checkpointed after an explicit checkpoint"
        )
    st["last_session_end"] = {"ts": now(), "reason": reason, "session_id": st.get("session_id")}
    jsave(paths.state, st)
    write_checkpoint(paths, st, "session-end")
    provenance_line(paths, "session-end", {"reason": reason})
    generate_next_prompt(paths, st)
    print(
        f"session ended ({reason}) · next-prompt regenerated at fingerprint "
        f"{state_fingerprint(paths)}\n"
        "resume: fable-think loop session-start && fable-think loop resume"
    )


def cmd_verify_handoff(paths: LoopPaths) -> None:
    """The handoff prompt must reflect the actual saved state."""
    if not paths.next_prompt.exists():
        _die("no next-prompt to verify")
    m = re.search(r"state-fingerprint: (\S+)", paths.next_prompt.read_text(encoding="utf-8"))
    if not m:
        _die("next-prompt records no state fingerprint")
    fp = state_fingerprint(paths)
    if m.group(1) != fp:
        _die(
            f"STALE HANDOFF: prompt fingerprint {m.group(1)} != state {fp} — "
            "regenerate the prompt (loop resume) after the final state change"
        )
    print(f"handoff consistent: prompt fingerprint == state ({fp})")


def cmd_status(paths: LoopPaths) -> None:
    st = jload(paths.state)
    if not st:
        _die("no loop state — run: fable-think loop start GOAL.md")
    hits = check_stops(paths, st, "status")
    print(f"goal: {st.get('goal')}")
    print(
        f"driving model: {st.get('driving_model')} · session resolved: "
        f"{resolved_model(paths)}"
    )
    print(
        f"cycles: total {st.get('cycle_count', 0)} · this session "
        f"{st.get('session_cycles', 0)}/{MAX_CYCLES_PER_SESSION} · promotions "
        f"{st.get('promotions_this_session', 0)}/{MAX_PROMOTIONS_PER_SESSION}"
    )
    oc = st.get("open_cycle")
    print(f"open cycle: {oc['id'] if oc else 'none'}")
    if st.get("stopped"):
        print(f"LOOP STOPPED: {st['stopped']}")
    q = st.get("queue", [])
    print(
        "queue: %d pending · %d done · %d blocked-or-other"
        % (
            sum(1 for a in q if a.get("status") == "pending"),
            sum(1 for a in q if a.get("status") == "done"),
            sum(1 for a in q if a.get("status") not in ("pending", "done")),
        )
    )
    cap = st.get("session_cycles", 0) >= MAX_CYCLES_PER_SESSION
    if cap:
        print(
            f"SESSION CYCLE CAP REACHED ({st.get('session_cycles', 0)}/"
            f"{MAX_CYCLES_PER_SESSION}) — a NEW session runs: fable-think loop session-start"
        )
    other = [h for h in hits if h[0] != "session-cycle-cap"]
    if other:
        print("STOP CONDITIONS TRUE:")
        for h in other:
            print("  - %s: %s" % h)
    elif not cap:
        print("stop conditions: none true")


def cmd_step(paths: LoopPaths, args: list[str]) -> None:
    st = jload(paths.state)
    if not st:
        _die("no loop state — run: fable-think loop start GOAL.md")
    if st.get("stopped"):
        _die(f"loop is stopped ({st['stopped']}); use start after resolving")
    if args and args[0] == "close":
        cmd_step_close(paths, st, args[1] if len(args) > 1 else None)
        return
    if st.get("open_cycle"):
        _die(
            f"cycle {st['open_cycle']['id']} already open — close it: "
            "fable-think loop step close OUTCOME.json"
        )
    hits = check_stops(paths, st, "open")
    if hits:
        for h in hits:
            print("STOP: %s — %s" % h)
        if any(h[0] == "model-switch" for h in hits):
            print("MODEL_SWITCH_STOP")
        raise SystemExit(2)
    ledger = jload(paths.ledger, {})
    action = next(
        (
            a
            for a in st["queue"]
            if a.get("status") == "pending" and not blocked_reason(st, a, ledger)
        ),
        None,
    )
    if not action:
        print("no eligible action. blocked:")
        for a in st["queue"]:
            if a.get("status") == "pending":
                print(f"  - {a['id']}: {blocked_reason(st, a, ledger)}")
        raise SystemExit(3)
    ok, fails = prompt_gate(action, ledger)
    if not ok:
        print(f"PROMPT GATE FAILED for {action['id']}:")
        for f in fails:
            print(f"  - {f}")
        raise SystemExit(4)
    cyc = {
        "id": "cycle-%03d" % (st.get("cycle_count", 0) + 1),
        "opened": now(),
        "action": action["id"],
        "budget_tokens": action.get("budget_tokens", BUDGET_TOKENS),
        "budget_wall_min": action.get("budget_wall_min", BUDGET_WALL_MIN),
        "opened_at_fingerprint": state_fingerprint(paths),
    }
    st["open_cycle"] = cyc
    jsave(paths.state, st)
    write_checkpoint(paths, st, f"open-{cyc['id']}")
    provenance_line(paths, "cycle-open", {"cycle": cyc["id"], "action": action["id"]})
    print(f"=== EXECUTION PACKET {cyc['id']} ===")
    print(json.dumps(action, indent=2))
    print(
        f"=== bounds: {cyc['budget_tokens'] // 1000}k tokens / "
        f"{cyc['budget_wall_min']} min · close with: fable-think loop step close OUTCOME.json ==="
    )


def cmd_step_close(paths: LoopPaths, st: dict, outcome_path: str | None) -> None:
    from pathlib import Path

    cyc = st.get("open_cycle")
    if not cyc:
        _die("no open cycle")
    if not outcome_path or not Path(outcome_path).exists():
        _die("outcome file required: fable-think loop step close OUTCOME.json")
    outcome = jload(Path(outcome_path))
    required = ["result_summary", "evidence_files", "verifier_ran", "tokens_spent"]
    missing = [k for k in required if k not in outcome]
    if missing:
        _die("outcome missing fields: " + ", ".join(missing))
    if not outcome.get("verifier_ran"):
        _die("outcome rejected: verifier did not run (outcome-over-self-report rule)")
    cyc["outcome"] = outcome
    hits = check_stops(paths, st, "close")
    if any(h[0] == "model-switch" for h in hits):
        print("MODEL_SWITCH_STOP — cycle closed as INVALID, work not counted")
        cyc["invalid"] = "model-switch"
    # Candidate archive.
    for cand in outcome.get("candidates", []):
        cid = cand.get("candidate_id") or ("cand-" + now().replace(":", ""))
        cand.setdefault("cycle", cyc["id"])
        jsave(paths.archive / f"{cid}.json", cand)
        if cand.get("disposition") == "promoted":
            st["promotions_this_session"] = st.get("promotions_this_session", 0) + 1
            if st["promotions_this_session"] > MAX_PROMOTIONS_PER_SESSION:
                _die("promotion cap exceeded — archive as PENDING-VALIDATION instead")
    with open(paths.traces, "a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                {
                    "ts": now(),
                    "cycle": cyc["id"],
                    "action": cyc["action"],
                    "result": outcome.get("result_summary", "")[:200],
                    "evidence_files": outcome.get("evidence_files", []),
                }
            )
            + "\n"
        )
    for a in st["queue"]:
        if a["id"] == cyc["action"]:
            a["status"] = outcome.get("action_status", "done")
    st["cycle_count"] = st.get("cycle_count", 0) + 1
    st["session_cycles"] = st.get("session_cycles", 0) + 1
    st["open_cycle"] = None
    st.setdefault("closed_cycles", []).append(cyc)
    jsave(paths.state, st)
    write_checkpoint(paths, st, f"close-{cyc['id']}")
    provenance_line(
        paths,
        "cycle-close",
        {"cycle": cyc["id"], "tokens": outcome.get("tokens_spent"), "invalid": cyc.get("invalid")},
    )
    generate_next_prompt(paths, st)
    print(f"cycle {cyc['id']} closed · checkpoint written · next-prompt regenerated")
    if hits:
        for h in hits:
            print("STOP at close: %s — %s" % h)


def cmd_inspect(paths: LoopPaths) -> None:
    st = jload(paths.state)
    if not st:
        _die("no loop state")
    print(json.dumps({k: v for k, v in st.items() if k != "queue"}, indent=2))
    if paths.traces.exists():
        tail = paths.traces.read_text(encoding="utf-8").splitlines()[-5:]
        print("--- last traces ---")
        for t in tail:
            print(t)
    if paths.archive.is_dir():
        names = sorted(p.name for p in paths.archive.iterdir())
        print("--- candidate archive: %s" % (", ".join(names) or "(empty)"))


def cmd_resume(paths: LoopPaths) -> None:
    st = jload(paths.state)
    if not st:
        _die("no loop state — run: fable-think loop start GOAL.md")
    p = generate_next_prompt(paths, st)
    print(open(p, encoding="utf-8").read())


def cmd_stop(paths: LoopPaths, reason: str) -> None:
    st = jload(paths.state)
    if not st:
        _die("no loop state")
    st["stopped"] = reason or "operator stop"
    if st.get("open_cycle"):
        st["open_cycle"]["aborted"] = now()
        st.setdefault("closed_cycles", []).append(st["open_cycle"])
        st["open_cycle"] = None
    jsave(paths.state, st)
    write_checkpoint(paths, st, "stop")
    provenance_line(paths, "loop-stop", {"reason": st["stopped"]})
    generate_next_prompt(paths, st)
    print(f"loop stopped ({st['stopped']}) · state checkpointed · next-prompt written")


def main(argv: list[str] | None = None) -> int:
    """Entry point for ``fable-think loop ...``; returns an exit code."""
    args = list(sys.argv[1:] if argv is None else argv)
    paths = LoopPaths().ensure()
    if not args:
        print(__doc__)
        return 0
    cmd, rest = args[0], args[1:]
    try:
        if cmd == "start":
            if not rest:
                _die("usage: fable-think loop start GOAL.md")
            cmd_start(paths, rest[0])
        elif cmd == "session-start":
            cmd_session_start(paths, rest)
        elif cmd == "session-end":
            cmd_session_end(paths, rest)
        elif cmd == "status":
            cmd_status(paths)
        elif cmd == "step":
            cmd_step(paths, rest)
        elif cmd == "inspect":
            cmd_inspect(paths)
        elif cmd == "resume":
            cmd_resume(paths)
        elif cmd == "verify-handoff":
            cmd_verify_handoff(paths)
        elif cmd == "stop":
            cmd_stop(paths, " ".join(rest))
        else:
            _die(f"unknown loop command: {cmd}")
    except LoopError as e:
        print(f"fable-think loop: {e}", file=sys.stderr)
        return 1
    return 0
