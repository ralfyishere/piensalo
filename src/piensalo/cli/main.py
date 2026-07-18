"""piensalo CLI: think / inspect / repair / verify / context / loop / skill / doctor / version.

Offline-first: ``think`` compiles a cognitive program without any model
call; ``inspect``/``repair``/``verify`` are deterministic scans of real
drafts; ``loop`` delegates to the bounded loop controller; ``skill``
manages skill directories (including the security scan); ``doctor`` checks
the environment without touching the network. A model is only executed
when the operator explicitly configures an adapter.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import piensalo
from piensalo import repair as repair_lib
from piensalo.compiler import compile_program
from piensalo.inspect import scanner
from piensalo.security import scan_skill_dir
from piensalo.security.skill_scan import ABS_PATH
from piensalo.verify import contract as contract_mod
from piensalo.verify import layered

SKILL_DIRS = ("skills", "micro-skills")

_SKILL_TEMPLATE = """---
name: {name}
description: "One-sentence description of the single intervention."
---

# {name}

**Trigger (observable):** State the observable condition that activates this skill.

**When NOT to activate:** Name the cases where running it would be waste.

## Procedure
1. First step.
2. Second step.
3. Third step.

## Required output
What the skill must leave behind in the work.

## Verification
How to check the skill actually ran correctly.

**Evidence status:** designed — no direct experimental test yet.
"""


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _load_contract(path: str | None) -> dict | None:
    return contract_mod.load_task_contract(path) if path else None


_PATHLIKE_SUFFIXES = (".md", ".txt", ".json")


def _resolve_task_text(positional: str | None, file_override: str | None,
                       text_override: str | None) -> str:
    """Resolve the think task source.

    Explicit overrides always win: ``--file PATH`` is read as a file,
    ``--text STRING`` is taken literally. Otherwise the positional argument
    is a file if it exists on disk; if it merely LOOKS like a path (ends in
    .md/.txt/.json or contains a path separator) but does not exist, that
    is a hard error rather than a silent literal-text fallback; anything
    else is literal task text.
    """
    if file_override and text_override is not None:
        raise ValueError("--file and --text are mutually exclusive")
    if file_override:
        return _read(file_override)  # FileNotFoundError propagates loudly
    if text_override is not None:
        return text_override
    if positional is None:
        raise ValueError("missing task: give a TASK file/text argument, --file, or --text")
    p = Path(positional)
    if p.is_file():
        return _read(positional)
    if p.exists():  # exists but is not a regular file (e.g. a directory)
        raise ValueError(f"not a file: {positional}")
    looks_like_path = positional.lower().endswith(_PATHLIKE_SUFFIXES) or (
        "/" in positional or os.sep in positional
    )
    if looks_like_path:
        raise ValueError(f"file not found: {positional} (use --text to force literal)")
    return positional


# ------------------------------------------------------------ subcommands
def cmd_think(args) -> int:
    try:
        task = _resolve_task_text(args.task, args.file, args.text)
    except ValueError as e:
        print(f"piensalo think: {e}", file=sys.stderr)
        return 2
    if args.adapter and not args.offline:
        from piensalo.adapters import get_adapter

        if args.adapter != "manual" and not args.model:
            print("piensalo think: --adapter requires --model", file=sys.stderr)
            return 1
        prompt = compile_program(task, mode="prompt")
        kwargs = {"model": args.model} if args.model else {}
        adapter = get_adapter(args.adapter, **kwargs)
        response = adapter.complete(prompt)
        print(response.text)
        print(
            f"\n--- provenance: requested={response.requested_model} "
            f"resolved={response.resolved_model} provider={response.provider} "
            f"tokens={response.tokens_in}/{response.tokens_out} "
            f"wall={response.wall_seconds:.1f}s ---",
            file=sys.stderr,
        )
        return 0
    # Offline (default): compile and print the cognitive program.
    print(compile_program(task, mode=args.mode))
    return 0


def cmd_inspect(args) -> int:
    task, draft = _read(args.task), _read(args.draft)
    contract = _load_contract(args.contract)
    result = scanner.scan(task, draft, contract, max_repairs=args.max_repairs)
    print(json.dumps(result, indent=2))
    if result["no_repair_needed"]:
        print("\nNO REPAIR NEEDED — no observable defect cleared the activation threshold.")
    else:
        print(f"\nselected repair(s): {', '.join(result['selected_repairs'])}")
        for line in result["evidence_from_draft"]:
            print(f"  evidence: {line}")
    return 0


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _build_repair_prompt(task: str, draft: str, skill: str, result: dict) -> str:
    """The full ready-to-paste repair prompt: draft + repair skill + task."""
    lines = [
        "You are applying ONE targeted repair to a draft.",
        "Apply ONLY the repair below to the demonstrated defect; preserve every",
        "correct portion of the draft. Output the full corrected draft and",
        "nothing else — no commentary, no preamble.",
        "",
        "## Task",
        "",
        task.strip(),
        "",
        "## Current draft",
        "",
        draft.strip(),
        "",
        f"## Repair skill to apply: {skill}",
        "",
        repair_lib.load_repair(skill).strip(),
        "",
        "## Demonstrated defect",
        f"- defect: {result['verification_target']}",
    ]
    lines.extend(f"- evidence: {e}" for e in result["evidence_from_draft"])
    return "\n".join(lines)


def _print_reinspection(result: dict) -> None:
    """Honest post-repair report: re-inspection findings, never a success claim."""
    print("re-inspection of repaired draft:")
    if result["no_repair_needed"]:
        print(
            "  no remaining observable defects "
            "(absence of detected defects, not proof of correctness)"
        )
        return
    print(f"  remaining observable defect(s): {', '.join(result['defects_detected'])}")
    for line in result["evidence_from_draft"]:
        print(f"  evidence: {line}")


def _repair_via_adapter(args, task: str, draft: str, contract: dict | None,
                        prompt: str, skill: str) -> int:
    from piensalo.adapters import get_adapter
    from piensalo.adapters.base import AdapterError

    adapter_name = {"openai": "openai-compat"}.get(args.adapter, args.adapter)
    draft_path = Path(args.draft)
    out_path = (
        Path(args.output)
        if args.output
        else draft_path.parent / (draft_path.stem + ".repaired.md")
    )
    for src in (args.draft, args.task, args.contract):
        if src and Path(src).exists() and out_path.resolve() == Path(src).resolve():
            print(f"piensalo repair: refusing to overwrite source file {src}", file=sys.stderr)
            return 1
    if out_path.exists() and not args.force:
        print(
            f"piensalo repair: output exists: {out_path} (use --force to overwrite)",
            file=sys.stderr,
        )
        return 1
    if adapter_name != "manual" and not args.model:
        print("piensalo repair: --adapter requires --model (manual excepted)", file=sys.stderr)
        return 1
    kwargs: dict = {}
    if args.model:
        kwargs["model"] = args.model
    if adapter_name == "manual" and args.response_file:
        kwargs["response_file"] = args.response_file

    started_at = datetime.now(timezone.utc).isoformat()
    try:
        adapter = get_adapter(adapter_name, **kwargs)
        response = adapter.complete(prompt)
    except (AdapterError, OSError) as e:  # includes ModelFallbackError — no fallback, ever
        print(f"piensalo repair: adapter failure: {e}", file=sys.stderr)
        return 1
    finished_at = datetime.now(timezone.utc).isoformat()

    # Contract-gated acceptance (NR-10): when a contract exists, the contract
    # — never the scanner that proposed the repair — judges whether the
    # repaired text ships. A rejected repair preserves the original draft.
    from piensalo.verify.acceptance import evaluate_repair

    acceptance = evaluate_repair(contract, draft, response.text) if contract \
        else None
    final_text = acceptance["output"] if acceptance else response.text

    out_path.write_text(final_text, encoding="utf-8")
    sidecar = out_path.with_name(out_path.name + ".provenance.json")
    sidecar.write_text(
        json.dumps(
            {
                "adapter": adapter_name,
                "provider": response.provider,
                "requested_model": response.requested_model,
                "resolved_model": response.resolved_model,
                "started_at": started_at,
                "finished_at": finished_at,
                "selected_repair": skill,
                "acceptance": (
                    {"verdict": acceptance["verdict"],
                     "accepted": acceptance["accept"],
                     "reason": acceptance["reason"]}
                    if acceptance else
                    {"verdict": "UNMEASURED",
                     "accepted": None,
                     "reason": "no contract declared: no independent verifier "
                               "gated this repair"}),
                "input_sha256": {
                    "task": _sha256(task),
                    "draft": _sha256(draft),
                    "prompt": _sha256(prompt),
                },
                "output_sha256": _sha256(final_text),
                "model_output_sha256": _sha256(response.text),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    if acceptance and not acceptance["accept"]:
        print(f"REPAIR {acceptance['verdict']} — {acceptance['reason']}")
        print(f"wrote ORIGINAL draft (repair not accepted): {out_path}")
    else:
        if acceptance:
            print(f"repair ACCEPTED under the contract — {acceptance['reason']}")
        print(f"wrote repaired draft: {out_path}")
    print(f"wrote provenance: {sidecar}")
    # A model returning text is never "repair succeeded" — re-inspect what
    # actually shipped.
    _print_reinspection(scanner.scan(task, final_text, contract, max_repairs=1))
    return 0


def cmd_repair(args) -> int:
    task, draft = _read(args.task), _read(args.draft)
    contract = _load_contract(args.contract)
    result = scanner.scan(task, draft, contract, max_repairs=1)
    if result["no_repair_needed"]:
        print("NO REPAIR NEEDED — no observable defect cleared the activation threshold.")
        return 0
    skill = result["selected_repairs"][0]
    prompt = _build_repair_prompt(task, draft, skill, result)
    if args.adapter:
        return _repair_via_adapter(args, task, draft, contract, prompt, skill)
    # DEFAULT (offline): emit an honestly-labeled packet; nothing is applied.
    print("REPAIR PACKET — instructions for a model; nothing has been applied.")
    print(f"# Selected repair: {skill} (defect: {result['verification_target']})")
    print("# Smallest justified repair — apply it to the demonstrated defect only;")
    print("# preserve every correct portion of the draft.")
    for line in result["evidence_from_draft"]:
        print(f"# evidence: {line}")
    print()
    print("--- READY-TO-PASTE PROMPT ---")
    print(prompt)
    print("--- END READY-TO-PASTE PROMPT ---")
    return 0


def _values_equal(got, expected) -> bool:
    """Deterministic value comparison: numeric when both sides parse as
    numbers (comma-tolerant), exact string equality otherwise."""
    try:
        return abs(float(str(got).replace(",", "")) - float(str(expected).replace(",", ""))) < 1e-9
    except (ValueError, TypeError):
        return str(got).strip() == str(expected).strip()


def _bucket(title: str, items: list[str]) -> list[str]:
    out = [title]
    if items:
        out.extend(f"  - {i}" for i in items)
    else:
        out.append("  (none)")
    return out


def cmd_verify(args) -> int:
    task, draft = _read(args.task), _read(args.draft)
    contract = _load_contract(args.contract)
    contract_result = contract_mod.check(contract, draft) if contract else None
    absent = layered.is_absent(draft)
    contract_checks = (
        {"all_required_fields_present": contract_result["all_present"]}
        if contract_result
        else {}
    )

    # Truth buckets. Rules: UNMEASURED never collapses into a verified
    # bucket; a deterministic value check exists ONLY where the contract
    # declares an expected value; cognition has no oracle on this path.
    det_verified: list[str] = []
    con_verified: list[str] = []
    model_assisted: list[str] = []  # no model verifier is configured in the CLI path
    unmeasured: list[str] = []
    failed_items: list[str] = []
    det_checks: dict = {}

    if contract_result:
        for p in contract_result["present"]:
            con_verified.append(f"contract field present: {p['field']}")
        for m in contract_result["missing"]:
            failed_items.append(f"contract field missing: {m['field']}")
        for f in contract.get("fields", []):
            expected = f.get("expected")
            if expected is None:
                continue
            got, _raw = layered.parse_anchored(draft, f["name"])
            key = f"{f['name']}_value"
            if got is None:
                det_checks[key] = None
                unmeasured.append(
                    f"{f['name']} value: no '{f['name']}:' line found — value unmeasurable"
                )
            elif _values_equal(got, expected):
                det_checks[key] = True
                det_verified.append(f"{f['name']}: {got} == expected {expected}")
            else:
                det_checks[key] = False
                failed_items.append(f"{f['name']}: {got} != expected {expected}")
    else:
        unmeasured.append("contract: no contract provided — nothing is contract-verified")

    unmeasured.append("cognition: UNMEASURED (no verifier configured — this is not a pass)")
    if absent:
        unmeasured.append("output: absent/stub — delivery incomplete, nothing measurable")

    verdict = layered.build_layered_verdict(
        cognition_checks={},
        contract_checks=contract_checks,
        deterministic_checks=det_checks,
        absent_output=absent,
    )
    print(json.dumps({"contract": contract_result, "layered_verdict": verdict}, indent=2))
    print()
    report = ["TRUTH REPORT (an empty bucket is an empty bucket, not a pass)"]
    report += _bucket("DETERMINISTICALLY VERIFIED", det_verified)
    report += _bucket("CONTRACT VERIFIED", con_verified)
    report += _bucket("MODEL-ASSISTED CHECK", model_assisted)
    report += _bucket("UNMEASURED", unmeasured)
    report += _bucket("FAILED", failed_items)
    print("\n".join(report))
    return 1 if failed_items else 0


def cmd_loop(args) -> int:
    from piensalo.loop import controller

    return controller.main(args.loop_args)


def _skill_paths(name: str | None = None) -> list[Path]:
    """All skill dirs visible from the CWD plus the built-in library."""
    found: list[Path] = []
    for d in SKILL_DIRS:
        base = Path(d)
        if base.is_dir():
            found.extend(p for p in sorted(base.iterdir()) if p.is_dir())
    if name:
        found = [p for p in found if p.name == name]
    return found


def _lint_skill_text(text: str) -> list[str]:
    problems = []
    if not text.startswith("---"):
        problems.append("missing frontmatter (--- block)")
    if "**Trigger" not in text and "trigger" not in text.lower():
        problems.append("no trigger section")
    if "## Procedure" not in text and "procedure" not in text.lower():
        problems.append("no procedure section")
    for lineno, line in enumerate(text.splitlines(), 1):
        m = ABS_PATH.search(line)
        if m:
            problems.append(f"line {lineno}: absolute path {m.group(0)}")
    return problems


def _expand_skill_arg(p: Path) -> tuple[list[Path], list[str]]:
    """Expand one directory argument to skill dirs.

    A dir containing SKILL.md is itself a skill; otherwise it is treated as
    a parent dir and expands to child dirs containing SKILL.md. Expanding
    to zero skills is an ERROR, never a silent pass.
    """
    if (p / "SKILL.md").is_file():
        return [p], []
    children = [c for c in sorted(p.iterdir()) if c.is_dir() and (c / "SKILL.md").is_file()]
    if not children:
        return [], [f"no skills under {p} (no SKILL.md in it or its child dirs)"]
    return children, []


def cmd_skill(args) -> int:
    action = args.action
    names: list[str] = args.name or []
    first: str | None = names[0] if names else None
    if action == "list":
        for p in _skill_paths():
            print(p)
        print("# built-in repair library:")
        for name in repair_lib.list_repairs():
            print(f"  {name}")
        return 0

    if action == "inspect":
        if not first:
            print("skill inspect requires a NAME", file=sys.stderr)
            return 1
        if first in repair_lib.list_repairs():
            print(repair_lib.load_repair(first))
            return 0
        matches = _skill_paths(first)
        if not matches:
            print(f"skill not found: {first}", file=sys.stderr)
            return 1
        skill_md = matches[0] / "SKILL.md"
        print(_read(str(skill_md)) if skill_md.exists() else f"(no SKILL.md in {matches[0]})")
        return 0

    if action == "lint":
        targets: list[tuple[str, str]] = []
        errors: list[str] = []
        if names:
            for raw in names:
                p = Path(raw)
                if p.is_dir():
                    dirs, errs = _expand_skill_arg(p)
                    errors.extend(errs)
                    targets.extend((str(sd), _read(str(sd / "SKILL.md"))) for sd in dirs)
                elif p.is_file():
                    targets.append((str(p), _read(str(p))))
                elif raw in repair_lib.list_repairs():
                    targets.append((raw, repair_lib.load_repair(raw)))
                else:
                    errors.append(f"skill not found: {raw}")
        else:
            for sp in _skill_paths():
                md = sp / "SKILL.md"
                if md.exists():
                    targets.append((str(sp), _read(str(md))))
            for name in repair_lib.list_repairs():
                targets.append((name, repair_lib.load_repair(name)))
        failed = bool(errors)
        for err in errors:
            print(f"lint error: {err}", file=sys.stderr)
        for name, text in targets:
            problems = _lint_skill_text(text)
            if problems:
                failed = True
                print(f"LINT FAIL {name}:")
                for prob in problems:
                    print(f"  - {prob}")
            else:
                print(f"lint ok: {name}")
        print(f"linted {len(targets)} skill target(s)")
        return 1 if failed else 0

    if action == "export":
        if not first or not args.target:
            print("skill export requires NAME and --target DIR", file=sys.stderr)
            return 1
        matches = _skill_paths(first)
        target = Path(args.target) / first
        if matches:
            shutil.copytree(matches[0], target, dirs_exist_ok=True)
        elif first in repair_lib.list_repairs():
            target.mkdir(parents=True, exist_ok=True)
            (target / "SKILL.md").write_text(
                repair_lib.load_repair(first), encoding="utf-8"
            )
        else:
            print(f"skill not found: {first}", file=sys.stderr)
            return 1
        print(f"exported {first} -> {target}")
        return 0

    if action == "create":
        if not first:
            print("skill create requires a NAME", file=sys.stderr)
            return 1
        target = Path(SKILL_DIRS[0]) / first
        if target.exists():
            print(f"already exists: {target}", file=sys.stderr)
            return 1
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text(
            _SKILL_TEMPLATE.format(name=first), encoding="utf-8"
        )
        print(f"created {target}/SKILL.md")
        return 0

    if action == "scan":
        if not names:
            print("skill scan requires at least one PATH", file=sys.stderr)
            return 1
        skill_dirs: list[Path] = []
        errors = []
        for raw in names:
            p = Path(raw)
            if not p.is_dir():
                errors.append(f"not a directory: {raw}")
                continue
            dirs, errs = _expand_skill_arg(p)
            skill_dirs.extend(dirs)
            errors.extend(errs)
        failed = bool(errors)
        for err in errors:
            print(f"scan error: {err}", file=sys.stderr)
        for sd in skill_dirs:
            findings = scan_skill_dir(sd)
            if not findings:
                print(f"scan clean: {sd} (no findings; not a guarantee of safety)")
                continue
            failed = True
            print(f"SCAN FINDINGS in {sd}:")
            for f in findings:
                print(f"  {f['file']}:{f['line']} [{f['category']}] {f['detail']}")
                if f["excerpt"]:
                    print(f"    > {f['excerpt']}")
        print(f"scanned {len(skill_dirs)} skill package(s)")
        return 1 if failed else 0

    print(f"unknown skill action: {action}", file=sys.stderr)
    return 1


def cmd_doctor(args) -> int:
    ok = True
    vi = sys.version_info
    py_ok = (vi.major, vi.minor) >= (3, 10)
    ok &= py_ok
    print(f"python: {vi.major}.{vi.minor}.{vi.micro} {'ok' if py_ok else 'NEEDS >= 3.10'}")
    for dep in ("anthropic", "openai", "pytest", "ruff"):
        try:
            __import__(dep)
            print(f"optional dep {dep}: present")
        except ImportError:
            print(f"optional dep {dep}: absent (fine — core is stdlib-only)")
    cli = shutil.which("claude")
    print(f"claude CLI: {'present at ' + cli if cli else 'absent (claude-cli adapter unavailable)'}")
    from piensalo.loop.state import LoopPaths

    paths = LoopPaths()
    try:
        paths.ensure()
        probe = paths.state_dir / ".doctor-probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        print(f"state dir writable: {paths.state_dir}")
    except OSError as e:
        ok = False
        print(f"state dir NOT writable: {paths.state_dir} ({e})")
    print("network: not checked (doctor never touches the network)")
    return 0 if ok else 1


def cmd_version(args) -> int:
    print(f"piensalo {piensalo.__version__}")
    return 0


# --------------------------------------------------------------- argparse
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="piensalo",
        description="A cognitive operating layer for AI models (offline-first).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("think", help="compile a task into a cognitive program")
    p.add_argument(
        "task",
        nargs="?",
        default=None,
        help="task file (e.g. TASK.md) or literal task text",
    )
    p.add_argument("--file", default=None, help="explicit task file path (always read as a file)")
    p.add_argument("--text", default=None, help="explicit literal task text (never a file)")
    p.add_argument("--offline", action="store_true", help="never call a model (default without --adapter)")
    p.add_argument("--mode", choices=("prose", "packet", "prompt"), default="prompt")
    p.add_argument("--adapter", help="optional adapter name (manual, claude-cli, openai-compat, ollama)")
    p.add_argument("--model", help="model id for the adapter")
    p.set_defaults(func=cmd_think)

    for name, func, needs_contract in (
        ("inspect", cmd_inspect, True),
        ("repair", cmd_repair, True),
        ("verify", cmd_verify, True),
    ):
        p = sub.add_parser(name, help=f"{name} a draft against its task")
        p.add_argument("--task", required=True)
        p.add_argument("--draft", required=True)
        if needs_contract:
            p.add_argument("--contract", default=None)
        if name == "inspect":
            p.add_argument("--max-repairs", type=int, default=1)
        if name == "repair":
            p.add_argument(
                "--adapter",
                choices=("manual", "claude-cli", "openai", "ollama"),
                default=None,
                help="run the repair packet through a model adapter "
                "(default: offline packet only, nothing applied)",
            )
            p.add_argument("--model", default=None, help="model id for the adapter")
            p.add_argument(
                "--output",
                default=None,
                help="repaired-draft path (default: <draft-stem>.repaired.md next to the draft)",
            )
            p.add_argument("--force", action="store_true", help="overwrite an existing output file")
            p.add_argument(
                "--response-file",
                default=None,
                help="manual adapter only: read the model response from this file",
            )
        p.set_defaults(func=func)

    from piensalo.context.cli import add_context_parser

    add_context_parser(sub)

    from piensalo.gateway.cli import add_gateway_parser

    add_gateway_parser(sub)

    p = sub.add_parser("loop", help="bounded loop controller")
    p.add_argument("loop_args", nargs=argparse.REMAINDER, help="loop subcommand and args")
    p.set_defaults(func=cmd_loop)

    p = sub.add_parser("skill", help="manage skill directories")
    p.add_argument("action", choices=("list", "inspect", "export", "lint", "create", "scan"))
    p.add_argument(
        "name",
        nargs="*",
        help="skill name(s) or path(s); lint/scan accept multiple skill dirs "
        "or parent dirs of skill dirs",
    )
    p.add_argument("--target", help="target directory for export")
    p.set_defaults(func=cmd_skill)

    p = sub.add_parser("doctor", help="environment checks (offline)")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("version", help="print version")
    p.set_defaults(func=cmd_version)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Console-script entry point; returns an exit code."""
    args = _build_parser().parse_args(argv)
    try:
        return args.func(args)
    except FileNotFoundError as e:
        print(f"piensalo: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
