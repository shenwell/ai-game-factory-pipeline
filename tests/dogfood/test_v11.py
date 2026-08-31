from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from game_factory.migrations.runner import migrate_config_v1_to_v2, run_migrations


def _init_v1_project(tmp_path: Path, factory_root: Path):
    import importlib.util

    spec = importlib.util.spec_from_file_location("gf_init", factory_root / "install" / "init.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    target = tmp_path / "game"
    mod.init_project(factory_root, target)
    manifest = json.loads((target / ".game-factory" / "install-manifest.json").read_text(encoding="utf-8"))
    manifest["factory_version"] = "1.0.0"
    (target / ".game-factory" / "install-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    cfg = yaml.safe_load((target / "game-factory.config.yaml").read_text(encoding="utf-8"))
    cfg["schema_version"] = 1
    (target / "game-factory.config.yaml").write_text(yaml.safe_dump(cfg), encoding="utf-8")
    return target


def test_upgrade_migrates_config(tmp_path: Path):
    factory_root = Path(__file__).resolve().parents[2]
    project = _init_v1_project(tmp_path, factory_root)
    result = run_migrations(project, "1.1.0")
    assert "1.0.0->1.1.0" in result["steps"]
    cfg = yaml.safe_load((project / "game-factory.config.yaml").read_text(encoding="utf-8"))
    assert cfg["schema_version"] == 2
    assert "opensource" in cfg["assets"]
    assert (project / "docs" / "ASSETS-3D.md").exists()


def test_migrate_1_1_3_adds_ui_contract(tmp_path: Path):
    factory_root = Path(__file__).resolve().parents[2]
    project = _init_v1_project(tmp_path, factory_root)
    manifest_path = project / ".game-factory" / "install-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["factory_version"] = "1.1.2"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (project / "docs" / "design" / "UI.md").unlink(missing_ok=True)

    result = run_migrations(project, "1.1.3")
    assert "1.1.2->1.1.3" in result["steps"]
    assert (project / "docs" / "design" / "UI.md").is_file()
    cfg = yaml.safe_load((project / "game-factory.config.yaml").read_text(encoding="utf-8"))
    assert cfg.get("ui", {}).get("shell") == "deferred_mvp"
    assert "ui_contract" in cfg["gates"]["full"]


def test_into_existing_godot(tmp_path: Path):
    import importlib.util

    factory_root = Path(__file__).resolve().parents[2]
    godot = tmp_path / "existing"
    godot.mkdir()
    (godot / "project.godot").write_text("[application]\nconfig/name=\"Test\"\n", encoding="utf-8")
    (godot / "Main.cs").write_text("// game", encoding="utf-8")

    spec = importlib.util.spec_from_file_location("gf_init", factory_root / "install" / "init.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    mod.init_into_existing(factory_root, godot)

    assert (godot / "game-factory.config.yaml").exists()
    assert (godot / "Main.cs").exists()
    assert (godot / ".game-factory" / "state.json").exists()
