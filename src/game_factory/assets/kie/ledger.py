from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def ledger_path(project_root: Path) -> Path:
    return project_root / ".game-factory" / "jobs" / "kie-ledger.json"


def load_ledger(project_root: Path) -> dict[str, Any]:
    path = ledger_path(project_root)
    if not path.exists():
        return {"jobs": [], "credits_estimated": 0}
    return json.loads(path.read_text(encoding="utf-8"))


def record_job(project_root: Path, entry: dict[str, Any]) -> None:
    ledger = load_ledger(project_root)
    ledger["jobs"].append(entry)
    ledger["credits_estimated"] = int(ledger.get("credits_estimated", 0)) + int(entry.get("credits", 0))
    path = ledger_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
