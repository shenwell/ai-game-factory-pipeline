#!/usr/bin/env python3
"""Sync upstream vendor trees into vendor/ and refresh VENDOR.lock."""

from __future__ import annotations

import json
import os
import re
import shutil
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VENDOR = ROOT / "vendor"


def _rmtree_force(path: Path) -> None:
    if not path.exists():
        return

    def _onexc(func, p, _exc_info):
        os.chmod(p, stat.S_IWRITE)
        func(p)

    shutil.rmtree(path, onexc=_onexc)


def _local_source(env_key: str, *relative_to_parent: str) -> Path:
    """Sibling of this repo, or an env override. Never a hardcoded drive path."""
    override = os.environ.get(env_key)
    if override:
        return Path(override)
    return ROOT.parent.joinpath(*relative_to_parent)


SOURCES = {
    "godogen": {
        "type": "local",
        "path": _local_source("GODOGEN_ROOT", "godogen"),
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
    "gamedev-ui": {
        "type": "git_sparse_multi",
        "url": "https://github.com/gamedev-skills/awesome-gamedev-agent-skills.git",
        "mappings": [
            ("skills/disciplines/game-ui-ux", "game-ui-ux"),
            ("skills/godot/godot-ui-control", "godot-ui-control"),
            ("skills/disciplines/input-systems", "input-systems"),
        ],
    },
    "godot_cli_control": {
        "type": "local",
        "path": _local_source("GODOT_CLI_CONTROL_ROOT", "godot-cli-control"),
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
        _rmtree_force(tmp)
    _run_git(["clone", "--depth", "1", url, str(tmp)], VENDOR)
    commit = _run_git(["rev-parse", "HEAD"], tmp)
    if target.exists():
        _rmtree_force(target)
    shutil.move(str(tmp / ".git"), str(VENDOR / f".git-{dest}-discard"))
    shutil.rmtree(VENDOR / f".git-{dest}-discard", ignore_errors=True)
    shutil.move(str(tmp), str(target))
    return commit


def sync_git_sparse(name: str, url: str, sparse: str, dest: str) -> str:
    tmp = VENDOR / f".sync-{dest}"
    if tmp.exists():
        _rmtree_force(tmp)
    _run_git(["clone", "--depth", "1", "--filter=blob:none", "--sparse", url, str(tmp)], VENDOR)
    _run_git(["sparse-checkout", "set", sparse], tmp)
    commit = _run_git(["rev-parse", "HEAD"], tmp)
    src = tmp / sparse
    target = VENDOR / dest
    if target.exists():
        _rmtree_force(target)
    shutil.copytree(src, target)
    _rmtree_force(tmp)
    return commit


def sync_git_sparse_multi(name: str, url: str, mappings: list[tuple[str, str]]) -> str:
    tmp = VENDOR / f".sync-{name}"
    if tmp.exists():
        _rmtree_force(tmp)
    _run_git(["clone", "--depth", "1", "--filter=blob:none", "--sparse", url, str(tmp)], VENDOR)
    sparse_paths = [m[0] for m in mappings]
    _run_git(["sparse-checkout", "set", *sparse_paths], tmp)
    commit = _run_git(["rev-parse", "HEAD"], tmp)
    for sparse, dest in mappings:
        src = tmp / sparse
        target = VENDOR / dest
        if not src.exists():
            raise FileNotFoundError(f"Sparse path missing in {name}: {sparse}")
        if target.exists():
            _rmtree_force(target)
        shutil.copytree(src, target)
    _rmtree_force(tmp)
    return commit


def sync_local(name: str, base: Path, copies: list[tuple[str, str]]) -> str:
    if not base.exists():
        env_hint = "GODOGEN_ROOT" if name == "godogen" else "GODOT_CLI_CONTROL_ROOT"
        raise FileNotFoundError(
            f"Local vendor source {name!r} not found at {base}. "
            f"Place it next to this repo or set {env_hint}."
        )
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


def _patch_kie_video_env_paths(text: str) -> str:
    text = re.sub(
        r"`\.env` \(canonical: [^)]+\)\.",
        "`.env` (project root, `GODOGEN_ROOT`, or the current working directory).",
        text,
        count=1,
    )
    text = re.sub(
        r'GODOGEN_ROOT = Path\(os\.environ\.get\("GODOGEN_ROOT", r?"[^"]+"\)\)',
        'GODOGEN_ROOT = Path(os.environ["GODOGEN_ROOT"]) if os.environ.get("GODOGEN_ROOT") else Path.cwd()',
        text,
        count=1,
    )
    text = re.sub(
        r"KIE_API_KEY is not set\. Put it in [^\n]+",
        "KIE_API_KEY is not set. Put it in the project `.env` (gitignored) or export KIE_API_KEY. Create the key at https://kie.ai/api-key",
        text,
        count=1,
    )
    text = re.sub(
        r"\n        if parent\.name\.lower\(\) in \{[^}]+\}:\n            break\n",
        "\n",
        text,
        count=1,
    )
    return text


def _patch_godot_cli_plugin(text: str) -> str:
    return text.replace(
        "Second Games: default OFF — only --cli-control",
        "Default OFF — use --cli-control",
    )


def apply_patches() -> None:
    patches = VENDOR / "patches"
    kie_skill = patches / "asset-gen-SKILL-kie-only.md"
    if kie_skill.exists():
        dst = VENDOR / "godogen" / "asset-gen" / "SKILL.md"
        if (VENDOR / "godogen" / "asset-gen").exists():
            shutil.copy2(kie_skill, dst)
    kie_video = VENDOR / "godogen" / "asset-gen" / "tools" / "kie_video.py"
    if kie_video.exists():
        original = kie_video.read_text(encoding="utf-8")
        patched = _patch_kie_video_env_paths(original)
        if patched != original:
            kie_video.write_text(patched, encoding="utf-8")
    plugin = VENDOR / "godot_cli_control" / "addon" / "plugin.gd"
    if plugin.exists():
        original = plugin.read_text(encoding="utf-8")
        patched = _patch_godot_cli_plugin(original)
        if patched != original:
            plugin.write_text(patched, encoding="utf-8")


def main() -> int:
    lock: dict = {"synced_at": datetime.now(timezone.utc).isoformat(), "sources": {}}
    for name, spec in SOURCES.items():
        if spec["type"] == "git":
            lock["sources"][name] = {"commit": sync_git(name, spec["url"], spec["dest"])}
        elif spec["type"] == "git_sparse":
            lock["sources"][name] = {
                "commit": sync_git_sparse(name, spec["url"], spec["sparse"], spec["dest"])
            }
        elif spec["type"] == "git_sparse_multi":
            lock["sources"][name] = {
                "commit": sync_git_sparse_multi(name, spec["url"], spec["mappings"])
            }
        elif spec["type"] == "local":
            lock["sources"][name] = {"commit": sync_local(name, spec["path"], spec["copy"])}
    apply_patches()
    (VENDOR / "VENDOR.lock").write_text(json.dumps(lock, indent=2), encoding="utf-8")
    print(json.dumps(lock, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
