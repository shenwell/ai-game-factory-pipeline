from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import jsonschema
import yaml

from game_factory.config import load_schema

MigrationFn = Callable[[Path, dict[str, Any]], dict[str, Any]]

MIGRATIONS: list[tuple[str, str, MigrationFn]] = []


def _register(from_ver: str, to_ver: str, fn: MigrationFn) -> None:
    MIGRATIONS.append((from_ver, to_ver, fn))


def _parse_version(ver: str) -> tuple[int, int, int]:
    parts = ver.strip().lstrip("v").split(".")
    nums = [int(p) for p in parts[:3]] + [0] * (3 - len(parts[:3]))
    return nums[0], nums[1], nums[2]


def _version_lt(a: str, b: str) -> bool:
    return _parse_version(a) < _parse_version(b)


def load_manifest(project_root: Path) -> dict[str, Any]:
    path = project_root / ".game-factory" / "install-manifest.json"
    if not path.exists():
        raise FileNotFoundError(f"Not a factory project: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_manifest(project_root: Path, manifest: dict[str, Any]) -> None:
    path = project_root / ".game-factory" / "install-manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def migrate_config_v1_to_v2(project_root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    cfg_path = project_root / "game-factory.config.yaml"
    if not cfg_path.exists():
        return manifest
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    if int(data.get("schema_version", 1)) >= 2:
        return manifest
    data["schema_version"] = 2
    data.setdefault("assets", {})
    data["assets"].setdefault(
        "opensource",
        {
            "enabled": False,
            "allow_licenses": ["CC0", "CC-BY-4.0", "MIT"],
            "catalog": ".game-factory/vendor/asset-catalog/kenney-index.json",
            "require_checksum": True,
        },
    )
    data["assets"].setdefault(
        "models_3d",
        {"user_glb_dir": "assets/models", "allow_procedural": True},
    )
    data.setdefault("production", {})
    data["production"].setdefault("worktree_dir", ".worktrees")
    data.setdefault("hosts", {"engines": ["godot"]})
    jsonschema.validate(data, load_schema("game-factory.config.schema.json"))
    cfg_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return manifest


def migrate_1_0_to_1_1(project_root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    manifest = migrate_config_v1_to_v2(project_root, manifest)
    catalog_dst = project_root / ".game-factory" / "vendor" / "asset-catalog"
    catalog_dst.mkdir(parents=True, exist_ok=True)
    assets_3d = project_root / "docs" / "ASSETS-3D.md"
    if not assets_3d.exists():
        assets_3d.parent.mkdir(parents=True, exist_ok=True)
        assets_3d.write_text(
            "# 3D assets\n\n"
            "Place user GLB files under `assets/models/`. Use procedural meshes in code for blockouts. "
            "Kie generates 2D references only; 3D rigging is out of pipeline scope.\n",
            encoding="utf-8",
        )
    manifest["factory_version"] = "1.1.0"
    manifest["upgraded_at"] = datetime.now(timezone.utc).isoformat()
    return manifest


_register("1.0.0", "1.1.0", migrate_1_0_to_1_1)


def _templates_root() -> Path:
    return Path(__file__).resolve().parents[3] / "templates" / "project"


def _copy_template_file(project_root: Path, rel: str, *, skip_existing: bool = True) -> None:
    src = _templates_root() / rel
    dst = project_root / rel
    if skip_existing and dst.exists():
        return
    if not src.is_file():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def migrate_1_1_3_ui(project_root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    for rel in (
        "docs/design/UI.md",
        "docs/MVP_DONE.md",
        "docs/DONE.md",
        "docs/PLAYTEST.md",
        "docs/ONBOARDING.md",
        ".cursor/commands/game-factory-ui.md",
    ):
        _copy_template_file(project_root, rel, skip_existing=True)

    cfg_path = project_root / "game-factory.config.yaml"
    if cfg_path.exists():
        data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
        data.setdefault("ui", {"shell": "deferred_mvp"})
        gates = data.setdefault("gates", {})
        full = list(gates.get("full") or [])
        if "ui_contract" not in full:
            full.append("ui_contract")
            gates["full"] = full
        jsonschema.validate(data, load_schema("game-factory.config.schema.json"))
        cfg_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")

    manifest["factory_version"] = "1.1.3"
    manifest["upgraded_at"] = datetime.now(timezone.utc).isoformat()
    return manifest


for _from in ("1.1.0", "1.1.1", "1.1.2"):
    _register(_from, "1.1.3", migrate_1_1_3_ui)


def run_migrations(project_root: Path, target_version: str) -> dict[str, Any]:
    manifest = load_manifest(project_root)
    current = manifest.get("factory_version", "1.0.0")
    if not _version_lt(current, target_version):
        return {"ok": True, "from": current, "to": current, "steps": []}
    steps: list[str] = []
    ver = current
    while _version_lt(ver, target_version):
        applied = False
        for from_ver, to_ver, fn in MIGRATIONS:
            if ver == from_ver:
                manifest = fn(project_root, manifest)
                ver = to_ver
                steps.append(f"{from_ver}->{to_ver}")
                applied = True
                break
        if not applied:
            break
    save_manifest(project_root, manifest)
    return {"ok": True, "from": current, "to": ver, "steps": steps}
