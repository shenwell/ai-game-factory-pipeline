#!/usr/bin/env python3
"""Init, upgrade, and overlay install for ai-game-factory projects."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

FACTORY_VERSION = "1.1.3"
FORBIDDEN_IN_TARGET = {".git"}


def _result_payload(target: Path, mode: str, **extra) -> dict:
    payload = {"ok": True, "path": Path(target).as_posix(), "factory_version": FACTORY_VERSION, "mode": mode}
    payload.update(extra)
    return payload


def _onboard_report(target: Path) -> dict:
    src = Path(__file__).resolve().parents[1] / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    from game_factory.onboard import format_onboard_line, run_onboard

    report = run_onboard(target.resolve())
    print(format_onboard_line(report), file=sys.stderr)
    return report


def _emit(payload: dict, target: Path) -> None:
    payload["onboard"] = _onboard_report(target)
    print(json.dumps(payload, indent=2))


def _is_empty_dir(path: Path) -> bool:
    if not path.exists():
        return True
    entries = [p for p in path.iterdir() if p.name not in FORBIDDEN_IN_TARGET]
    return len(entries) == 0


def _is_godot_project(path: Path) -> bool:
    return (path / "project.godot").exists()


def _is_factory_project(path: Path) -> bool:
    return (path / ".game-factory" / "install-manifest.json").exists()


def _copy_tree(src: Path, dst: Path, *, skip_existing: bool = False) -> None:
    if not src.exists():
        return
    if src.is_file():
        if skip_existing and dst.exists():
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return
    dst.mkdir(parents=True, exist_ok=True)
    for child in src.iterdir():
        _copy_tree(child, dst / child.name, skip_existing=skip_existing)


def _publish_skills(factory_root: Path, target: Path) -> None:
    vendor = factory_root / "vendor"
    agents = target / ".agents" / "skills"
    cursor = target / ".cursor" / "skills"
    agents.mkdir(parents=True, exist_ok=True)
    cursor.mkdir(parents=True, exist_ok=True)

    _copy_tree(vendor / "game-design", agents / "game-design")
    _copy_tree(vendor / "game-design", cursor / "game-design")

    skill_src = vendor / "godogen" / "asset-gen"
    kie_patch = factory_root / "vendor" / "patches" / "asset-gen-SKILL-kie-only.md"
    _copy_tree(skill_src, agents / "asset-gen")
    _copy_tree(skill_src, cursor / "asset-gen")
    if kie_patch.exists():
        shutil.copy2(kie_patch, agents / "asset-gen" / "SKILL.md")
        shutil.copy2(kie_patch, cursor / "asset-gen" / "SKILL.md")

    _copy_tree(vendor / "godot_cli_control" / "skill", agents / "godot-cli-control")
    _copy_tree(vendor / "godot_cli_control" / "skill", cursor / "godot-cli-control")

    for ui_skill in ("game-ui-ux", "godot-ui-control", "input-systems"):
        src = vendor / ui_skill
        if src.exists():
            _copy_tree(src, agents / ui_skill)
            _copy_tree(src, cursor / ui_skill)

    for name in (
        "game-factory-mvp",
        "game-factory-produce",
        "game-factory-playtest",
        "game-factory-status",
        "game-factory-config",
        "game-factory-onboard",
        "game-factory-ui",
    ):
        src = factory_root / "templates" / "skills" / name
        if src.exists():
            _copy_tree(src, agents / name)
            _copy_tree(src, cursor / name)


def _write_initial_state(target: Path) -> None:
    gf = target / ".game-factory"
    gf.mkdir(parents=True, exist_ok=True)
    state_path = gf / "state.json"
    if state_path.exists():
        return
    state = {
        "schema_version": 1,
        "phase": "bootstrap",
        "iteration": 0,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "blockers": [],
        "approval_hashes": {},
        "retry_counts": {},
    }
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    events = gf / "events.jsonl"
    if not events.exists():
        events.write_text("", encoding="utf-8")
    (gf / "jobs").mkdir(exist_ok=True)
    (gf / "runtime").mkdir(exist_ok=True)


def _write_manifest(factory_root: Path, target: Path) -> None:
    vendor_lock = factory_root / "vendor" / "VENDOR.lock"
    manifest_path = target / ".game-factory" / "install-manifest.json"
    existing = {}
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest = {
        "factory_version": FACTORY_VERSION,
        "installed_at": existing.get("installed_at") or datetime.now(timezone.utc).isoformat(),
        "vendor_lock": json.loads(vendor_lock.read_text(encoding="utf-8")) if vendor_lock.exists() else {},
        "paths": {
            "studio": ".game-factory/vendor/gamestudio",
            "godot_guide": "godot.md",
            "asset_catalog": ".game-factory/vendor/asset-catalog/kenney-index.json",
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _overlay_factory(factory_root: Path, target: Path, *, skip_existing_docs: bool = False) -> None:
    templates = factory_root / "templates" / "project"
    _copy_tree(templates / "docs", target / "docs", skip_existing=skip_existing_docs)
    for name in ("GAME.md", "AGENTS.md", "game-factory.config.yaml", ".env.example"):
        src = templates / name
        if src.exists():
            _copy_tree(src, target / name, skip_existing=True)
    if not (target / "godot.md").exists():
        _copy_tree(factory_root / "vendor" / "godogen" / "engines" / "godot.md", target / "godot.md")
    _copy_tree(factory_root / "vendor" / "gamestudio", target / ".game-factory" / "vendor" / "gamestudio")
    _copy_tree(
        factory_root / "vendor" / "asset-catalog",
        target / ".game-factory" / "vendor" / "asset-catalog",
    )
    addon_dst = target / "addons" / "godot_cli_control"
    if not addon_dst.exists():
        _copy_tree(factory_root / "vendor" / "godot_cli_control" / "addon", addon_dst)
    _publish_skills(factory_root, target)
    _copy_tree(templates / ".cursor" / "commands", target / ".cursor" / "commands")
    _copy_tree(templates / ".cursor" / "rules", target / ".cursor" / "rules")
    tasks = target / "tasks" / "open"
    tasks.mkdir(parents=True, exist_ok=True)
    _write_initial_state(target)
    _write_manifest(factory_root, target)


def init_project(factory_root: Path, target: Path) -> None:
    target = target.resolve()
    if not _is_empty_dir(target):
        raise SystemExit(f"Refusing init: target not empty: {target}")

    staging = target.parent / f".{target.name}.staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    templates = factory_root / "templates" / "project"
    _copy_tree(templates, staging)
    _copy_tree(factory_root / "vendor" / "gamestudio", staging / ".game-factory" / "vendor" / "gamestudio")
    _copy_tree(
        factory_root / "vendor" / "asset-catalog",
        staging / ".game-factory" / "vendor" / "asset-catalog",
    )
    _copy_tree(factory_root / "vendor" / "godogen" / "engines" / "godot.md", staging / "godot.md")
    _copy_tree(factory_root / "vendor" / "godot_cli_control" / "addon", staging / "addons" / "godot_cli_control")
    _publish_skills(factory_root, staging)
    _copy_tree(factory_root / "templates" / "project" / ".cursor" / "commands", staging / ".cursor" / "commands")
    _copy_tree(factory_root / "templates" / "project" / ".cursor" / "rules", staging / ".cursor" / "rules")
    _write_initial_state(staging)
    _write_manifest(factory_root, staging)

    target.mkdir(parents=True, exist_ok=True)
    for child in staging.iterdir():
        dest = target / child.name
        if dest.exists():
            if dest.is_dir():
                shutil.rmtree(dest)
            else:
                dest.unlink()
        shutil.move(str(child), str(dest))
    shutil.rmtree(staging)
    _emit(_result_payload(target, "fresh"), target)


def init_into_existing(factory_root: Path, target: Path) -> None:
    requested = target
    target = target.resolve()
    if not _is_godot_project(target):
        raise SystemExit(f"Refusing --into-existing: no project.godot in {target}")
    if _is_factory_project(target):
        raise SystemExit(f"Already a factory project; use --upgrade instead: {target}")
    _overlay_factory(factory_root, target, skip_existing_docs=True)
    _emit(_result_payload(requested, "into-existing"), target)


def upgrade_project(factory_root: Path, target: Path) -> None:
    requested = target
    target = target.resolve()
    if not _is_factory_project(target):
        raise SystemExit(f"Not a factory project (missing install-manifest): {target}")
    from game_factory.migrations.runner import run_migrations

    _publish_skills(factory_root, target)
    _copy_tree(
        factory_root / "vendor" / "asset-catalog",
        target / ".game-factory" / "vendor" / "asset-catalog",
    )
    _copy_tree(factory_root / "vendor" / "gamestudio", target / ".game-factory" / "vendor" / "gamestudio")
    mig = run_migrations(target, FACTORY_VERSION)
    manifest_path = target / ".game-factory" / "install-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["factory_version"] = FACTORY_VERSION
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    _copy_tree(
        factory_root / "templates" / "project" / "docs" / "ONBOARDING.md",
        target / "docs" / "ONBOARDING.md",
        skip_existing=True,
    )
    _copy_tree(
        factory_root / "templates" / "project" / ".cursor" / "commands" / "game-factory-onboard.md",
        target / ".cursor" / "commands" / "game-factory-onboard.md",
        skip_existing=True,
    )
    _emit(_result_payload(requested, "upgrade", migration=mig), target)


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize or upgrade game-factory project")
    parser.add_argument("--out", required=True, help="Target directory")
    parser.add_argument("--factory-root", default=None, help="Path to ai-game-factory repo")
    parser.add_argument("--upgrade", action="store_true", help="Upgrade existing factory project")
    parser.add_argument("--into-existing", action="store_true", help="Overlay onto existing Godot project")
    args = parser.parse_args()
    factory_root = Path(args.factory_root or Path(__file__).resolve().parents[1])
    target = Path(args.out)
    if args.upgrade and args.into_existing:
        raise SystemExit("Use only one of --upgrade or --into-existing")
    if args.upgrade:
        upgrade_project(factory_root, target)
    elif args.into_existing:
        init_into_existing(factory_root, target)
    else:
        init_project(factory_root, target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
