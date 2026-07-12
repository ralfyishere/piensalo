#!/usr/bin/env python3
"""Grader self-test battery — verify the verifier BEFORE grading anything.

For every evals/public-tasks/<task>/ with a probes/ dir, run
hidden-grader/grade.py on each probe file and compare the emitted layered
verdict against probes/expected.json:

  { "<probe-file>": {"cognition_pass": true|false|null,
                     "contract_pass": true|false|null,   # null = don't care
                     "failure_layer": "<layer>"|null } }

Every task must include at least these probe classes:
  clean-correct     -> cognition true, contract true, layer none
  decorated-correct -> cognition true (decoration-masking guard), contract false
  wrong-value       -> cognition false, layer cognition
  prose-trap        -> text mentioning task numbers/scale WITHOUT stating the
                       answer -> cognition MUST NOT be credited
                       (fallback-overreach guard)
  stall             -> cognition null, layer delivery-incomplete
  stub              -> cognition null, layer delivery-incomplete

Exit 0 only if every probe of every task matches.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TASKS = os.path.abspath(os.path.join(HERE, "..", "public-tasks"))
REQUIRED = ["clean-correct", "decorated-correct", "wrong-value",
            "prose-trap", "stall", "stub"]

fails = []
tasks = [d for d in sorted(os.listdir(TASKS))
         if os.path.isdir(os.path.join(TASKS, d)) and not d.startswith("_")]
for task in tasks:
    tdir = os.path.join(TASKS, task)
    probes = os.path.join(tdir, "probes")
    grader = os.path.join(tdir, "hidden-grader", "grade.py")
    if not os.path.isdir(probes) or not os.path.exists(grader):
        fails.append("%s: missing probes/ or grader" % task)
        continue
    expected = json.load(open(os.path.join(probes, "expected.json")))
    names = [os.path.splitext(p)[0] for p in expected]
    for req in REQUIRED:
        if not any(req in n for n in names):
            fails.append("%s: missing required probe class '%s'" % (task, req))
    for probe, want in expected.items():
        ppath = os.path.join(probes, probe)
        if not os.path.exists(ppath):
            fails.append("%s/%s: probe file missing" % (task, probe))
            continue
        out = subprocess.run(["python3", grader, ppath],
                             capture_output=True, text=True)
        try:
            got = json.loads(out.stdout.strip().splitlines()[-1])
        except Exception:
            fails.append("%s/%s: grader emitted no verdict (%s)"
                         % (task, probe, out.stderr.strip()[:120]))
            continue
        checks = [("cognition_pass", got["cognitive_correctness"]["pass"]),
                  ("contract_pass", got["task_contract_compliance"]["pass"]),
                  ("failure_layer", got["failure_layer"])]
        for key, actual in checks:
            if key in want and want[key] is not None and actual != want[key]:
                fails.append("%s/%s: %s expected %r got %r"
                             % (task, probe, key, want[key], actual))

print("tasks checked: %d" % len(tasks))
if fails:
    for f in fails:
        print("FAIL " + f)
    print("%d failure(s)" % len(fails))
    sys.exit(1)
print("ALL GRADER SELF-TESTS PASS")
