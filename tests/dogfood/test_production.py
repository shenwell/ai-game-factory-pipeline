from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
import yaml

from game_factory.gates.runner import verify
from game_factory.production.producer import close_batch, plan_batch, production_status

REPO = Path(__file__).resolve().parents[2]


def _init_minimal_project(tmp_path: Path) -> Path:
    import importlib.util

    spec = importlib.util.spec_from_file_location("gf_init", REPO / "install" / "init.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    target = tmp_path / "game"
    mod.init_project(REPO, target)
    return target


def test_plan_and_close_batch(tmp_path: Path):
    project = _init_minimal_project(tmp_path)
    tasks = project / "tasks" / "open"
    tasks.mkdir(parents=True, exist_ok=True)
    (tasks / "NN-001-hud.md").write_text("zone: ui\nweight: 8\n", encoding="utf-8")
    (tasks / "NN-002-score.md").write_text("zone: ui\nweight: 10\n", encoding="utf-8")

    wo = plan_batch(project)
    assert wo is not None
    assert wo["zone"] == "ui"
    assert len(wo["task_ids"]) == 2

    result = close_batch(project, wo["id"])
    assert result["gate"]["ok"] is True
    assert len(result["closed_tasks"]) == 2
    assert production_status(project)["open_tasks"] == []


def test_fast_gates_on_init_project(tmp_path: Path):
    project = _init_minimal_project(tmp_path)
    manifest = project / ".game-factory" / "install-manifest.json"
    assert manifest.exists()
    result = verify(project, "fast")
    assert result["ok"] is True
