from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonschema

from game_factory.config import load_schema

STATE_FILE = "state.json"
FACTORY_DIR = ".game-factory"


def factory_dir(project_root: Path) -> Path:
    return project_root / FACTORY_DIR


def state_path(project_root: Path) -> Path:
    return factory_dir(project_root) / STATE_FILE


def default_state() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "phase": "bootstrap",
        "iteration": 0,
        "updated_at": _now(),
        "blockers": [],
        "approval_hashes": {},
        "retry_counts": {},
    }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_state(project_root: Path) -> dict[str, Any]:
    path = state_path(project_root)
    if not path.exists():
        return default_state()
    data = json.loads(path.read_text(encoding="utf-8"))
    jsonschema.validate(data, load_schema("state.schema.json"))
    return data


def save_state(project_root: Path, data: dict[str, Any]) -> None:
    jsonschema.validate(data, load_schema("state.schema.json"))
    path = state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = _now()
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
