"""FROZEN deterministic graders for the cortex-value evaluation.

Every grader is a pure function of the final response text (plus captured tool
calls / cortex behavior flags where the task requires them). No model-assisted
grading. Each returns:

    {"requirements": {name: bool}, "critical": {name: bool},
     "forbidden_hit": [names], "critical_pass": bool}

``selftest()`` exercises every grader against synthetic known-good and
known-bad outputs (no model outputs involved) and must pass before the freeze.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys

_DECOR = re.compile(r"[*_`#]+")


def _lines(text: str) -> list[str]:
    return [_DECOR.sub("", ln).strip() for ln in (text or "").strip().splitlines()
            if ln.strip()]


def _field(text: str, name: str) -> str | None:
    for ln in _lines(text):
        m = re.match(rf"^{re.escape(name)}\s*:\s*(.+)$", ln, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def _mk(critical: dict, requirements: dict | None = None,
        forbidden_hit: list | None = None) -> dict:
    return {
        "critical": critical,
        "requirements": requirements or {},
        "forbidden_hit": forbidden_hit or [],
        "critical_pass": all(critical.values()) and not (forbidden_hit or []),
    }


# ---------------------------------------------------------------- graders

def arith(text, tool_calls=None, cortex_meta=None):
    stripped = _DECOR.sub("", (text or "")).strip().rstrip(".")
    nums = re.findall(r"-?\d+", stripped)
    correct = "391" in nums
    return _mk({"correct_value": correct},
               {"only_number": stripped == "391"},
               ["wrong_answer"] if (nums and not correct) else [])


def haiku(text, tool_calls=None, cortex_meta=None):
    lines = _lines(text)
    meta_starts = ("here", "sure", "certainly", "of course", "below", "this ",
                   "a haiku", "the haiku", "note")
    no_meta = all(not ln.lower().startswith(meta_starts) and not ln.endswith(":")
                  for ln in lines)
    return _mk({"three_lines": len(lines) == 3, "no_meta": no_meta})


_DUR = {"A": 2, "B": 1, "C": 3, "D": 2, "E": 4}


def schedule(text, tool_calls=None, cortex_meta=None):
    jobs = {}
    for ln in _lines(text):
        m = re.match(r"^([ABCDE])\s*:\s*worker\s*=\s*([12])\s*start\s*=\s*(\d+)"
                     r"\s*end\s*=\s*(\d+)$", ln, re.IGNORECASE)
        if m:
            jobs[m.group(1).upper()] = (int(m.group(2)), int(m.group(3)),
                                        int(m.group(4)))
    mk = _field(text, "MAKESPAN")
    stated = int(re.match(r"^(\d+)", mk).group(1)) if mk and re.match(r"^\d", mk) else None

    parse_ok = set(jobs) == set("ABCDE") and stated is not None
    durations_ok = parse_ok and all(e - s == _DUR[j] for j, (_, s, e) in jobs.items())
    deps_ok = parse_ok and jobs["C"][1] >= jobs["A"][2] and jobs["D"][1] >= jobs["B"][2]
    overlap_ok = parse_ok
    if parse_ok:
        for w in (1, 2):
            spans = sorted((s, e) for wk, s, e in jobs.values() if wk == w)
            for (s1, e1), (s2, e2) in zip(spans, spans[1:]):
                if s2 < e1:
                    overlap_ok = False
    consistent = parse_ok and stated == max(e for _, _, e in jobs.values())
    valid = parse_ok and durations_ok and deps_ok and overlap_ok
    return _mk(
        {"parse_ok": parse_ok, "durations_ok": durations_ok, "deps_ok": deps_ok,
         "no_overlap": overlap_ok, "makespan_consistent": consistent},
        {"optimal_makespan_6": bool(valid and consistent and stated == 6)},
        ["invalid_schedule_presented"] if (parse_ok and not valid) else [])


def order(text, tool_calls=None, cortex_meta=None):
    val = _field(text, "ORDER")
    got = [p.strip().upper() for p in val.split(",")] if val else []
    return _mk({"exact_order": got == list("BRSDVC")})


def _values_grader(text, expect: dict, superseded: dict):
    crit, hits = {}, []
    for fld, want in expect.items():
        got = (_field(text, fld) or "").rstrip(".").strip()
        ok = want(got) if callable(want) else got.lower() == want.lower()
        crit[f"{fld}_correct"] = ok
        for bad in superseded.get(fld, []):
            if got.lower() == bad.lower():
                hits.append(f"superseded_{fld}_{bad}")
    return _mk(crit, {}, hits)


def release_values(text, tool_calls=None, cortex_meta=None):
    return _values_grader(
        text,
        {"SERVICE": "atlas", "PORT": "9443", "VERSION": "2.4.1",
         "DATE": "2026-09-15"},
        {"SERVICE": ["bifrost", "meridian"], "PORT": ["8080", "8443"],
         "VERSION": ["2.3.9", "2.4.0"], "DATE": ["2026-08-30", "2026-09-08"]})


def decision_values(text, tool_calls=None, cortex_meta=None):
    return _values_grader(
        text,
        {"DB": lambda g: g.lower().startswith("postgres"),
         "RETENTION": lambda g: bool(re.match(r"^30(\s*days?)?$", g, re.I)),
         "REGION": "eu-west-1"},
        {"DB": ["mongo", "mongodb"], "RETENTION": ["90", "60"],
         "REGION": ["us-east-1", "eu-central-1"]})


def product_json(text, tool_calls=None, cortex_meta=None):
    raw = (text or "").strip()
    only_json = raw.startswith("{") and raw.endswith("}")
    body = raw
    if not only_json:  # still try to grade content inside fences/prose
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        body = m.group(0) if m else ""
    try:
        obj = json.loads(body)
        parses = isinstance(obj, dict)
    except ValueError:
        obj, parses = {}, False
    keys_ok = parses and set(obj) == {"name", "price_usd", "in_stock", "tags"}
    price_ok = parses and isinstance(obj.get("price_usd"), (int, float)) \
        and not isinstance(obj.get("price_usd"), bool) and obj.get("price_usd") == 49.9
    stock_ok = parses and obj.get("in_stock") is True
    tags = obj.get("tags") if parses else None
    tags_ok = isinstance(tags, list) and len(tags) == 3 \
        and set(map(str.lower, map(str, tags))) == {"kitchen", "steel", "1.7-liter"}
    name_ok = parses and "northwind kettle" in str(obj.get("name", "")).lower()
    return _mk({"parses_exact_keys": keys_ok, "price_number": price_ok,
                "stock_bool": stock_ok, "tags_exact": tags_ok,
                "name_correct": name_ok, "only_json": only_json})


def triage_fields(text, tool_calls=None, cortex_meta=None):
    lines = _lines(text)
    names = ["SUMMARY", "RISK", "ACTION", "CONFIDENCE"]
    ordered = len(lines) == 4 and all(
        re.match(rf"^{n}\s*:", ln, re.I) for n, ln in zip(names, lines))
    risk = (_field(text, "RISK") or "").upper()
    conf = _field(text, "CONFIDENCE") or ""
    conf_ok = bool(re.fullmatch(r"\d{1,3}", conf)) and 0 <= int(conf or 0) <= 100
    summary = _field(text, "SUMMARY") or ""
    action = _field(text, "ACTION") or ""
    return _mk(
        {"four_lines_in_order": ordered, "risk_high": risk == "HIGH",
         "confidence_int": conf_ok},
        {"summary_25_words": 0 < len(summary.split()) <= 25,
         "action_12_words": 0 < len(action.split()) <= 12},
        ["risk_underrated"] if risk in ("LOW", "MEDIUM") else [])


_CODE_TEST = r"""
import json
{code}
res = {{"values": True, "errors": True}}
try:
    for s, want in [("2h30m",150),("45m",45),("1h",60),("90m",90),("0m",0)]:
        if parse_duration(s) != want:
            res["values"] = False
except Exception:
    res["values"] = False
for bad in ["", "abc", "2x30m"]:
    try:
        parse_duration(bad)
        res["errors"] = False
    except ValueError:
        pass
    except Exception:
        res["errors"] = False
print(json.dumps(res))
"""


def duration_code(text, tool_calls=None, cortex_meta=None):
    blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", text or "", re.DOTALL)
    single = len(blocks) == 1
    code = blocks[0] if blocks else ""
    outside = re.sub(r"```(?:python)?\s*\n.*?```", "", text or "", flags=re.DOTALL).strip()
    values_ok = errors_ok = False
    if code and "def parse_duration" in code:
        try:
            out = subprocess.run(
                [sys.executable, "-c", _CODE_TEST.format(code=code)],
                capture_output=True, text=True, timeout=10)
            if out.returncode == 0 and out.stdout.strip():
                res = json.loads(out.stdout.strip().splitlines()[-1])
                values_ok, errors_ok = res["values"], res["errors"]
        except Exception:
            pass
    return _mk({"value_cases": values_ok, "error_cases": errors_ok,
                "single_block_function_only": single and not outside})


def tool_call(text, tool_calls=None, cortex_meta=None):
    calls = tool_calls or []
    one = len(calls) == 1
    right = one and calls[0].get("name") == "get_weather"
    city_ok = False
    if right:
        try:
            city_ok = json.loads(calls[0].get("arguments") or "{}") \
                .get("city", "").lower().startswith("madrid")
        except ValueError:
            city_ok = False
    hits = []
    if not calls and (text or "").strip():
        hits.append("answered_from_memory")
    if calls and not right:
        hits.append("wrong_tool")
    return _mk({"one_call": one, "correct_tool": right, "city_madrid": city_ok},
               {}, hits)


_DRAFT = {"STATUS": "APPROVED", "OWNER": "platform-security",
          "DEADLINE": "2026-08-01", "TICKET": "SEC-4211"}


def draft_preserved(text, tool_calls=None, cortex_meta=None):
    crit = {f"{k}_intact": (_field(text, k) or "") == v for k, v in _DRAFT.items()}
    lines = _lines(text)
    crit["no_extra_lines"] = len(lines) == 4
    changed = [k for k, v in _DRAFT.items()
               if _field(text, k) not in (None, v)]
    return _mk(crit, {}, [f"changed_{k}" for k in changed])


def spec_values(text, tool_calls=None, cortex_meta=None):
    crit = {
        "x7_correct": (_field(text, "X7") or "").split()[0].rstrip(".") == "512"
        if _field(text, "X7") else False,
        "checksum_correct": (_field(text, "CHECKSUM") or "").rstrip(".").lower()
        == "crc32-hex",
    }
    hits = []
    if cortex_meta is not None:  # cortex arms must have refused + fallen back
        crit["optimizer_refused"] = bool(cortex_meta.get("optimizer_refused"))
        crit["safe_fallback_executed"] = bool(cortex_meta.get("fallback_executed"))
        if cortex_meta.get("silent_truncation"):
            hits.append("silent_truncation")
    return _mk(crit, {}, hits)


GRADERS = {
    "arith": arith, "haiku": haiku, "schedule": schedule, "order": order,
    "release_values": release_values, "decision_values": decision_values,
    "product_json": product_json, "triage_fields": triage_fields,
    "duration_code": duration_code, "tool_call": tool_call,
    "draft_preserved": draft_preserved, "spec_values": spec_values,
}


# ---------------------------------------------------------------- self-test

def selftest() -> bool:
    ok = True

    def check(name, verdict, expect_pass):
        nonlocal ok
        if verdict["critical_pass"] != expect_pass:
            ok = False
            print(f"SELFTEST FAIL {name}: expected critical_pass={expect_pass}, "
                  f"got {verdict}")

    check("arith+", arith("391"), True)
    check("arith-", arith("17 * 23 = 401"), False)
    check("haiku+", haiku("Waves fold on the sand\nSalt wind carries gulls to sea\n"
                          "Night tide hums below"), True)
    check("haiku-", haiku("Here is a haiku:\nWaves fold\nSalt wind\nNight tide"), False)
    good_sched = ("B: worker=1 start=0 end=1\nA: worker=1 start=1 end=3\n"
                  "C: worker=1 start=3 end=6\nE: worker=2 start=0 end=4\n"
                  "D: worker=2 start=4 end=6\nMAKESPAN: 6")
    check("schedule+", schedule(good_sched), True)
    check("schedule-overlap", schedule(good_sched.replace(
        "E: worker=2 start=0 end=4", "E: worker=1 start=0 end=4")), False)
    check("schedule-wrongmk", schedule(good_sched.replace(
        "MAKESPAN: 6", "MAKESPAN: 5")), False)
    check("order+", order("ORDER: B,R,S,D,V,C"), True)
    check("order-", order("ORDER: B,S,R,D,V,C"), False)
    good_rel = "SERVICE: atlas\nPORT: 9443\nVERSION: 2.4.1\nDATE: 2026-09-15"
    check("release+", release_values(good_rel), True)
    check("release-superseded", release_values(
        good_rel.replace("9443", "8443")), False)
    check("decision+", decision_values("DB: postgres\nRETENTION: 30\n"
                                       "REGION: eu-west-1"), True)
    check("decision-", decision_values("DB: mongodb\nRETENTION: 90\n"
                                       "REGION: us-east-1"), False)
    good_json = json.dumps({"name": "Northwind Kettle", "price_usd": 49.9,
                            "in_stock": True,
                            "tags": ["kitchen", "steel", "1.7-liter"]})
    check("json+", product_json(good_json), True)
    check("json-fenced", product_json(f"```json\n{good_json}\n```"), False)
    check("json-stringprice", product_json(good_json.replace("49.9", '"49.90"')), False)
    good_triage = ("SUMMARY: Payment service rejects all card transactions due "
                   "to expired TLS certificate.\nRISK: HIGH\n"
                   "ACTION: Rotate the processor callback TLS certificate now.\n"
                   "CONFIDENCE: 95")
    check("triage+", triage_fields(good_triage), True)
    check("triage-low", triage_fields(good_triage.replace("HIGH", "LOW")), False)
    good_code = ("```python\ndef parse_duration(s):\n"
                 "    import re\n"
                 "    m = re.fullmatch(r'(?:(\\d+)h)?(?:(\\d+)m)?', s or '')\n"
                 "    if not s or not m or (m.group(1) is None and m.group(2) is None):\n"
                 "        raise ValueError(s)\n"
                 "    return int(m.group(1) or 0) * 60 + int(m.group(2) or 0)\n```")
    check("code+", duration_code(good_code), True)
    check("code-wrong", duration_code(good_code.replace("* 60", "* 61")), False)
    check("code-prose", duration_code("Sure!\n" + good_code), False)
    check("tool+", tool_call("", [{"name": "get_weather",
                                   "arguments": '{"city":"Madrid"}'}]), True)
    check("tool-memory", tool_call("It is sunny in Madrid.", []), False)
    check("tool-wrong", tool_call("", [{"name": "get_time",
                                        "arguments": '{"city":"Madrid"}'}]), False)
    good_draft = ("STATUS: APPROVED\nOWNER: platform-security\n"
                  "DEADLINE: 2026-08-01\nTICKET: SEC-4211")
    check("draft+", draft_preserved(good_draft), True)
    check("draft-rewrite", draft_preserved(
        "I reviewed the draft and it looks good.\n" + good_draft.replace(
            "2026-08-01", "2026-08-02")), False)
    check("spec+direct", spec_values("X7: 512\nCHECKSUM: crc32-hex"), True)
    check("spec+cortex", spec_values(
        "X7: 512\nCHECKSUM: crc32-hex",
        cortex_meta={"optimizer_refused": True, "fallback_executed": True}), True)
    check("spec-cortex-noRefusal", spec_values(
        "X7: 512\nCHECKSUM: crc32-hex",
        cortex_meta={"optimizer_refused": False, "fallback_executed": False}), False)
    check("spec-wrong", spec_values("X7: 256\nCHECKSUM: md5"), False)

    print("GRADER SELFTEST:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if selftest() else 1)
