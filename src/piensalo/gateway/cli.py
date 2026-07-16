"""CLI wiring for the Cortex Gateway: ``piensalo serve`` and
``piensalo gateway <status|inspect|report|replay|doctor>``.

Follows the repo convention: this module exposes ``add_gateway_parser(sub)``
which the top-level CLI calls to register subcommands, each with a ``func``.

Security-sensitive values (auth token, upstream API key) are read from the
environment by name rather than accepted as literal flags, to keep secrets out
of shell history and process listings.
"""
from __future__ import annotations

import argparse
import os

from . import report as gwreport
from .config import ConfigError, GatewayConfig


def _config_from_args(args) -> GatewayConfig:
    auth_token = os.environ.get(args.auth_token_env) if args.auth_token_env else None
    upstream_key = os.environ.get(args.upstream_key_env) if args.upstream_key_env else None
    return GatewayConfig.build(
        mode=args.mode,
        bind_host=args.bind,
        bind_port=args.port,
        upstream_base_url=args.upstream_base_url or "",
        upstream_model=args.upstream_model or "",
        auth_token=auth_token,
        upstream_api_key=upstream_key,
        allow_non_loopback_bind=args.allow_non_loopback_bind,
        allow_non_loopback_upstream=args.allow_non_loopback_upstream,
        allowed_upstream_prefixes=tuple(args.allowed_upstream or ()),
        no_store=not args.store,
        redact=not args.no_redact,
        retention=args.retention,
        ledger_dir=args.ledger_dir,
    )


def cmd_serve(args) -> int:
    from .server import serve  # local import: server pulls in http.server

    try:
        cfg = _config_from_args(args)
    except ConfigError as e:
        print(f"piensalo serve: {e}", flush=True)
        return 2
    if not cfg.upstream_base_url:
        print("piensalo serve: --upstream-base-url is required", flush=True)
        return 2
    try:
        server = serve(cfg)
    except ValueError as e:
        print(f"piensalo serve: {e}", flush=True)
        return 2
    summary = cfg.public_summary()
    print(
        f"PIÉNSALO Cortex Gateway [observe] listening on "
        f"http://{summary['bind']}  ->  {summary['upstream_base_url']}",
        flush=True,
    )
    print(
        "  observe mode: traffic is forwarded unchanged; router runs in shadow; "
        "events are recorded locally. This does not modify responses.",
        flush=True,
    )
    print(f"  ledger: {cfg.ledger_dir}/events.jsonl   auth: {'on' if cfg.auth_token else 'off'}",
          flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\npiensalo serve: shutting down", flush=True)
    finally:
        server.server_close()
    return 0


def cmd_gateway(args) -> int:
    action = args.action
    if action == "status":
        cfg = None
        if args.upstream_base_url:
            try:
                cfg = _config_from_args(args)
            except ConfigError:
                cfg = None
        print(gwreport.render_terminal(gwreport.status(args.ledger_dir, cfg)))
    elif action == "inspect":
        print(gwreport.render_terminal(gwreport.inspect(args.ledger_dir, args.last)))
    elif action == "report":
        print(gwreport.render_terminal(gwreport.report(args.ledger_dir)))
    elif action == "replay":
        if not args.request_id:
            print("piensalo gateway replay: --request-id is required", flush=True)
            return 2
        row = gwreport.replay(args.ledger_dir, args.request_id)
        if row is None:
            print(f"piensalo gateway: no event with request_id {args.request_id!r}", flush=True)
            return 1
        print(gwreport.render_terminal(row))
    elif action == "doctor":
        cfg = None
        if args.upstream_base_url:
            try:
                cfg = _config_from_args(args)
            except ConfigError as e:
                print(gwreport.render_terminal({"ok": False, "config_error": str(e)}))
                return 1
        result = gwreport.doctor(cfg, args.ledger_dir)
        print(gwreport.render_terminal(result))
        return 0 if result["ok"] else 1
    return 0


def _add_common_config_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--mode", choices=("observe",), default="observe",
                   help="gateway mode (only 'observe' is implemented)")
    p.add_argument("--bind", default="127.0.0.1", help="bind host (loopback by default)")
    p.add_argument("--port", type=int, default=8788, help="bind port")
    p.add_argument("--upstream-base-url", default=None,
                   help="upstream OpenAI-compatible base URL, e.g. http://127.0.0.1:11434/v1")
    p.add_argument("--upstream-model", default=None, help="upstream model id (for the record)")
    p.add_argument("--auth-token-env", default=None,
                   help="env var name holding the gateway bearer token (clients must present it)")
    p.add_argument("--upstream-key-env", default=None,
                   help="env var name holding the upstream API key (replaces client Authorization)")
    p.add_argument("--allow-non-loopback-bind", action="store_true",
                   help="permit binding a non-loopback host (off by default; fail-closed)")
    p.add_argument("--allow-non-loopback-upstream", action="store_true",
                   help="permit a private-network upstream address")
    p.add_argument("--allowed-upstream", action="append", default=None,
                   help="allow-list prefix for the upstream URL (repeatable)")
    p.add_argument("--store", action="store_true",
                   help="retain request/response bodies (default: do NOT store)")
    p.add_argument("--no-redact", action="store_true",
                   help="do not redact non-secret header values (secrets are always dropped)")
    p.add_argument("--retention", choices=("hashes", "metadata", "full"), default="hashes",
                   help="ledger retention level (default: hashes)")
    p.add_argument("--ledger-dir", default=".piensalo/gateway", help="event ledger directory")


def add_gateway_parser(sub) -> None:
    p = sub.add_parser("serve", help="run the Cortex Gateway (observe mode)")
    _add_common_config_flags(p)
    p.set_defaults(func=cmd_serve)

    g = sub.add_parser("gateway", help="inspect the local gateway event ledger")
    g.add_argument("action", choices=("status", "inspect", "report", "replay", "doctor"))
    g.add_argument("--ledger-dir", default=".piensalo/gateway", help="event ledger directory")
    g.add_argument("--last", type=int, default=20, help="inspect: number of recent events")
    g.add_argument("--request-id", default=None, help="replay: request id to show")
    # doctor/status can optionally validate a config:
    g.add_argument("--mode", choices=("observe",), default="observe")
    g.add_argument("--bind", default="127.0.0.1")
    g.add_argument("--port", type=int, default=8788)
    g.add_argument("--upstream-base-url", default=None)
    g.add_argument("--upstream-model", default=None)
    g.add_argument("--auth-token-env", default=None)
    g.add_argument("--upstream-key-env", default=None)
    g.add_argument("--allow-non-loopback-bind", action="store_true")
    g.add_argument("--allow-non-loopback-upstream", action="store_true")
    g.add_argument("--allowed-upstream", action="append", default=None)
    g.add_argument("--store", action="store_true")
    g.add_argument("--no-redact", action="store_true")
    g.add_argument("--retention", choices=("hashes", "metadata", "full"), default="hashes")
    g.set_defaults(func=cmd_gateway)
