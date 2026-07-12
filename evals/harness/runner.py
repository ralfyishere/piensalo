#!/usr/bin/env python3
"""Piénsalo public eval harness — condition runner.

Design invariants (non-negotiable):
- The model's workspace for a task contains ONLY task.md + public-context/.
  Graders, keys, probes, meta and contracts never enter a workspace.
- Graders are FROZEN per run: their SHA-256 digests are recorded in the run
  manifest before the first cell executes, and grading uses those files.
- Provider stubs (quota/API-error text) are recorded as NOT_RUN — never
  graded as failures.
- Requested AND resolved model ids are recorded per cell; with
  model.assert_resolved=true, a mismatch marks the cell MODEL_MISMATCH and
  excludes it from analysis.
- Every run appends to the task-consumption ledger
  (evals/results/consumption-ledger.json): a task exposed to a model is
  consumed for that model family.

Conditions (each is a prompt-construction function):
  first pass:  bare | portable-skill | minimal-core | full-program
  second pass (paired on the same trial's bare draft):
               output-guardian | oracle-repair | adaptive-repair |
               verify-only | no-repair-control

Adapters: piensalo.adapters (if the package is installed) -> claude CLI
(`claude -p --output-format json`) -> manual (prompts are written to
pending-prompts/, answers are read from an answers dir). `--smoke` runs the
manual adapter end-to-end with answers auto-populated from probe files: it
exercises workspace build, prompt construction, pairing, stub policy,
grading, the ledger and analysis WITHOUT any API — it is a plumbing test,
not a benchmark.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
EVALS = os.path.abspath(os.path.join(HERE, ".."))
DEFAULT_TASK_ROOT = os.path.join(EVALS, "public-tasks")
RESULTS = os.path.join(EVALS, "results")
LEDGER = os.path.join(RESULTS, "consumption-ledger.json")

STUB_RE = re.compile(r"hit your session limit|session limit|quota|rate limit|"
                     r"usage limit|too many requests|API Error|overloaded_error",
                     re.I)


class MissingAsset(Exception):
    pass


# ---------------------------------------------------------------- conditions

def _asset_text(assets, key):
    path = assets.get(key)
    if not path:
        raise MissingAsset("config assets.%s not set" % key)
    path = os.path.normpath(os.path.join(HERE, path)) if not os.path.isabs(path) else path
    if not os.path.exists(path):
        raise MissingAsset("config assets.%s -> %s not found" % (key, path))
    return open(path).read()


def _repair_text(assets, name):
    root = assets.get("micro_skills_dir")
    if not root:
        raise MissingAsset("config assets.micro_skills_dir not set")
    root = os.path.normpath(os.path.join(HERE, root)) if not os.path.isabs(root) else root
    for cand in (os.path.join(root, name + ".md"),
                 os.path.join(root, name, "SKILL.md")):
        if os.path.exists(cand):
            return open(cand).read()
    raise MissingAsset("repair '%s' not found under %s" % (name, root))


def _repair_menu(assets):
    root = assets.get("micro_skills_dir")
    if not root:
        return []
    root = os.path.normpath(os.path.join(HERE, root)) if not os.path.isabs(root) else root
    if not os.path.isdir(root):
        return []
    names = []
    for e in sorted(os.listdir(root)):
        if e.endswith(".md"):
            names.append(e[:-3])
        elif os.path.isdir(os.path.join(root, e)):
            names.append(e)
    return names


def cond_bare(task_text, contract, assets, draft=None, meta=None):
    return task_text


def cond_portable_skill(task_text, contract, assets, draft=None, meta=None):
    return ("Follow this skill while solving the task.\n\n=== SKILL ===\n"
            + _asset_text(assets, "portable_skill")
            + "\n\n=== TASK ===\n" + task_text)


def cond_minimal_core(task_text, contract, assets, draft=None, meta=None):
    return ("Operate under these core working rules.\n\n=== RULES ===\n"
            + _asset_text(assets, "minimal_core")
            + "\n\n=== TASK ===\n" + task_text)


def cond_full_program(task_text, contract, assets, draft=None, meta=None):
    return ("Operate under this full program.\n\n=== PROGRAM ===\n"
            + _asset_text(assets, "full_program")
            + "\n\n=== TASK ===\n" + task_text)


def cond_output_guardian(task_text, contract, assets, draft, meta=None):
    return ("Your first attempt at the task is below.\n\n=== FIRST ATTEMPT ===\n"
            + draft +
            "\n\nCheck it against the OUTPUT CONTRACT only. Do NOT change any "
            "values, picks or conclusions; fix format only, so that every "
            "required field line is present and exact.\n\n=== OUTPUT CONTRACT ===\n"
            + contract + "\n\n=== TASK ===\n" + task_text +
            "\n\nEmit the corrected final answer only.")


def cond_oracle_repair(task_text, contract, assets, draft, meta):
    repairs = (meta or {}).get("oracle_repairs") or []
    if not repairs:
        return None  # oracle says: no repair warranted -> reuse bare draft
    bodies = "\n\n".join(_repair_text(assets, r) for r in repairs)
    return ("Your first attempt at the task is below.\n\n=== FIRST ATTEMPT ===\n"
            + draft + "\n\nApply ONLY this repair:\n\n" + bodies +
            "\n\nThen give the corrected final answer.\n\n=== TASK ===\n"
            + task_text)


def cond_adaptive_repair(task_text, contract, assets, draft, meta=None):
    menu = _repair_menu(assets)
    menu_txt = "\n".join("- " + m for m in menu) if menu else "(no repairs available)"
    return ("Your first attempt at the task is below.\n\n=== FIRST ATTEMPT ===\n"
            + draft +
            "\n\nDiagnose the attempt against the task. Select AT MOST ONE "
            "repair from the menu below — select NONE if the attempt already "
            "handles the task's constraints (an unnecessary repair can make "
            "the answer worse). State the selection on a line "
            "`REPAIR_SELECTED: <name|none>`, apply it if selected, then give "
            "the final answer.\n\n=== REPAIR MENU ===\n" + menu_txt +
            "\n\n=== TASK ===\n" + task_text)


def cond_verify_only(task_text, contract, assets, draft, meta=None):
    return ("Your first attempt at the task is below.\n\n=== FIRST ATTEMPT ===\n"
            + draft +
            "\n\nRe-derive the answer independently from the task statement, "
            "without assuming the first attempt is right. If the re-derivation "
            "disagrees, trust the re-derivation. Then give the final answer in "
            "the task's required format.\n\n=== TASK ===\n" + task_text)


def cond_no_repair_control(task_text, contract, assets, draft, meta=None):
    return ("Your first attempt at the task is below.\n\n=== FIRST ATTEMPT ===\n"
            + draft +
            "\n\nReview it and restate your final answer in the task's "
            "required format. Do not apply any new methods.\n\n=== TASK ===\n"
            + task_text)


CONDITIONS = {
    "bare": (1, cond_bare),
    "portable-skill": (1, cond_portable_skill),
    "minimal-core": (1, cond_minimal_core),
    "full-program": (1, cond_full_program),
    "output-guardian": (2, cond_output_guardian),
    "oracle-repair": (2, cond_oracle_repair),
    "adaptive-repair": (2, cond_adaptive_repair),
    "verify-only": (2, cond_verify_only),
    "no-repair-control": (2, cond_no_repair_control),
}


# ---------------------------------------------------------------- adapters

def adapter_piensalo(cfg):
    try:
        from piensalo import adapters  # type: ignore
    except ImportError:
        return None

    def complete(prompt, ws):
        t0 = time.time()
        out = adapters.complete(prompt, model=cfg["model"]["requested"], cwd=ws)
        return {"answer": out.get("text", ""),
                "resolved": out.get("model", "not_visible"),
                "tokens": out.get("tokens", 0),
                "wall": round(time.time() - t0, 1),
                "status": "OK"}
    return complete


def adapter_claude_cli(cfg):
    if not shutil.which("claude"):
        return None

    def complete(prompt, ws):
        t0 = time.time()
        p = subprocess.run(
            ["claude", "-p", "--output-format", "json",
             "--model", cfg["model"]["requested"]],
            input=prompt, capture_output=True, text=True, cwd=ws,
            timeout=cfg.get("cell_timeout_s", 600))
        wall = round(time.time() - t0, 1)
        try:
            d = json.loads(p.stdout)
        except Exception:
            return {"answer": "", "resolved": "not_visible", "tokens": 0,
                    "wall": wall, "status": "NOT_RUN",
                    "note": "unparseable CLI output: " + (p.stdout or p.stderr)[:200]}
        answer = d.get("result", "") or ""
        mu = d.get("modelUsage") or {}
        resolved = ";".join(mu.keys()) if mu else "not_visible"
        toks = sum((u.get("inputTokens") or 0) + (u.get("outputTokens") or 0)
                   for u in mu.values())
        status = "OK"
        if d.get("is_error") and STUB_RE.search(json.dumps(d)):
            status = "NOT_RUN"
        return {"answer": answer, "resolved": resolved, "tokens": toks,
                "wall": wall, "status": status}
    return complete


def adapter_manual(cfg, run_dir, answers_dir):
    pending = os.path.join(run_dir, "pending-prompts")
    os.makedirs(pending, exist_ok=True)

    def complete_named(cell_id):
        def complete(prompt, ws):
            apath = os.path.join(answers_dir, cell_id + ".md") if answers_dir else None
            if apath and os.path.exists(apath):
                return {"answer": open(apath).read(),
                        "resolved": "manual", "tokens": 0, "wall": 0,
                        "status": "OK"}
            open(os.path.join(pending, cell_id + ".prompt.md"), "w").write(prompt)
            return {"answer": "", "resolved": "manual", "tokens": 0, "wall": 0,
                    "status": "PENDING"}
        return complete
    return complete_named


# ---------------------------------------------------------------- plumbing

def load_config(path):
    cfg = {
        "model": {"requested": "manual", "assert_resolved": False},
        "adapter": "auto",
        "task_root": os.path.relpath(DEFAULT_TASK_ROOT, HERE),
        "tasks": "all",
        "conditions": ["bare"],
        "trials": 1,
        "assets": {},
        "answers_dir": None,
        "smoke_tasks": ["dev-01-bill-split", "dev-08-incident-record"],
    }
    if path and os.path.exists(path):
        cfg.update(json.load(open(path)))
    return cfg


def task_list(cfg, task_root):
    if cfg["tasks"] == "all":
        return [d for d in sorted(os.listdir(task_root))
                if os.path.isdir(os.path.join(task_root, d))]
    return list(cfg["tasks"])


def build_ws(task_root, task):
    """Fresh workspace with ONLY task.md + public-context/."""
    ws = tempfile.mkdtemp(prefix="ftv_%s_" % task)
    tdir = os.path.join(task_root, task)
    shutil.copy(os.path.join(tdir, "task.md"), os.path.join(ws, "task.md"))
    pc = os.path.join(tdir, "public-context")
    if os.path.isdir(pc):
        shutil.copytree(pc, os.path.join(ws, "public-context"))
    return ws


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def grade(task_root, task, answer_path, out_path):
    grader = os.path.join(task_root, task, "hidden-grader", "grade.py")
    p = subprocess.run(["python3", grader, answer_path],
                       capture_output=True, text=True)
    verdict = None
    for line in reversed(p.stdout.strip().splitlines() or []):
        line = line.strip()
        if line.startswith("{"):
            try:
                verdict = json.loads(line)
            except Exception:
                pass
            break
    if verdict is None:
        verdict = {"error": "unparseable grader output",
                   "failure_layer": "harness",
                   "stdout": p.stdout[:500], "stderr": p.stderr[:500]}
    open(out_path, "w").write(json.dumps(verdict, indent=1))
    return verdict


def append_ledger(entry):
    os.makedirs(RESULTS, exist_ok=True)
    ledger = []
    if os.path.exists(LEDGER):
        try:
            ledger = json.load(open(LEDGER))
        except Exception:
            ledger = []
    ledger.append(entry)
    open(LEDGER, "w").write(json.dumps(ledger, indent=2))


def meter_row(run_dir, cell, requested, resolved, status, wall, tokens, nbytes):
    path = os.path.join(run_dir, "meter.tsv")
    new = not os.path.exists(path)
    with open(path, "a") as f:
        if new:
            f.write("cell\trequested_model\tresolved_model\tstatus\twall_s\ttokens\tbytes\n")
        f.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n"
                % (cell, requested, resolved, status, wall, tokens, nbytes))


# ---------------------------------------------------------------- main run

def run(cfg, run_id, smoke=False):
    task_root = cfg["task_root"]
    if not os.path.isabs(task_root):
        task_root = os.path.normpath(os.path.join(HERE, task_root))

    run_dir = os.path.join(RESULTS, "runs", run_id)
    cells_dir = os.path.join(run_dir, "cells")
    grades_dir = os.path.join(run_dir, "grades")
    for d in (cells_dir, grades_dir):
        os.makedirs(d, exist_ok=True)

    tasks = cfg["smoke_tasks"] if smoke else task_list(cfg, task_root)
    conds = ["bare", "verify-only"] if smoke else list(cfg["conditions"])
    trials = 1 if smoke else int(cfg["trials"])
    # second-pass conditions need the same trial's bare draft
    if any(CONDITIONS[c][0] == 2 for c in conds) and "bare" not in conds:
        conds = ["bare"] + conds

    answers_dir = cfg.get("answers_dir")
    if smoke:
        # Auto-populate a manual answers dir from probe files: bare gets the
        # decorated-correct probe, second passes get clean-correct. Plumbing
        # test only — NOT model output, NOT a benchmark.
        answers_dir = os.path.join(run_dir, "smoke-answers")
        os.makedirs(answers_dir, exist_ok=True)
        for t in tasks:
            probes = os.path.join(task_root, t, "probes")
            for c in conds:
                src = "decorated-correct.md" if c == "bare" else "clean-correct.md"
                shutil.copy(os.path.join(probes, src),
                            os.path.join(answers_dir, "%s.%s.t1.md" % (t, c)))

    requested = cfg["model"]["requested"]
    adapter_name = "manual" if smoke else cfg["adapter"]
    named_adapter = None
    adapter = None
    if adapter_name in ("auto", "piensalo"):
        adapter = adapter_piensalo(cfg)
        if adapter:
            adapter_name = "piensalo"
    if adapter is None and adapter_name in ("auto", "claude_cli"):
        adapter = adapter_claude_cli(cfg)
        if adapter:
            adapter_name = "claude_cli"
    if adapter is None:
        adapter_name = "manual"
        named_adapter = adapter_manual(cfg, run_dir, answers_dir)

    # freeze graders: record digests before any cell runs
    grader_shas = {t: sha256(os.path.join(task_root, t, "hidden-grader", "grade.py"))
                   for t in tasks}
    lib = os.path.join(EVALS, "graders", "layered_common.py")
    manifest = {
        "run_id": run_id, "smoke": smoke,
        "date": datetime.datetime.now().isoformat(timespec="seconds"),
        "adapter": adapter_name,
        "model_requested": requested,
        "assert_resolved": bool(cfg["model"].get("assert_resolved")),
        "tasks": tasks, "conditions": conds, "trials": trials,
        "grader_sha256": grader_shas,
        "layered_common_sha256": sha256(lib),
    }
    open(os.path.join(run_dir, "manifest.json"), "w").write(json.dumps(manifest, indent=2))

    statuses = {}
    for task in tasks:
        tdir = os.path.join(task_root, task)
        task_text = open(os.path.join(tdir, "task.md")).read()
        contract = open(os.path.join(tdir, "contract.json")).read()
        meta_p = os.path.join(tdir, "hidden-grader", "meta.json")
        meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
        for trial in range(1, trials + 1):
            ws = build_ws(task_root, task)
            try:
                drafts = {}
                for cond in conds:
                    npass, builder = CONDITIONS[cond]
                    cell = "%s.%s.t%d" % (task, cond, trial)
                    if npass == 2:
                        draft = drafts.get("bare")
                        if draft is None:
                            statuses[cell] = "SKIPPED_NO_DRAFT"
                            continue
                        try:
                            prompt = builder(task_text, contract, cfg["assets"],
                                             draft, meta)
                        except MissingAsset as e:
                            statuses[cell] = "SKIPPED_MISSING_ASSET"
                            meter_row(run_dir, cell, requested, "-",
                                      "SKIPPED_MISSING_ASSET: %s" % e, 0, 0, 0)
                            continue
                        if prompt is None:  # oracle abstains -> reuse draft
                            open(os.path.join(cells_dir, cell + ".md"), "w").write(draft)
                            statuses[cell] = "OK_REUSED_BARE"
                            meter_row(run_dir, cell, requested, "reuse_bare",
                                      "OK_REUSED_BARE", 0, 0, len(draft.encode()))
                            grade(task_root, task,
                                  os.path.join(cells_dir, cell + ".md"),
                                  os.path.join(grades_dir, cell + ".json"))
                            continue
                    else:
                        try:
                            prompt = builder(task_text, contract, cfg["assets"],
                                             None, meta)
                        except MissingAsset as e:
                            statuses[cell] = "SKIPPED_MISSING_ASSET"
                            meter_row(run_dir, cell, requested, "-",
                                      "SKIPPED_MISSING_ASSET: %s" % e, 0, 0, 0)
                            continue

                    fn = named_adapter(cell) if named_adapter else adapter
                    out = fn(prompt, ws)
                    answer = out["answer"]
                    status = out["status"]
                    if status == "OK" and STUB_RE.search(answer) and len(answer.strip()) < 400:
                        status = "NOT_RUN"  # provider stub: never grade as failure
                    if (status == "OK" and cfg["model"].get("assert_resolved")
                            and out["resolved"] not in ("manual", "not_visible")
                            and requested not in out["resolved"]):
                        status = "MODEL_MISMATCH"
                    statuses[cell] = status
                    meter_row(run_dir, cell, requested, out["resolved"], status,
                              out["wall"], out["tokens"], len(answer.encode()))
                    if status != "OK":
                        continue
                    cpath = os.path.join(cells_dir, cell + ".md")
                    open(cpath, "w").write(answer)
                    if cond == "bare":
                        drafts["bare"] = answer
                    grade(task_root, task, cpath,
                          os.path.join(grades_dir, cell + ".json"))
            finally:
                shutil.rmtree(ws, ignore_errors=True)
            print("DONE %s t%d" % (task, trial), flush=True)

    open(os.path.join(run_dir, "statuses.json"), "w").write(json.dumps(statuses, indent=2))
    append_ledger({
        "run_id": run_id,
        "date": manifest["date"],
        "smoke": smoke,
        "model_requested": requested,
        "adapter": adapter_name,
        "tasks": tasks,
        "conditions": conds,
        "trials": trials,
        "note": ("smoke plumbing test; answers came from probe files, not a model"
                 if smoke else
                 "tasks listed here are CONSUMED for this model family"),
    })

    counts = {}
    for s in statuses.values():
        counts[s] = counts.get(s, 0) + 1
    print("RUN %s complete: %s" % (run_id, json.dumps(counts)))
    return run_dir, statuses


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", default=os.path.join(HERE, "config.json"))
    ap.add_argument("--smoke", action="store_true",
                    help="manual-adapter plumbing test over 2 tasks; no API")
    ap.add_argument("--tasks", help="comma-separated task ids (overrides config)")
    ap.add_argument("--conditions", help="comma-separated conditions (overrides config)")
    ap.add_argument("--trials", type=int)
    ap.add_argument("--adapter", choices=["auto", "piensalo", "claude_cli", "manual"])
    ap.add_argument("--answers-dir")
    ap.add_argument("--run-id")
    args = ap.parse_args()

    cfg = load_config(args.config)
    if args.tasks:
        cfg["tasks"] = args.tasks.split(",")
    if args.conditions:
        cfg["conditions"] = args.conditions.split(",")
    if args.trials:
        cfg["trials"] = args.trials
    if args.adapter:
        cfg["adapter"] = args.adapter
    if args.answers_dir:
        cfg["answers_dir"] = os.path.abspath(args.answers_dir)

    unknown = [c for c in cfg["conditions"] if c not in CONDITIONS]
    if unknown:
        sys.exit("unknown conditions: %s (known: %s)"
                 % (unknown, ", ".join(CONDITIONS)))

    run_id = args.run_id or datetime.datetime.now().strftime(
        "%Y%m%d-%H%M%S") + ("-smoke" if args.smoke else "")
    run_dir, statuses = run(cfg, run_id, smoke=args.smoke)

    # analysis over whatever completed
    subprocess.run(["python3", os.path.join(HERE, "analyze.py"),
                    "--run", run_dir], check=False)

    pending = [c for c, s in statuses.items() if s == "PENDING"]
    if pending:
        print("PENDING cells (%d): prompts in %s/pending-prompts/; provide "
              "answers as <cell>.md via --answers-dir and re-run with the "
              "same --run-id" % (len(pending), run_dir))
        sys.exit(2)
    if args.smoke:
        graded = len([s for s in statuses.values()
                      if s in ("OK", "OK_REUSED_BARE")])
        if graded != len(statuses) or graded == 0:
            sys.exit("SMOKE FAILED: statuses %s" % json.dumps(statuses))
        print("SMOKE OK: %d cells graded end-to-end (probe-sourced answers)" % graded)


if __name__ == "__main__":
    main()
