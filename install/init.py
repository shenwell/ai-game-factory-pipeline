#!/usr/bin/env python3
"""Atomic fresh-only init: copy templates + vendor publish into empty target directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

FACTORY_VERSION = "1.0.0"
FORBIDDEN_IN_TARGET = {".git"}


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_empty_dir(path: Path) -> bool:
    if not path.exists():
        return True
    entries = [p for p in path.iterdir() if p.name not in FORBIDDEN_IN_TARGET]
    return len(entries) == 0


def _copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return
    shutil.copytree(src, dst, dirs_exist_ok=True)


def _publish_skills(factory_root: Path, target: Path) -> None:
    vendor = factory_root / "vendor"
    agents = target / ".agents" / "skills"
    cursor = target / ".cursor" / "skills"
    agents.mkdir(parents=True, exist_ok=True)
    cursor.mkdir(parents=True, exist_ok=True)

    # game-design
    _copy_tree(vendor / "game-design", agents / "game-design")
    _copy_tree(vendor / "game-design", cursor / "game-design")

    # asset-gen from godogen vendor (Kie-only SKILL if patched)
    skill_src = vendor / "godogen" / "asset-gen"
    kie_patch = factory_root / "vendor" / "patches" / "asset-gen-SKILL-kie-only.md"
    _copy_tree(skill_src, agents / "asset-gen")
    _copy_tree(skill_src, cursor / "asset-gen")
    if kie_patch.exists():
        shutil.copy2(kie_patch, agents / "asset-gen" / "SKILL.md")
        shutil.copy2(kie_patch, cursor / "asset-gen" / "SKILL.md")

    # godot-cli-control
    _copy_tree(vendor / "godot_cli_control" / "skill", agents / "godot-cli-control")
    _copy_tree(vendor / "godot_cli_control" / "skill", cursor / "godot-cli-control")

    # game-factory orchestration skills
    for name in ("game-factory-mvp", "game-factory-produce", "game-factory-playtest", "game-factory-status", "game-factory-config"):
        src = factory_root / "templates" / "skills" / name
        if src.exists():
            _copy_tree(src, agents / name)
            _copy_tree(src, cursor / name)


def _write_initial_state(target: Path) -> None:
    gf = target / ".game-factory"
    gf.mkdir(parents=True, exist_ok=True)
    state = {
        "schema_version": 1,
        "phase": "bootstrap",
        "iteration": 0,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "blockers": [],
        "approval_hashes": {},
        "retry_counts": {},
    }
    (gf / "state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    (gf / "events.jsonl").write_text("", encoding="utf-8")
    (gf / "jobs").mkdir(exist_ok=True)
    (gf / "runtime").mkdir(exist_ok=True)


def _write_manifest(factory_root: Path, target: Path) -> None:
    vendor_lock = factory_root / "vendor" / "VENDOR.lock"
    manifest = {
        "factory_version": FACTORY_VERSION,
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "vendor_lock": json.loads(vendor_lock.read_text(encoding="utf-8")) if vendor_lock.exists() else {},
        "paths": {
            "studio": ".game-factory/vendor/gamestudio",
            "godot_guide": "godot.md",
        },
    }
    (target / ".game-factory" / "install-manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )


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

    # vendor snapshot into project
    _copy_tree(factory_root / "vendor" / "gamestudio", staging / ".game-factory" / "vendor" / "gamestudio")
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
    print(json.dumps({"ok": True, "path": str(target), "factory_version": FACTORY_VERSION}))


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize empty game project from ai-game-factory")
    parser.add_argument("--out", required=True, help="Empty target directory")
    parser.add_argument("--factory-root", default=None, help="Path to ai-game-factory repo")
    args = parser.parse_args()
    factory_root = Path(args.factory_root or Path(__file__).resolve().parents[1])
    target = Path(args.out)
    init_project(factory_root, target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
