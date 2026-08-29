from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import jsonschema

from game_factory.config import load_schema

TASK_PREFIX = re.compile(r"^(NN|bug|debt|idea|later)-")


def tasks_open_dir(project_root: Path) -> Path:
    return project_root / "tasks" / "open"


def list_open_tasks(project_root: Path) -> list[Path]:
    d = tasks_open_dir(project_root)
    if not d.exists():
        return []
    return sorted(d.glob("*.md"))


def open_bug_tasks(project_root: Path) -> list[Path]:
    return [p for p in list_open_tasks(project_root) if p.name.startswith("bug-")]


def build_work_order(project_root: Path, zone: str, task_paths: list[Path]) -> dict[str, Any]:
    wo = {
        "id": f"wo-{zone}-{len(task_paths)}",
        "zone": zone,
        "task_ids": [p.stem for p in task_paths],
        "allowed_globs": [f"{zone}/**"],
        "forbidden_globs": ["docs/design/**"],
        "acceptance_criteria": ["factory verify fast exits 0"],
        "evidence_commands": ["factory verify fast"],
        "risk_class": "layout",
        "weight_total": len(task_paths) * 2,
    }
    jsonschema.validate(wo, load_schema("work-order.schema.json"))
    return wo


def save_work_order(project_root: Path, wo: dict[str, Any]) -> Path:
    path = project_root / ".game-factory" / "jobs" / f"{wo['id']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(wo, indent=2), encoding="utf-8")
    return path
