#!/usr/bin/env python3
"""Piénsalo public eval harness — run analyzer.

Computes, from a run directory produced by runner.py:
- per-condition, per-class score stats (mean/median/stdev);
- paired deltas vs the bare condition (same task, same trial);
- negative transfer (harm vs bare, reported per class — a "boost" that
  hurts competent-baseline tasks is a real cost, not noise);
- cost (tokens per condition, added tokens vs bare);
- variance across trials;
- pass@k and pass^k per condition (pass = final_score == 100 across the
  k = trials attempts of a task).

Cells with status NOT_RUN / PENDING / MODEL_MISMATCH / SKIPPED_* are excluded
from all statistics and counted separately. Small n: report direction, not
certainty.
"""
import argparse
import json
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
EVALS = os.path.abspath(os.path.join(HERE, ".."))


def mean(xs):
    return round(st.mean(xs), 1) if xs else None


def median(xs):
    return round(st.median(xs), 1) if xs else None


def stdev(xs):
    return round(st.stdev(xs), 1) if len(xs) > 1 else 0.0 if xs else None


def latest_run():
    root = os.path.join(EVALS, "results", "runs")
    runs = sorted(os.listdir(root)) if os.path.isdir(root) else []
    if not runs:
        raise SystemExit("no runs found under %s" % root)
    return os.path.join(root, runs[-1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", help="run directory (default: latest)")
    args = ap.parse_args()
    run_dir = args.run or latest_run()

    manifest = json.load(open(os.path.join(run_dir, "manifest.json")))
    task_root = os.path.join(EVALS, "public-tasks")
    grades_dir = os.path.join(run_dir, "grades")
    statuses = {}
    sp = os.path.join(run_dir, "statuses.json")
    if os.path.exists(sp):
        statuses = json.load(open(sp))

    # task classes/labels from meta.json
    klass, label = {}, {}
    for t in manifest["tasks"]:
        mp = os.path.join(task_root, t, "hidden-grader", "meta.json")
        m = json.load(open(mp)) if os.path.exists(mp) else {}
        klass[t] = m.get("class", "unclassified")
        label[t] = m.get("label", "UNKNOWN")

    # tokens from meter.tsv
    tokens = {}
    mt = os.path.join(run_dir, "meter.tsv")
    if os.path.exists(mt):
        for i, line in enumerate(open(mt)):
            if i == 0:
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 6:
                try:
                    tokens[parts[0]] = int(parts[5])
                except ValueError:
                    pass

    # graded cells
    cells = []  # (task, cond, trial, verdict)
    for f in sorted(os.listdir(grades_dir)) if os.path.isdir(grades_dir) else []:
        if not f.endswith(".json"):
            continue
        cell = f[:-5]
        task, cond, tno = cell.rsplit(".", 2)
        v = json.load(open(os.path.join(grades_dir, f)))
        if "final_score" not in v:
            continue
        cells.append((task, cond, int(tno[1:]), v, cell))

    conds = manifest["conditions"]
    trials = manifest["trials"]
    excluded = {}
    for c, s in statuses.items():
        if s not in ("OK", "OK_REUSED_BARE"):
            excluded[s] = excluded.get(s, 0) + 1

    R = {"run_id": manifest["run_id"],
         "model_requested": manifest["model_requested"],
         "adapter": manifest["adapter"],
         "smoke": manifest.get("smoke", False),
         "n_cells_graded": len(cells),
         "excluded_by_status": excluded,
         "note": ("smoke run: answers are probe files, not model output"
                  if manifest.get("smoke") else
                  "small n: report direction, not certainty")}

    classes = sorted(set(klass.values()))
    per = {}
    for cond in conds:
        cx = [x for x in cells if x[1] == cond]
        scores = [v["final_score"] for (_, _, _, v, _) in cx]
        cog = [1 if v["cognitive_correctness"]["pass"] else 0
               for (_, _, _, v, _) in cx
               if v["cognitive_correctness"]["pass"] is not None]
        deliv = [1 if v["failure_layer"] in ("delivery", "rendering") else 0
                 for (_, _, _, v, _) in cx]
        byclass = {}
        for k in classes:
            ks = [v["final_score"] for (t, _, _, v, _) in cx if klass[t] == k]
            byclass[k] = {"mean": mean(ks), "n": len(ks)}
        toks = [tokens[c] for (_, _, _, _, c) in cx if c in tokens]
        per[cond] = {
            "n": len(cx),
            "score_mean": mean(scores), "score_median": median(scores),
            "score_stdev": stdev(scores),
            "cognition_rate": round(st.mean(cog), 3) if cog else None,
            "delivery_failure_rate": round(st.mean(deliv), 3) if deliv else None,
            "by_class": byclass,
            "tokens_mean": mean(toks),
        }
    R["per_condition"] = per

    # paired vs bare (same task, same trial)
    bare = {(t, n): v["final_score"] for (t, c, n, v, _) in cells if c == "bare"}
    bare_tok = {(t, n): tokens.get("%s.bare.t%d" % (t, n)) for (t, c, n, v, _) in cells if c == "bare"}
    paired = {}
    for cond in conds:
        if cond == "bare":
            continue
        deltas, added, byclass_delta = [], [], {}
        for (t, c, n, v, cell) in cells:
            if c != cond or (t, n) not in bare:
                continue
            d = v["final_score"] - bare[(t, n)]
            deltas.append(d)
            byclass_delta.setdefault(klass[t], []).append(d)
            bt = bare_tok.get((t, n))
            if cell in tokens and bt is not None:
                added.append(tokens[cell] - bt)
        neg = {k: {"mean_delta": mean(ds),
                   "harm": (mean(ds) is not None and st.mean(ds) < 0),
                   "n": len(ds)}
               for k, ds in byclass_delta.items()}
        paired[cond] = {
            "n_pairs": len(deltas),
            "mean_delta_vs_bare": mean(deltas),
            "median_delta_vs_bare": median(deltas),
            "delta_stdev": stdev(deltas),
            "by_class": neg,
            "median_added_tokens_vs_bare": median(added),
        }
    R["paired_vs_bare"] = paired
    R["negative_transfer_note"] = (
        "by_class.harm=true on a class the condition was not meant to help "
        "means the intervention actively hurt those tasks; report it, do not "
        "average it away.")

    # pass@k / pass^k per condition (k = trials; pass = final_score == 100)
    pk = {}
    for cond in conds:
        by_task = {}
        for (t, c, n, v, _) in cells:
            if c == cond:
                by_task.setdefault(t, []).append(v["final_score"] == 100)
        full = {t: rs for t, rs in by_task.items() if len(rs) == trials}
        if full:
            pass_at_k = round(st.mean([1 if any(rs) else 0 for rs in full.values()]), 3)
            pass_pow_k = round(st.mean([1 if all(rs) else 0 for rs in full.values()]), 3)
        else:
            pass_at_k = pass_pow_k = None
        pk[cond] = {"k": trials, "n_tasks_complete": len(full),
                    "pass_at_k": pass_at_k, "pass_pow_k": pass_pow_k}
    R["pass_at_k"] = pk

    # per task-cond variance across trials
    var = {}
    for cond in conds:
        spread = []
        by_task = {}
        for (t, c, n, v, _) in cells:
            if c == cond:
                by_task.setdefault(t, []).append(v["final_score"])
        for t, rs in by_task.items():
            if len(rs) > 1:
                spread.append(max(rs) - min(rs))
        var[cond] = {"mean_within_task_range": mean(spread),
                     "n_tasks_multi_trial": len(spread)}
    R["within_task_variance"] = var

    out = os.path.join(run_dir, "ANALYSIS.json")
    open(out, "w").write(json.dumps(R, indent=2))
    print(json.dumps(R, indent=2))


if __name__ == "__main__":
    main()
