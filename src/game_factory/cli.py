from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from game_factory import __version__
from game_factory.config import load_config
from game_factory.gates.runner import verify
from game_factory.state import load_state
from game_factory.adapters.orca import client as orca_client
from game_factory.assets.providers import opensource as oss_assets
from game_factory.migrations.runner import run_migrations
from game_factory.onboard import format_onboard_line, run_onboard
from game_factory.paths import join_project, relpath
from game_factory.production import worktrees
from game_factory.production.producer import close_batch, plan_batch, production_status
from game_factory.production.verifier import independent_verify
from game_factory.transitions import transition


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


def cmd_onboard(args: argparse.Namespace) -> int:
    root = Path(args.project).resolve()
    report = run_onboard(root)
    print(json.dumps(report, indent=2))
    print(format_onboard_line(report), file=sys.stderr)
    return 0 if report["ok"] else 1


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


def cmd_migrate(args: argparse.Namespace) -> int:
    root = Path(args.project).resolve()
    result = run_migrations(root, __version__)
    print(json.dumps(result, indent=2))
    return 0


def cmd_assets_search(args: argparse.Namespace) -> int:
    root = Path(args.project).resolve()
    hits = oss_assets.search_catalog(root, args.query, args.license)
    print(json.dumps({"results": hits}, indent=2))
    return 0


def cmd_orca_dispatch(args: argparse.Namespace) -> int:
    root = Path(args.project).resolve()
    cfg = load_config(root)
    pid = cfg.get("orchestration", {}).get("orca_project_id")
    out = orca_client.dispatch(root, join_project(root, args.work_order), orca_project_id=pid)
    print(json.dumps(out, indent=2))
    return 0


def cmd_orca_status(args: argparse.Namespace) -> int:
    root = Path(args.project).resolve()
    print(json.dumps(orca_client.status(root, args.job_id), indent=2))
    return 0


def cmd_orca_collect(args: argparse.Namespace) -> int:
    root = Path(args.project).resolve()
    print(json.dumps(orca_client.collect(root, args.job_id), indent=2))
    return 0


def cmd_orca_cancel(args: argparse.Namespace) -> int:
    root = Path(args.project).resolve()
    print(json.dumps(orca_client.cancel(root, args.job_id), indent=2))
    return 0


def cmd_worktree_add(args: argparse.Namespace) -> int:
    root = Path(args.project).resolve()
    path = worktrees.create_writer_worktree(root, args.zone, args.writer)
    print(json.dumps({"worktree": relpath(root, path)}, indent=2))
    return 0


def cmd_worktree_remove(args: argparse.Namespace) -> int:
    root = Path(args.project).resolve()
    worktrees.remove_writer_worktree(root, args.zone, args.writer)
    print(json.dumps({"ok": True}, indent=2))
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

    p_onboard = sub.add_parser("onboard", help="Verify files and toolchain after install")
    p_onboard.set_defaults(func=cmd_onboard)

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

    p_mig = sub.add_parser("migrate")
    p_mig.set_defaults(func=cmd_migrate)

    p_assets = sub.add_parser("assets")
    assets_sub = p_assets.add_subparsers(dest="assets_cmd", required=True)
    p_search = assets_sub.add_parser("search")
    p_search.add_argument("query", default="", nargs="?")
    p_search.add_argument("--license", default=None)
    p_search.set_defaults(func=cmd_assets_search)

    p_orca = sub.add_parser("orca")
    orca_sub = p_orca.add_subparsers(dest="orca_cmd", required=True)
    p_od = orca_sub.add_parser("dispatch")
    p_od.add_argument("--work-order", required=True)
    p_od.set_defaults(func=cmd_orca_dispatch)
    p_os = orca_sub.add_parser("status")
    p_os.add_argument("--job-id", required=True)
    p_os.set_defaults(func=cmd_orca_status)
    p_oc = orca_sub.add_parser("collect")
    p_oc.add_argument("--job-id", required=True)
    p_oc.set_defaults(func=cmd_orca_collect)
    p_ox = orca_sub.add_parser("cancel")
    p_ox.add_argument("--job-id", required=True)
    p_ox.set_defaults(func=cmd_orca_cancel)

    p_wt = sub.add_parser("worktree")
    wt_sub = p_wt.add_subparsers(dest="wt_cmd", required=True)
    p_wa = wt_sub.add_parser("add")
    p_wa.add_argument("--zone", required=True)
    p_wa.add_argument("--writer", required=True)
    p_wa.set_defaults(func=cmd_worktree_add)
    p_wr = wt_sub.add_parser("remove")
    p_wr.add_argument("--zone", required=True)
    p_wr.add_argument("--writer", required=True)
    p_wr.set_defaults(func=cmd_worktree_remove)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
