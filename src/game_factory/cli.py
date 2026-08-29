from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from game_factory import __version__
from game_factory.config import load_config
from game_factory.gates.runner import verify
from game_factory.state import load_state
from game_factory.production.producer import close_batch, plan_batch, production_status
from game_factory.production.verifier import independent_verify
from game_factory.transitions import transition


def _repo_root() -> Path:
    return Path.cwd()


def cmd_status(args: argparse.Namespace) -> int:
    root = Path(args.project).resolve()
    state = load_state(root)
    try:
        cfg = load_config(root)
    except FileNotFoundError:
        cfg = None
    out = {"factory_version": __version__, "state": state, "config_loaded": cfg is not None}
    print(json.dumps(out, indent=2))
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    root = Path(args.project).resolve()
    result = verify(root, args.profile)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


def cmd_produce_plan(args: argparse.Namespace) -> int:
    root = Path(args.project).resolve()
    wo = plan_batch(root)
    print(json.dumps({"work_order": wo}, indent=2))
    return 0 if wo else 2


def cmd_produce_close(args: argparse.Namespace) -> int:
    root = Path(args.project).resolve()
    result = close_batch(root, args.work_order)
    print(json.dumps(result, indent=2))
    return 0 if result["gate"]["ok"] else 1


def cmd_produce_status(args: argparse.Namespace) -> int:
    root = Path(args.project).resolve()
    print(json.dumps(production_status(root), indent=2))
    return 0


def cmd_verify_release(args: argparse.Namespace) -> int:
    root = Path(args.project).resolve()
    result = independent_verify(root)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


def cmd_transition(args: argparse.Namespace) -> int:
    root = Path(args.project).resolve()
    transition(root, args.to, args.reason)
    return 0


def cmd_validate_config(args: argparse.Namespace) -> int:
    root = Path(args.project).resolve()
    load_config(root)
    print("ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="game-factory")
    parser.add_argument("--project", default=".", help="Game project root")
    sub = parser.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status")
    p_status.set_defaults(func=cmd_status)

    p_val = sub.add_parser("validate-config")
    p_val.set_defaults(func=cmd_validate_config)

    p_verify = sub.add_parser("verify")
    p_verify.add_argument("profile", choices=["fast", "full", "visual"])
    p_verify.set_defaults(func=cmd_verify)

    p_tr = sub.add_parser("transition")
    p_tr.add_argument("--to", required=True)
    p_tr.add_argument("--reason", default="cli")
    p_tr.set_defaults(func=cmd_transition)

    p_prod = sub.add_parser("produce")
    prod_sub = p_prod.add_subparsers(dest="produce_cmd", required=True)
    p_plan = prod_sub.add_parser("plan")
    p_plan.set_defaults(func=cmd_produce_plan)
    p_close = prod_sub.add_parser("close")
    p_close.add_argument("--work-order", required=True)
    p_close.set_defaults(func=cmd_produce_close)
    p_pstat = prod_sub.add_parser("status")
    p_pstat.set_defaults(func=cmd_produce_status)

    p_vrel = sub.add_parser("verify-release")
    p_vrel.set_defaults(func=cmd_verify_release)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
