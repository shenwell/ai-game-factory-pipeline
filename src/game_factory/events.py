from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def events_path(project_root: Path) -> Path:
    return project_root / ".game-factory" / "events.jsonl"


def append_event(project_root: Path, event_type: str, payload: dict[str, Any]) -> None:
    path = events_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "type": event_type,
        "payload": payload,
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
