from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from game_factory.config import load_config
from game_factory.events import append_event
from game_factory.gates.runner import verify
from game_factory.production.batching import (
    build_work_order,
    list_open_tasks,
    open_bug_tasks,
    save_work_order,
    tasks_open_dir,
)

WEIGHT_RE = re.compile(r"weight:\s*(\d+)", re.I)
ZONE_RE = re.compile(r"zone:\s*(\S+)", re.I)


def _task_weight(path: Path) -> int:
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = WEIGHT_RE.search(text)
    return int(m.group(1)) if m else 2


def _task_zone(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = ZONE_RE.search(text)
    return m.group(1) if m else "src"


def plan_batch(project_root: Path) -> dict[str, Any] | None:
    cfg = load_config(project_root)
    target = cfg["production"]["batch_weight_target"]
    lo, hi = int(target[0]), int(target[1])
    by_zone: dict[str, list[Path]] = {}
    for task in list_open_tasks(project_root):
        if task.name.startswith(("later-", "idea-", "debt-")):
            continue
        zone = _task_zone(task)
        by_zone.setdefault(zone, []).append(task)

    for zone, tasks in sorted(by_zone.items()):
        batch: list[Path] = []
        weight = 0
        for task in tasks:
            w = _task_weight(task)
            if batch and weight + w > hi:
                break
            batch.append(task)
            weight += w
            if weight >= lo:
                break
        if batch and weight >= lo:
            wo = build_work_order(project_root, zone, batch)
            save_work_order(project_root, wo)
            append_event(project_root, "batch_planned", {"work_order_id": wo["id"], "zone": zone})
            return wo
    return None


def close_batch(project_root: Path, work_order_id: str) -> dict[str, Any]:
    wo_path = project_root / ".game-factory" / "jobs" / f"{work_order_id}.json"
    if not wo_path.exists():
        raise FileNotFoundError(f"Work order not found: {work_order_id}")
    import json

    wo = json.loads(wo_path.read_text(encoding="utf-8"))
    gate = verify(project_root, "fast")
    result = {"work_order_id": work_order_id, "gate": gate, "closed_tasks": []}
    if gate["ok"]:
        for task_id in wo["task_ids"]:
            src = tasks_open_dir(project_root) / f"{task_id}.md"
            if src.exists():
                src.unlink()
                result["closed_tasks"].append(task_id)
        append_event(project_root, "batch_closed", result)
    return result


def production_status(project_root: Path) -> dict[str, Any]:
    open_tasks = list_open_tasks(project_root)
    bugs = open_bug_tasks(project_root)
    return {
        "open_tasks": [p.name for p in open_tasks],
        "bug_tasks": [p.name for p in bugs],
        "can_release": len(bugs) == 0 and not any(p.name.startswith("NN-") for p in open_tasks),
    }
