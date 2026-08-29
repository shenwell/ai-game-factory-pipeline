#!/usr/bin/env python3
"""Sync upstream vendor trees into vendor/ and refresh VENDOR.lock."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VENDOR = ROOT / "vendor"

SOURCES = {
    "godogen": {
        "type": "local",
        "path": Path(r"D:\GAMES Creator\godogen"),
        "copy": [
            ("engines/godot.md", "godogen/engines/godot.md"),
            ("prompts/runtime.md", "godogen/prompts/runtime.md"),
            ("asset-gen", "godogen/asset-gen"),
        ],
    },
    "gamestudio": {
        "type": "git",
        "url": "https://github.com/studioigor/gamestudio.git",
        "dest": "gamestudio",
    },
    "game-design": {
        "type": "git_sparse",
        "url": "https://github.com/saschb2b/skills.git",
        "sparse": "skills/productivity/game-design",
        "dest": "game-design",
    },
    "godot_cli_control": {
        "type": "local",
        "path": Path(r"D:\GAMES Creator\Second Games"),
        "copy": [
            ("addons/godot_cli_control", "godot_cli_control/addon"),
            (".cursor/skills/godot-cli-control", "godot_cli_control/skill"),
        ],
    },
}


def _run_git(args: list[str], cwd: Path) -> str:
    out = subprocess.check_output(["git"] + args, cwd=cwd, text=True, stderr=subprocess.STDOUT)
    return out.strip()


def sync_git(name: str, url: str, dest: str) -> str:
    target = VENDOR / dest
    tmp = VENDOR / f".sync-{dest}"
    if tmp.exists():
        shutil.rmtree(tmp)
    _run_git(["clone", "--depth", "1", url, str(tmp)], VENDOR)
    commit = _run_git(["rev-parse", "HEAD"], tmp)
    if target.exists():
        shutil.rmtree(target)
    shutil.move(str(tmp / ".git"), str(VENDOR / f".git-{dest}-discard"))
    shutil.rmtree(VENDOR / f".git-{dest}-discard", ignore_errors=True)
    shutil.move(str(tmp), str(target))
    return commit


def sync_git_sparse(name: str, url: str, sparse: str, dest: str) -> str:
    tmp = VENDOR / f".sync-{dest}"
    if tmp.exists():
        shutil.rmtree(tmp)
    _run_git(["clone", "--depth", "1", "--filter=blob:none", "--sparse", url, str(tmp)], VENDOR)
    _run_git(["sparse-checkout", "set", sparse], tmp)
    commit = _run_git(["rev-parse", "HEAD"], tmp)
    src = tmp / sparse
    target = VENDOR / dest
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(src, target)
    shutil.rmtree(tmp)
    return commit


def sync_local(name: str, base: Path, copies: list[tuple[str, str]]) -> str:
    stamp = "local"
    if (base / ".git").exists():
        try:
            stamp = _run_git(["rev-parse", "HEAD"], base)
        except Exception:
            pass
    for rel_src, rel_dst in copies:
        src = base / rel_src
        dst = VENDOR / rel_dst
        if dst.exists():
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    return stamp


def apply_patches() -> None:
    patches = VENDOR / "patches"
    kie_skill = patches / "asset-gen-SKILL-kie-only.md"
    if kie_skill.exists():
        dst = VENDOR / "godogen" / "asset-gen" / "SKILL.md"
        if (VENDOR / "godogen" / "asset-gen").exists():
            shutil.copy2(kie_skill, dst)


def main() -> int:
    lock: dict = {"synced_at": datetime.now(timezone.utc).isoformat(), "sources": {}}
    for name, spec in SOURCES.items():
        if spec["type"] == "git":
            lock["sources"][name] = {"commit": sync_git(name, spec["url"], spec["dest"])}
        elif spec["type"] == "git_sparse":
            lock["sources"][name] = {
                "commit": sync_git_sparse(name, spec["url"], spec["sparse"], spec["dest"])
            }
        elif spec["type"] == "local":
            lock["sources"][name] = {"commit": sync_local(name, spec["path"], spec["copy"])}
    apply_patches()
    (VENDOR / "VENDOR.lock").write_text(json.dumps(lock, indent=2), encoding="utf-8")
    print(json.dumps(lock, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
