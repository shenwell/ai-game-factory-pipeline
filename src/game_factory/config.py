from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
import yaml

SCHEMAS_DIR = Path(__file__).resolve().parents[2] / "schemas"


def load_schema(name: str) -> dict[str, Any]:
    path = SCHEMAS_DIR / name
    return json.loads(path.read_text(encoding="utf-8"))


def load_config(project_root: Path) -> dict[str, Any]:
    path = project_root / "game-factory.config.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Missing config: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    jsonschema.validate(data, load_schema("game-factory.config.schema.json"))
    return data


def save_config(project_root: Path, data: dict[str, Any]) -> None:
    jsonschema.validate(data, load_schema("game-factory.config.schema.json"))
    path = project_root / "game-factory.config.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
