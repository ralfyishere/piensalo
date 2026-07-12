"""fable-think CLI: think / inspect / repair / verify / loop / skill / doctor / version.

Offline-first: ``think`` compiles a cognitive program without any model
call; ``inspect``/``repair``/``verify`` are deterministic scans of real
drafts; ``loop`` delegates to the bounded loop controller; ``skill``
manages skill directories (including the security scan); ``doctor`` checks
the environment without touching the network. A model is only executed
when the operator explicitly configures an adapter.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import fable_think
from fable_think import repair as repair_lib
from fable_think.compiler import compile_program
from fable_think.inspect import scanner
from fable_think.security import scan_skill_dir
from fable_think.security.skill_scan import ABS_PATH
from fable_think.verify import contract as contract_mod
from fable_think.verify import layered

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


# ------------------------------------------------------------ subcommands
def cmd_think(args) -> int:
    task = _read(args.task)
    if args.adapter and not args.offline:
        from fable_think.adapters import get_adapter

        if args.adapter != "manual" and not args.model:
            print("fable-think think: --adapter requires --model", file=sys.stderr)
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


def cmd_repair(args) -> int:
    task, draft = _read(args.task), _read(args.draft)
    contract = _load_contract(args.contract)
    result = scanner.scan(task, draft, contract, max_repairs=1)
    if result["no_repair_needed"]:
        print("NO REPAIR NEEDED — no observable defect cleared the activation threshold.")
        return 0
    skill = result["selected_repairs"][0]
    print(f"# Selected repair: {skill} (defect: {result['verification_target']})")
    print("# Smallest justified repair — apply it to the demonstrated defect only;")
    print("# preserve every correct portion of the draft.")
    for line in result["evidence_from_draft"]:
        print(f"# evidence: {line}")
    print()
    print(repair_lib.load_repair(skill))
    return 0


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
    # No cognition oracle is configured in the generic CLI path, so the
    # cognition layer is UNMEASURED unless the output is absent (rule 3).
    verdict = layered.build_layered_verdict(
        cognition_checks={},
        contract_checks=contract_checks,
        deterministic_checks={},
        absent_output=absent,
    )
    print(json.dumps({"contract": contract_result, "layered_verdict": verdict}, indent=2))
    return 0


def cmd_loop(args) -> int:
    from fable_think.loop import controller

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


def cmd_skill(args) -> int:
    action = args.action
    if action == "list":
        for p in _skill_paths():
            print(p)
        print("# built-in repair library:")
        for name in repair_lib.list_repairs():
            print(f"  {name}")
        return 0

    if action == "inspect":
        if not args.name:
            print("skill inspect requires a NAME", file=sys.stderr)
            return 1
        if args.name in repair_lib.list_repairs():
            print(repair_lib.load_repair(args.name))
            return 0
        matches = _skill_paths(args.name)
        if not matches:
            print(f"skill not found: {args.name}", file=sys.stderr)
            return 1
        skill_md = matches[0] / "SKILL.md"
        print(_read(str(skill_md)) if skill_md.exists() else f"(no SKILL.md in {matches[0]})")
        return 0

    if action == "lint":
        targets: list[tuple[str, str]] = []
        if args.name:
            p = Path(args.name)
            if p.is_dir():
                md = p / "SKILL.md"
                if not md.exists():
                    print(f"LINT FAIL {p}: no SKILL.md", file=sys.stderr)
                    return 1
                targets.append((str(p), _read(str(md))))
            elif p.is_file():
                targets.append((str(p), _read(str(p))))
            elif args.name in repair_lib.list_repairs():
                targets.append((args.name, repair_lib.load_repair(args.name)))
            else:
                print(f"skill not found: {args.name}", file=sys.stderr)
                return 1
        else:
            for sp in _skill_paths():
                md = sp / "SKILL.md"
                if md.exists():
                    targets.append((str(sp), _read(str(md))))
            for name in repair_lib.list_repairs():
                targets.append((name, repair_lib.load_repair(name)))
        failed = False
        for name, text in targets:
            problems = _lint_skill_text(text)
            if problems:
                failed = True
                print(f"LINT FAIL {name}:")
                for prob in problems:
                    print(f"  - {prob}")
            else:
                print(f"lint ok: {name}")
        return 1 if failed else 0

    if action == "export":
        if not args.name or not args.target:
            print("skill export requires NAME and --target DIR", file=sys.stderr)
            return 1
        matches = _skill_paths(args.name)
        target = Path(args.target) / args.name
        if matches:
            shutil.copytree(matches[0], target, dirs_exist_ok=True)
        elif args.name in repair_lib.list_repairs():
            target.mkdir(parents=True, exist_ok=True)
            (target / "SKILL.md").write_text(
                repair_lib.load_repair(args.name), encoding="utf-8"
            )
        else:
            print(f"skill not found: {args.name}", file=sys.stderr)
            return 1
        print(f"exported {args.name} -> {target}")
        return 0

    if action == "create":
        if not args.name:
            print("skill create requires a NAME", file=sys.stderr)
            return 1
        target = Path(SKILL_DIRS[0]) / args.name
        if target.exists():
            print(f"already exists: {target}", file=sys.stderr)
            return 1
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text(
            _SKILL_TEMPLATE.format(name=args.name), encoding="utf-8"
        )
        print(f"created {target}/SKILL.md")
        return 0

    if action == "scan":
        if not args.name:
            print("skill scan requires a PATH", file=sys.stderr)
            return 1
        findings = scan_skill_dir(args.name)
        if not findings:
            print(f"scan clean: {args.name} (no findings; not a guarantee of safety)")
            return 0
        print(f"SCAN FINDINGS in {args.name}:")
        for f in findings:
            print(f"  {f['file']}:{f['line']} [{f['category']}] {f['detail']}")
            if f["excerpt"]:
                print(f"    > {f['excerpt']}")
        return 1

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
    from fable_think.loop.state import LoopPaths

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
    print(f"fable-think {fable_think.__version__}")
    return 0


# --------------------------------------------------------------- argparse
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fable-think",
        description="A cognitive operating layer for AI models (offline-first).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("think", help="compile a task into a cognitive program")
    p.add_argument("task", help="path to the task file (e.g. TASK.md)")
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
        p.set_defaults(func=func)

    p = sub.add_parser("loop", help="bounded loop controller")
    p.add_argument("loop_args", nargs=argparse.REMAINDER, help="loop subcommand and args")
    p.set_defaults(func=cmd_loop)

    p = sub.add_parser("skill", help="manage skill directories")
    p.add_argument("action", choices=("list", "inspect", "export", "lint", "create", "scan"))
    p.add_argument("name", nargs="?", help="skill name or path")
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
        print(f"fable-think: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
