from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from game_factory.config import load_config


def leases_path(project_root: Path) -> Path:
    return project_root / ".game-factory" / "jobs" / "zone-leases.json"


def load_leases(project_root: Path) -> dict[str, Any]:
    path = leases_path(project_root)
    if not path.exists():
        return {"leases": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def save_leases(project_root: Path, data: dict[str, Any]) -> None:
    path = leases_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def worktree_root(project_root: Path) -> Path:
    cfg = load_config(project_root)
    rel = cfg.get("production", {}).get("worktree_dir", ".worktrees")
    return project_root / rel


def acquire_zone_lease(project_root: Path, zone: str, writer_id: str) -> dict[str, Any]:
    cfg = load_config(project_root)
    max_writers = int(cfg["production"].get("max_parallel_writers", 1))
    data = load_leases(project_root)
    active = {k: v for k, v in data["leases"].items() if v.get("status") == "active"}
    if len(active) >= max_writers:
        raise RuntimeError(f"max_parallel_writers={max_writers} reached")
    if zone in active:
        raise RuntimeError(f"zone {zone} already leased by {active[zone]['writer_id']}")
    data["leases"][zone] = {
        "writer_id": writer_id,
        "status": "active",
        "since": datetime.now(timezone.utc).isoformat(),
    }
    save_leases(project_root, data)
    return data["leases"][zone]


def release_zone_lease(project_root: Path, zone: str) -> None:
    data = load_leases(project_root)
    if zone in data["leases"]:
        data["leases"][zone]["status"] = "released"
        data["leases"][zone]["released_at"] = datetime.now(timezone.utc).isoformat()
    save_leases(project_root, data)


def create_writer_worktree(project_root: Path, zone: str, writer_id: str) -> Path:
    acquire_zone_lease(project_root, zone, writer_id)
    root = worktree_root(project_root)
    root.mkdir(parents=True, exist_ok=True)
    branch = f"factory/{zone}/{writer_id}"
    wt_path = root / f"{zone}-{writer_id}"
    if wt_path.exists():
        return wt_path
    subprocess.run(
        ["git", "worktree", "add", "-B", branch, str(wt_path), "HEAD"],
        cwd=project_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return wt_path


def remove_writer_worktree(project_root: Path, zone: str, writer_id: str) -> None:
    wt_path = worktree_root(project_root) / f"{zone}-{writer_id}"
    if wt_path.exists():
        subprocess.run(["git", "worktree", "remove", "--force", str(wt_path)], cwd=project_root, check=False)
    release_zone_lease(project_root, zone)
