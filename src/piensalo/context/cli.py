"""`piensalo context` subcommands: compile / inspect / verify / diff.

All four are offline and provider-independent: no model call, no network,
no credential, no SDK. Exit codes: 0 success (including qualified), 1
UNSAFE TO RESUME, 2 usage or input error, 3 REQUIRES EXPANSION (honest
budget refusal).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from piensalo.context import diff as diff_mod
from piensalo.context import schema, verify
from piensalo.context.compiler import CompileError, compile_to_dir
from piensalo.context.parser import ParseError
from piensalo.context.tokens import ESTIMATOR, estimate_tokens

EXIT_OK = 0
EXIT_UNSAFE = 1
EXIT_USAGE = 2
EXIT_EXPANSION = 3

_VERDICT_EXIT = {
    "DETERMINISTICALLY VERIFIED": EXIT_OK,
    "SAFE WITH QUALIFICATIONS": EXIT_OK,
    "REQUIRES EXPANSION": EXIT_EXPANSION,
    "UNSAFE TO RESUME": EXIT_UNSAFE,
    "UNMEASURED": EXIT_UNSAFE,
}


def cmd_compile(args) -> int:
    try:
        result = compile_to_dir(
            args.transcript,
            args.output,
            goal=args.goal,
            token_budget=args.budget,
            fmt=args.format,
            project_state_path=args.project_state,
            source_model=args.source_model,
            target_model=args.target_model,
        )
    except (CompileError, ParseError) as e:
        print(f"piensalo context compile: {e}", file=sys.stderr)
        return EXIT_USAGE
    out = Path(args.output)
    m = result.capsule["metrics"]
    print(f"wrote {out / 'capsule.json'}")
    print(f"wrote {out / 'resume.md'}")
    print(f"wrote {out / 'verification.json'}")
    print(f"capsule_id: {result.capsule['capsule_id']}")
    print(f"tokens (estimates, {ESTIMATOR}): original "
          f"{m['original_tokens_est']}, resume {m['resume_tokens_est']}, "
          f"budget {m['token_budget']}")
    print(f"verdict: {result.verification['verdict']}")
    print("behavioral equivalence: UNMEASURED (not a claim of equivalence)")
    if result.refused:
        print("resume.md is an honest refusal: the critical working set does "
              "not fit the budget", file=sys.stderr)
        return EXIT_EXPANSION
    return EXIT_OK


def _resolve_bundle(path: str) -> tuple[Path, dict]:
    p = Path(path)
    capsule = schema.load_capsule(str(p))  # raises ValueError with specifics
    directory = p if p.is_dir() else p.parent
    return directory, capsule


def _print_records(title: str, records: list[dict]) -> None:
    if not records:
        return
    print(f"\n{title}:")
    for rec in records:
        first = rec["content"].split("\n")[0]
        extra = f" (expires: {rec['expiry']})" if rec.get("expiry") else ""
        print(f"  [{rec['id']}] ({rec['exactness']}){extra} {first}")
        for line in rec["content"].split("\n")[1:]:
            print(f"      {line}")


def cmd_inspect(args) -> int:
    try:
        directory, capsule = _resolve_bundle(args.path)
    except ValueError as e:
        print(f"piensalo context inspect: {e}", file=sys.stderr)
        return EXIT_USAGE
    m = capsule["metrics"]
    print(f"capsule: {capsule['capsule_id']}  ({capsule['schema_version']})")
    print(f"compiled for goal: {capsule['compiled_for']['goal']}")
    src_model = capsule["compiled_for"]["source_model"]
    tgt_model = capsule["compiled_for"]["target_model"]
    print(f"source model: {src_model or '(unrecorded — optional metadata)'}")
    print(f"target model: {tgt_model or '(any — capsule is model-independent)'}")
    print(f"\nmission objective: {capsule['mission']['objective'] or '(none declared)'}")
    for sc in capsule["mission"]["success_conditions"]:
        print(f"  success condition: {sc}")

    decisions = capsule["decisions"]
    _print_records("ACTIVE decisions",
                   [r for r in decisions if r["status"] == "ACTIVE"])
    _print_records("SUPERSEDED decisions (historical truth, not current)",
                   [r for r in decisions if r["status"] == "SUPERSEDED"])
    _print_records("CONTESTED decisions",
                   [r for r in decisions if r["status"] == "CONTESTED"])
    _print_records("Other-status decisions (TEMPORARY/EXPIRED/UNVERIFIED)",
                   [r for r in decisions if r["status"] in
                    ("TEMPORARY", "EXPIRED", "UNVERIFIED")])
    _print_records("Critical constraints and invariants", capsule["invariants"])
    _print_records("Completed work", capsule["completed"])
    _print_records("Failed approaches", capsule["failed_approaches"])
    _print_records("Open questions", capsule["open_questions"])
    _print_records("Open actions", capsule["open_actions"])
    _print_records("Stop conditions", capsule["stop_conditions"])
    print(f"\nnext action: {capsule['next_action'] or '(none declared)'}")

    print("\nexact references:")
    for name in sorted(capsule["references"]):
        ref = capsule["references"][name]
        print(f"  {name}: {ref['location']} sha256={ref['content_hash'][:16]}... "
              f"({ref['access_policy']})")
    if capsule["known_omissions"]:
        print("\nknown omissions:")
        for om in capsule["known_omissions"]:
            print(f"  [{om.get('kind')}] lines {om.get('lines')}: "
                  f"{om.get('preview', '')}")
    print(f"\nrisk: behavioral_equivalence={capsule['risk']['behavioral_equivalence']}")
    for note in capsule["risk"]["notes"]:
        print(f"  note: {note}")

    capsule_tokens = estimate_tokens(
        (directory / "capsule.json").read_text(encoding="utf-8")
        if (directory / "capsule.json").is_file()
        else schema.canonical_json(capsule))
    resume_path = directory / "resume.md"
    resume_tokens = (estimate_tokens(resume_path.read_text(encoding="utf-8"))
                     if resume_path.is_file() else None)
    verif_path = directory / "verification.json"
    verif_tokens = (estimate_tokens(verif_path.read_text(encoding="utf-8"))
                    if verif_path.is_file() else None)
    print(f"\ntoken estimates ({ESTIMATOR}):")
    print(f"  original transcript: {m['original_tokens_est']}")
    print(f"  capsule.json:        {capsule_tokens}")
    print(f"  resume.md:           {resume_tokens if resume_tokens is not None else '(missing)'}")
    print(f"  verification.json:   {verif_tokens if verif_tokens is not None else '(missing)'}")
    if resume_tokens:
        print(f"  gross compression ratio (original/resume): "
              f"{round(m['original_tokens_est'] / resume_tokens, 2)}")
    print("\nbehavioral equivalence: UNMEASURED — this inspection describes "
          "structure only,")
    print("not whether a resumed model behaves like the full-history model.")
    return EXIT_OK


def cmd_verify(args) -> int:
    try:
        report = verify.verify_dir(args.path,
                                   transcript_override=args.transcript)
    except ValueError as e:
        print(f"piensalo context verify: {e}", file=sys.stderr)
        return EXIT_USAGE
    print(json.dumps(report, indent=2, sort_keys=True))
    print(f"\nverdict: {report['verdict']}")
    print("behavioral equivalence: UNMEASURED (never converted into a pass "
          "by structural checks)")
    return _VERDICT_EXIT[report["verdict"]]


def cmd_diff(args) -> int:
    try:
        d = diff_mod.diff_paths(args.capsule_a, args.capsule_b)
    except ValueError as e:
        print(f"piensalo context diff: {e}", file=sys.stderr)
        return EXIT_USAGE
    if args.json:
        print(schema.canonical_json(d), end="")
    else:
        print(diff_mod.render_diff(d))
    return EXIT_OK


def add_context_parser(sub) -> None:
    """Wire `piensalo context ...` into the main argparse tree."""
    p = sub.add_parser(
        "context",
        help="compile long transcripts into verified continuation capsules "
             "(offline, model-independent)",
    )
    csub = p.add_subparsers(dest="context_command", required=True)

    c = csub.add_parser("compile", help="transcript -> capsule.json + "
                                        "resume.md + verification.json")
    c.add_argument("transcript", help="plain-text or JSONL transcript file")
    c.add_argument("--goal", required=True, help="the declared next goal")
    c.add_argument("--budget", required=True, type=int,
                   help="token budget for resume.md (estimate)")
    c.add_argument("--output", required=True, help="output directory")
    c.add_argument("--format", choices=("text", "jsonl"), default=None,
                   help="transcript format (default: by file extension)")
    c.add_argument("--project-state", default=None,
                   help="optional project-state JSON file")
    c.add_argument("--source-model", default=None,
                   help="optional provenance metadata: model that produced "
                        "the transcript (any provider)")
    c.add_argument("--target-model", default=None,
                   help="optional metadata: intended consumer model "
                        "(any provider; capsule works regardless)")
    c.set_defaults(func=cmd_compile)

    c = csub.add_parser("inspect", help="human-readable capsule view")
    c.add_argument("path", help="output directory or capsule.json")
    c.set_defaults(func=cmd_inspect)

    c = csub.add_parser("verify", help="deterministic structural checks -> verdict")
    c.add_argument("path", help="output directory or capsule.json")
    c.add_argument("--transcript", default=None,
                   help="transcript path (default: capsule.source_path)")
    c.set_defaults(func=cmd_verify)

    c = csub.add_parser("diff", help="compare two capsules")
    c.add_argument("capsule_a", help="first output dir or capsule.json")
    c.add_argument("capsule_b", help="second output dir or capsule.json")
    c.add_argument("--json", action="store_true",
                   help="machine-readable canonical JSON output")
    c.set_defaults(func=cmd_diff)
