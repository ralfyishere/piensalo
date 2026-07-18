"""Cortex-value evaluation harness (see PREREGISTRATION.md — FROZEN).

Runs the 12 frozen tasks under four conditions against the same local model:

  A direct         task -> model
  B context        Context Optimizer runtime -> model -> verify -> expand/fallback
  C think_context  deterministic THINK plan + the B pipeline
  D full_cortex    Cortex Router decides; CHECK repairs only demonstrated
                   failures; draft tasks go CHECK-first (abstention path)

Reuses the shipping mechanisms only: compile_program (THINK), run_optimized
(CONTEXT), scan + _build_repair_prompt + repair library (CHECK), verify.contract,
CortexRouter, OpenAICompatAdapter (deterministic extras temperature=0 seed=42).

Every model call is recorded with purpose, tokens, and wall time. `--mock`
smoke-tests the plumbing with a canned adapter (zero real model calls).

Usage:
    python evals/cortex-value/harness.py --mock          # plumbing smoke
    python evals/cortex-value/harness.py                 # frozen run
    python evals/cortex-value/harness.py --only 03,08    # subset (debug only)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from graders import GRADERS  # noqa: E402
from tasks import TASKS, TOOL_DEFS  # noqa: E402

from piensalo.adapters.base import ModelAdapter, ModelResponse  # noqa: E402
from piensalo.adapters.openai_compat import OpenAICompatAdapter  # noqa: E402
from piensalo.cli.main import _build_repair_prompt  # noqa: E402
from piensalo.compiler.program import compile_program  # noqa: E402
from piensalo.context.ingest import load_context_text  # noqa: E402
from piensalo.context.runtime import run_optimized  # noqa: E402
from piensalo.gateway.protocol import ContentBlock, Message, NormalizedRequest  # noqa: E402
from piensalo.gateway.router import CortexRouter, RouterPolicy  # noqa: E402
from piensalo.inspect import scanner  # noqa: E402
from piensalo.verify import contract as contract_mod  # noqa: E402

MODEL = "qwen2.5:7b"
BASE = "http://127.0.0.1:11434/v1"
EXTRA = {"temperature": 0, "seed": 42}
TIMEOUT = 180
ROUTER = CortexRouter(RouterPolicy(context_token_threshold=800))

MATCH = {
    "PASS_THROUGH": {"PASS_THROUGH"},
    "CONTEXT": {"CONTEXT", "CONTEXT_AND_CHECK", "THINK_AND_CONTEXT", "FULL_CORTEX"},
    "CHECK": {"CHECK", "CONTEXT_AND_CHECK", "FULL_CORTEX"},
    "THINK": {"THINK", "THINK_AND_CONTEXT", "FULL_CORTEX"},
}


class MockAdapter(ModelAdapter):
    provider = "mock"

    def complete(self, prompt: str) -> ModelResponse:
        return ModelResponse(text="MOCK", requested_model=self.requested_model,
                             resolved_model=self.requested_model, provider="mock",
                             tokens_in=len(prompt) // 4, tokens_out=1,
                             wall_seconds=0.0)


class Runner:
    def __init__(self, mock: bool):
        self.mock = mock
        self.adapter = (MockAdapter(MODEL) if mock else
                        OpenAICompatAdapter(MODEL, base_url=BASE,
                                            timeout=TIMEOUT, extra_body=EXTRA))
        self.calls: list[dict] = []

    # ---------------------------------------------------------- model calls

    def call_text(self, prompt: str, purpose: str) -> str:
        r = self.adapter.complete(prompt)
        self.calls.append({"purpose": purpose, "tokens_in": r.tokens_in,
                           "tokens_out": r.tokens_out,
                           "wall_s": round(r.wall_seconds, 2)})
        return r.text

    def call_tools(self, prompt: str, tool_names: list[str], purpose: str):
        """Tool-capable call (raw endpoint; the text adapter cannot carry
        tools). Returns (content, tool_calls)."""
        if self.mock:
            self.calls.append({"purpose": purpose, "tokens_in": len(prompt) // 4,
                               "tokens_out": 1, "wall_s": 0.0})
            return "", [{"name": "get_weather", "arguments": '{"city":"Madrid"}'}]
        body = {"model": MODEL, "messages": [{"role": "user", "content": prompt}],
                "tools": [TOOL_DEFS[n] for n in tool_names], **EXTRA}
        req = urllib.request.Request(
            BASE + "/chat/completions", data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        t0 = time.monotonic()
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            d = json.loads(resp.read())
        wall = time.monotonic() - t0
        usage = d.get("usage", {})
        self.calls.append({"purpose": purpose,
                           "tokens_in": usage.get("prompt_tokens", 0),
                           "tokens_out": usage.get("completion_tokens", 0),
                           "wall_s": round(wall, 2)})
        msg = d["choices"][0]["message"]
        tcs = [{"name": tc["function"]["name"],
                "arguments": tc["function"]["arguments"]}
               for tc in (msg.get("tool_calls") or [])]
        return msg.get("content") or "", tcs

    # ------------------------------------------------------------- helpers

    def full_input(self, t: dict) -> str:
        parts = [t["task_text"]]
        if t.get("context_text"):
            parts.append("--- CONTEXT ---\n" + t["context_text"])
        if t.get("draft_text"):
            parts.append("--- DRAFT ---\n" + t["draft_text"])
        return "\n\n".join(parts)

    def internal_contract(self, t: dict) -> dict | None:
        if not t.get("contract_fields"):
            return None
        return contract_mod.convert_task_contract(
            {"required_output_fields": [{"name": n} for n in t["contract_fields"]]})

    def think_plan(self, t: dict) -> str:
        return compile_program(t["task_text"], mode="prompt")

    # ---------------------------------------------------------- mechanisms

    def run_runtime(self, t: dict, task_text: str) -> dict:
        """The B pipeline: optimize -> model -> verify -> expand/fallback."""
        if t.get("tools"):
            # Documented deviation: the optimizer has nothing to optimize and
            # the runtime cannot carry tools; tool tasks call the tool-capable
            # endpoint directly under this condition.
            content, tcs = self.call_tools(task_text, t["tools"], "execute")
            return {"text": content, "tool_calls": tcs, "meta": {
                "note": "tool task: runtime cannot carry tools; direct tool call"}}
        items = (load_context_text(t["context_text"], name=t["id"])
                 if t.get("context_text") else [])
        task_for_runtime = task_text
        if t.get("draft_text"):
            task_for_runtime += "\n\n--- DRAFT ---\n" + t["draft_text"]
        # No-context tasks have nothing to select; the budget must not
        # constrain the task envelope itself (caught in mock smoke: a THINK-
        # prefixed task busted the 700 default and refused with zero items).
        budget = (t.get("context_budget") or 700) if items else 10_000
        rr = run_optimized(
            task_text=task_for_runtime, items=items,
            budget=budget, adapter=self.adapter,
            contract=self.internal_contract(t), max_expansions=2,
            fallback=t.get("fallback", "run" if t.get("context_text") else "recommend"))
        for a in rr.attempts:
            self.calls.append({"purpose": a.label, "tokens_in": a.tokens_in,
                               "tokens_out": a.tokens_out,
                               "wall_s": round(a.wall_seconds, 2)})
        meta = {
            "outcome": rr.outcome,
            "optimizer_refused": bool(rr.selection.refused),
            "fallback_executed": rr.outcome == "SAFE FALLBACK (EXECUTED)",
            "silent_truncation": False,  # refusal/fallback is explicit by design
            "expansion_rounds": sum(1 for a in rr.attempts
                                    if a.label.startswith("expansion")),
        }
        return {"text": rr.response_text or "", "tool_calls": None, "meta": meta}

    def check_repair(self, t: dict, text: str) -> dict:
        """CHECK: inspect -> at most one targeted repair on demonstrated
        failure -> accept only a deterministic improvement."""
        icontract = self.internal_contract(t)
        cres = contract_mod.check(icontract, text) if icontract else None
        # Instructions-only task for the scanner (the shipping CLI contract);
        # embedding the draft inside the "task" distorts deliverable detection.
        sres = scanner.scan(t["task_text"], text,
                            cres or icontract, max_repairs=1)
        missing = len(cres["missing"]) if cres else 0
        meta = {"check_ran": True, "defects": len(sres.get("defects_detected", [])),
                "contract_missing": missing, "abstained": False,
                "repair_attempted": False, "repair_accepted": False}
        if sres["no_repair_needed"] and missing == 0:
            meta["abstained"] = True  # NO REPAIR NEEDED is a success verdict
            return {"text": text, "meta": meta}
        if not sres["selected_repairs"]:
            return {"text": text, "meta": meta}
        skill = sres["selected_repairs"][0]
        prompt = _build_repair_prompt(t["task_text"], text, skill, sres)
        meta["repair_attempted"] = True
        meta["repair_skill"] = skill
        repaired = self.call_text(prompt, "repair")
        r_cres = contract_mod.check(icontract, repaired) if icontract else None
        r_missing = len(r_cres["missing"]) if r_cres else 0
        r_sres = scanner.scan(t["task_text"], repaired, r_cres or icontract, 1)
        better = (r_missing < missing) or (
            r_missing == missing
            and len(r_sres.get("defects_detected", [])) < len(
                sres.get("defects_detected", [])))
        if better:
            meta["repair_accepted"] = True
            return {"text": repaired, "meta": meta}
        return {"text": text, "meta": meta}  # never accept a non-improvement

    # ---------------------------------------------------------- conditions

    def cond_direct(self, t: dict) -> dict:
        if t.get("tools"):
            content, tcs = self.call_tools(self.full_input(t), t["tools"], "execute")
            return {"text": content, "tool_calls": tcs, "meta": {}}
        return {"text": self.call_text(self.full_input(t), "execute"),
                "tool_calls": None, "meta": {}}

    def cond_context(self, t: dict) -> dict:
        return self.run_runtime(t, t["task_text"])

    def cond_think_context(self, t: dict) -> dict:
        plan = self.think_plan(t)
        if t.get("tools"):
            content, tcs = self.call_tools(
                plan + "\n\n## TASK\n" + self.full_input(t), t["tools"], "execute")
            return {"text": content, "tool_calls": tcs,
                    "meta": {"think_prefix_chars": len(plan)}}
        out = self.run_runtime(t, plan + "\n\n## TASK\n" + t["task_text"])
        out["meta"]["think_prefix_chars"] = len(plan)
        return out

    def cond_full_cortex(self, t: dict) -> dict:
        # Draft tasks: CHECK-first (the shipping inspect-then-repair flow).
        if t.get("draft_text"):
            out = self.check_repair(t, t["draft_text"])
            out["meta"]["router_decision"] = "CHECK (draft-first policy)"
            out["tool_calls"] = None
            return out
        req = NormalizedRequest(model=MODEL, messages=[Message(
            role="user",
            content=[ContentBlock(type="text", text=self.full_input(t))])])
        decision = ROUTER.decide(req)
        d = decision.decision
        meta: dict = {"router_decision": d,
                      "router_reasons": decision.reasons}
        want_think = d in ("THINK", "THINK_AND_CONTEXT", "FULL_CORTEX")
        want_context = d in ("CONTEXT", "CONTEXT_AND_CHECK",
                             "THINK_AND_CONTEXT", "FULL_CORTEX")
        want_check = d in ("CHECK", "CONTEXT_AND_CHECK", "FULL_CORTEX")

        if d == "PASS_THROUGH":
            out = self.cond_direct(t)
            out["meta"].update(meta)
            return out

        task_text = t["task_text"]
        if want_think:
            plan = self.think_plan(t)
            meta["think_prefix_chars"] = len(plan)
            task_text = plan + "\n\n## TASK\n" + task_text

        if want_context:
            out = self.run_runtime(t, task_text)
        elif t.get("tools"):
            content, tcs = self.call_tools(task_text, t["tools"], "execute")
            out = {"text": content, "tool_calls": tcs, "meta": {}}
        else:
            prompt = task_text
            if t.get("context_text"):
                prompt += "\n\n--- CONTEXT ---\n" + t["context_text"]
            out = {"text": self.call_text(prompt, "execute"),
                   "tool_calls": None, "meta": {}}

        if want_check and out["text"]:
            checked = self.check_repair(t, out["text"])
            out["text"] = checked["text"]
            out["meta"].update(checked["meta"])
        out["meta"].update(meta)
        return out


# ------------------------------------------------------------------ verdicts

def verdict(cond_grade: dict, direct_grade: dict, meta: dict) -> str:
    if meta.get("abstained") and cond_grade["critical_pass"]:
        return "CORRECT ABSTENTION"
    if meta.get("fallback_executed") and cond_grade["critical_pass"]:
        return "SAFE FALLBACK"
    all_c = lambda g: {**g["critical"], **g["requirements"]}  # noqa: E731
    c, d = all_c(cond_grade), all_c(direct_grade)
    keys = set(c) | set(d)
    new_failures = [k for k in keys if not c.get(k, True) and d.get(k, False)]
    gains = [k for k in keys if c.get(k, False) and not d.get(k, True)]
    if cond_grade["forbidden_hit"] and not direct_grade["forbidden_hit"]:
        return "REGRESSION"
    if new_failures:
        return "REGRESSION"
    if gains:
        return "IMPROVED"
    return "MAINTAINED"


# ---------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--only", default=None, help="comma list of task-id prefixes")
    args = ap.parse_args()
    os.environ.setdefault("OPENAI_API_KEY", "ollama")

    tasks = TASKS
    if args.only:
        wanted = args.only.split(",")
        tasks = [t for t in TASKS if any(t["id"].startswith(w) for w in wanted)]

    conditions = [("direct", "cond_direct"), ("context", "cond_context"),
                  ("think_context", "cond_think_context"),
                  ("full_cortex", "cond_full_cortex")]
    results: dict = {"model": MODEL, "settings": EXTRA, "mock": args.mock,
                     "tasks": {}}

    for t in tasks:
        results["tasks"][t["id"]] = {}
        for cname, fn in conditions:
            runner = Runner(args.mock)
            t0 = time.monotonic()
            try:
                out = getattr(runner, fn)(t)
                error = None
            except Exception as e:  # honest failure capture, run continues
                out = {"text": "", "tool_calls": None, "meta": {"error": str(e)}}
                error = str(e)
            wall = round(time.monotonic() - t0, 2)
            cortex_meta = out["meta"] if cname != "direct" else None
            grade = GRADERS[t["grader"]](out["text"], out.get("tool_calls"),
                                         cortex_meta)
            results["tasks"][t["id"]][cname] = {
                "grade": grade, "meta": out["meta"], "calls": runner.calls,
                "tokens_in": sum(c["tokens_in"] for c in runner.calls),
                "tokens_out": sum(c["tokens_out"] for c in runner.calls),
                "wall_s": wall, "error": error,
                "response_text": out["text"][:2000],
                "tool_calls": out.get("tool_calls"),
            }
            print(f"{t['id']:22s} {cname:14s} critical_pass="
                  f"{grade['critical_pass']} calls={len(runner.calls)} "
                  f"tokens={sum(c['tokens_in'] + c['tokens_out'] for c in runner.calls)} "
                  f"wall={wall}s", flush=True)

        # per-task verdicts vs direct
        dgrade = results["tasks"][t["id"]]["direct"]["grade"]
        for cname, _ in conditions[1:]:
            cell = results["tasks"][t["id"]][cname]
            cell["verdict"] = verdict(cell["grade"], dgrade, cell["meta"])
            print(f"  -> {cname}: {cell['verdict']}", flush=True)

    outpath = Path(__file__).parent / "results" / (
        "run-mock.json" if args.mock else "run.json")
    outpath.parent.mkdir(exist_ok=True)
    outpath.write_text(json.dumps(results, indent=2) + "\n")
    print(f"\nwrote {outpath}")


if __name__ == "__main__":
    main()
