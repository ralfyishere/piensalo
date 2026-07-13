#!/usr/bin/env python3
"""Generate the pre-registered Context Optimizer evaluation tasks.

Run once; the generated tasks/ tree is committed and then FROZEN — task
answers and graders are never tuned after seeing optimized results
(PREREGISTRATION.md is the binding record). Deterministic: same script,
same bytes.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TASKS = ROOT / "tasks"

# Deterministic office-noise paragraphs: realistic distractor mass.
CHATTER_TOPICS = [
    "the summer offsite venue and whether the lake house fits 40 people",
    "who keeps leaving the standing desk at maximum height",
    "the espresso machine descaling rota and its laminated instructions",
    "whether the team mascot should be a heron or an axolotl",
    "the never-ending thread about tabs versus spaces in the wiki",
    "parking garage badge readers rebooting every Tuesday",
    "the potluck signup sheet and three people all bringing hummus",
    "a long recap of the trivia night and the disputed geography answer",
    "the office plants watering schedule on alternating weeks",
    "whether meeting-free Wednesdays survived the reorg",
    "the saga of the missing HDMI adapter from room Ontario",
    "lunch options near the office and the new dumpling place",
    "the design team's font pairing debate for the internal newsletter",
    "a birthday card circulating for someone in another department",
    "the ergonomics vendor demo and the chair with too many levers",
]


def chatter(n: int, salt: str) -> str:
    paras = []
    for i in range(n):
        topic = CHATTER_TOPICS[i % len(CHATTER_TOPICS)]
        paras.append(
            f"Digression {salt}-{i + 1}: a long discussion about {topic}. "
            "It wandered for a while, several people chimed in with "
            "anecdotes, someone posted a poll, and the thread ended with "
            "no engineering decision, no constraint, and no action item. "
            "Nothing in it affects the current work beyond morale.")
    return "\n\n".join(paras)


def write(name: str, task: str, context: str, expected: dict,
          contract: dict | None, budget: int) -> None:
    d = TASKS / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "task.md").write_text(task, encoding="utf-8")
    (d / "context.txt").write_text(context, encoding="utf-8")
    (d / "expected.json").write_text(
        json.dumps(expected, indent=2) + "\n", encoding="utf-8")
    if contract:
        (d / "contract.json").write_text(
            json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    (d / "budget.txt").write_text(str(budget) + "\n", encoding="utf-8")


DEPLOY = "make deploy ENV=staging TAG=beta"
COMMIT = "4f2a9c1e7b3d5a20"
MIGRATION = ("Never run schema migrations against the production database "
             "from a laptop.")
FREEZE = "The platform team freezes all deploys on Friday afternoons."
STOP = "Stop the rollout if error rate exceeds 0.5% for 10 consecutive minutes."
FAILED = ("Caching whole responses in Redis; cache invalidation bugs "
          "produced stale order totals in checkout and the approach was "
          "abandoned.")


def core_markers() -> str:
    return f"""\
OBJECTIVE: Harden the acme-widgets service for the beta cut.
SUCCESS CONDITION: Staging runs 24h without a p95 regression.
DECISION: Host the beta on the shared acme-platform cluster.
DECISION: Host the beta on a dedicated small cluster after the March
  latency incident.
SUPERSEDES: Host the beta on the shared acme-platform cluster.
CONSTRAINT [EXACT]: {MIGRATION}
CONSTRAINT [EXACT]: Deploy to staging only with `{DEPLOY}`.
CONSTRAINT [EXACT]: {FREEZE}
ARTIFACT: services/widgets/src/store/pool.py
ARTIFACT: commit {COMMIT}
STOP CONDITION: {STOP}
FAILED APPROACH: {FAILED}
NEXT ACTION: Reproduce the CI failure locally with `pytest -q tests/store`.
"""


def main() -> None:
    write(
        "01-exact-recall",
        "Using only the provided project context, report the exact staging "
        "deploy command, the pinned commit, and the currently active "
        "hosting decision (the superseded one does not count).\n\n"
        "Quote the command and commit byte-for-byte. Answer with exactly "
        "these lines:\nCOMMAND: <exact command>\nCOMMIT: <exact commit>\n"
        "HOSTING: <one sentence>\n",
        chatter(10, "a") + "\n\n" + core_markers() + "\n" + chatter(14, "b"),
        {"must_contain": [DEPLOY, COMMIT, "dedicated"],
         "must_not_contain": ["shared acme-platform cluster is the host"]},
        {"required_output_fields": [{"name": "COMMAND"}, {"name": "COMMIT"},
                                    {"name": "HOSTING"}]},
        1600)

    write(
        "02-constraint-adherence",
        "Draft a five-step beta rollout plan for the widgets service that "
        "respects the project's operational constraints. After the plan, "
        "output these lines quoting the binding texts byte-for-byte from "
        "the context:\nMIGRATION_RULE: <exact constraint>\n"
        "FREEZE_RULE: <exact constraint>\nSTOP_RULE: <exact stop "
        "condition>\n",
        chatter(12, "c") + "\n\n" + core_markers() + "\n" + chatter(12, "d"),
        {"must_contain": [MIGRATION, FREEZE, STOP]},
        {"required_output_fields": [{"name": "MIGRATION_RULE"},
                                    {"name": "FREEZE_RULE"},
                                    {"name": "STOP_RULE"}]},
        1700)

    quant_context = (
        chatter(8, "e")
        + "\n\nCONSTRAINT [EXACT]: The widgets service must sustain 240 "
          "requests per second at steady state.\n"
          "CONSTRAINT [EXACT]: The reports service must sustain 60 requests "
          "per second at steady state.\n"
          "CONSTRAINT [EXACT]: The auth service must sustain 100 requests "
          "per second at steady state.\n\n"
        + "Digression e-x: someone mentioned the office has 500 chairs, 12 "
          "plants, and 3 espresso machines, and that trivia night had 42 "
          "attendees paying 15 dollars each. None of that is engineering.\n\n"
        + chatter(10, "f")
        + "\n\nNEXT ACTION: Size the ingress for combined steady-state "
          "load.\n")
    write(
        "03-quantitative",
        "From the project context, compute the combined steady-state "
        "requests per second across the widgets, reports, and auth "
        "services. Show one line of arithmetic, then answer with exactly:\n"
        "TOTAL: <number>\n",
        quant_context,
        {"field_values": {"TOTAL": "400"},
         "must_not_contain": ["TOTAL: 442", "TOTAL: 500"]},
        {"required_output_fields": [{"name": "TOTAL", "format": "number"}]},
        1400)

    structured_context = (
        chatter(9, "g")
        + "\n\nARTIFACT: service name acme-widgets\n"
          "CONSTRAINT [EXACT]: The beta ships as version 2.7.1-beta.3, "
          "nothing else.\n"
          "NEXT ACTION: Run `pytest -q tests/store` before tagging.\n\n"
        + chatter(9, "h"))
    write(
        "04-structured-output",
        "Answer with exactly three lines and nothing else:\n"
        "NAME: <the service name from context>\n"
        "VERSION: <the exact beta version from context>\n"
        "NEXT_COMMAND: <the exact test command from context>\n",
        structured_context,
        {"must_contain": ["2.7.1-beta.3", "pytest -q tests/store"]},
        {"required_output_fields": [{"name": "NAME"}, {"name": "VERSION"},
                                    {"name": "NEXT_COMMAND"}],
         "no_extra_lines": True},
        1300)

    code_context = (
        chatter(8, "i")
        + "\n\nARTIFACT: services/widgets/src/store/pool.py\n\n"
          "The pool module's acquire() helper hardcodes timeout=5, and the "
          "CI runner is slower than laptops, so "
          "tests/store/test_pool.py::test_acquire_timeout flakes in CI. "
          "The team agreed the timeout in acquire() must become "
          "configurable.\n\n"
          "NEXT ACTION: Reproduce with `pytest -q tests/store` before "
          "changing pool.py.\n\n"
        + chatter(12, "j"))
    write(
        "05-repo-coding",
        "Based on the project context: which file and function must change "
        "to fix the flaky CI timeout, and what exact command reproduces "
        "it? Answer with exactly:\nFILE: <exact path>\nFUNCTION: <name>\n"
        "COMMAND: <exact command>\n",
        code_context,
        {"must_contain": ["services/widgets/src/store/pool.py", "acquire",
                          "pytest -q tests/store"]},
        {"required_output_fields": [{"name": "FILE"}, {"name": "FUNCTION"},
                                    {"name": "COMMAND"}]},
        1500)

    failed_context = (
        chatter(10, "k")
        + f"\n\nFAILED APPROACH: {FAILED}\n"
          "DECISION: Cache per-entity fragments with version-keyed "
          "invalidation instead of whole responses.\n\n"
        + chatter(12, "m"))
    write(
        "06-failed-approach",
        "Recommend a caching approach for the widgets service that is "
        "consistent with this project's history. Answer with exactly:\n"
        "APPROACH: <one sentence consistent with the active decision>\n"
        "AVOID: <byte-for-byte the failed approach recorded in the "
        "context>\n",
        failed_context,
        {"must_contain": [FAILED, "version-keyed"]},
        {"required_output_fields": [{"name": "APPROACH"},
                                    {"name": "AVOID"}]},
        1500)

    distractor_context = (
        chatter(15, "n")
        + "\n\nDigression n-owners: the retro also assigned the logging "
          "cleanup to owner d.kim and the docs overhaul to owner a.singh, "
          "both due next sprint, and thanked j.ortiz for the on-call "
          "handover template.\n\n"
        + chatter(10, "p")
        + "\n\nOPEN ACTION: The incident retro assigned the pager rotation "
          "fix to owner mireya.flores with a hard due date of Thursday.\n\n"
        + chatter(15, "q"))
    write(
        "07-distractor-heavy",
        "From the project context: who owns the pager rotation fix? "
        "Answer with exactly:\nOWNER: <exact username>\n",
        distractor_context,
        {"field_values": {"OWNER": "mireya.flores"},
         "must_not_contain": ["OWNER: d.kim", "OWNER: a.singh",
                              "OWNER: j.ortiz"]},
        {"required_output_fields": [{"name": "OWNER"}]},
        1200)

    dense = "\n".join(
        f"CONSTRAINT [EXACT]: Binding rule {i:02d}: subsystem-{i:02d} must "
        f"keep its p99 under {150 + i} ms and abort on breach."
        for i in range(1, 41))
    write(
        "08-fallback-required",
        "Quote binding rule 07 and binding rule 23 byte-for-byte from the "
        "context. Answer with exactly:\nC7: <exact rule text>\n"
        "C23: <exact rule text>\n",
        "OBJECTIVE: Certify every binding rule before launch.\n" + dense
        + "\nNEXT ACTION: Certify the full rule table.\n",
        {"must_contain": [
            "Binding rule 07: subsystem-07 must keep its p99 under 157 ms "
            "and abort on breach.",
            "Binding rule 23: subsystem-23 must keep its p99 under 173 ms "
            "and abort on breach."]},
        {"required_output_fields": [{"name": "C7"}, {"name": "C23"}]},
        400)

    print(f"wrote 8 tasks under {TASKS}")


if __name__ == "__main__":
    main()
