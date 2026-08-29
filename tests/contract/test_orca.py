from __future__ import annotations

import json
from pathlib import Path

from game_factory.adapters.orca.client import cancel, collect, dispatch, status


def test_orca_local_dispatch_cycle(tmp_path: Path):
    wo = tmp_path / "wo.json"
    wo.write_text(
        json.dumps(
            {
                "id": "wo-test",
                "zone": "ui",
                "task_ids": ["t1"],
                "allowed_globs": ["ui/**"],
                "forbidden_globs": [],
                "acceptance_criteria": ["ok"],
                "risk_class": "layout",
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / ".game-factory" / "jobs").mkdir(parents=True)
    out = dispatch(tmp_path, wo)
    assert out["job_id"]
    st = status(tmp_path, out["job_id"])
    assert st["status"] in ("queued_local", "dispatched", "queued")
    col = collect(tmp_path, out["job_id"])
    assert col["status"] == "complete"
    can = cancel(tmp_path, out["job_id"])
    assert can["status"] == "cancelled"
