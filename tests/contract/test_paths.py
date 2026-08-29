from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from game_factory.gates.runner import _step_glb_import
from game_factory.paths import join_project, relpath, under_root

REPO = Path(__file__).resolve().parents[2]
SKIP_DIR_NAMES = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules", "egg-info"}
MACHINE_PATH_NEEDLES = (
    "D:\\GAMES Creator",
    "D:/GAMES Creator",
    r"D:\GAMES Creator",
)


def test_relpath_posix_under_root(tmp_path: Path):
    nested = tmp_path / "assets" / "models" / "hero.glb"
    nested.parent.mkdir(parents=True)
    nested.write_bytes(b"glb")
    assert relpath(tmp_path, nested) == "assets/models/hero.glb"


def test_under_root_rejects_absolute(tmp_path: Path):
    with pytest.raises(ValueError, match="project-relative"):
        under_root(tmp_path, tmp_path / "assets", name="assets.output_dir")


def test_join_project_keeps_relative(tmp_path: Path):
    assert join_project(tmp_path, ".game-factory/jobs/wo.json") == tmp_path / ".game-factory" / "jobs" / "wo.json"


def test_glb_evidence_is_relative(tmp_path: Path):
    (tmp_path / "game-factory.config.yaml").write_text(
        "schema_version: 2\nproject:\n  name: x\n  display_name: x\n  dimension: 3d\n"
        "  logical_resolution: [1280,720]\ntoolchain:\n  godot: '>=4.7'\n  dotnet: '>=9'\n"
        "  python: '>=3.11'\npipeline:\n  retry_budget: 3\n  on_optional_asset_failure: procedural\n"
        "gates:\n  fast: [config]\n  full: [fast]\n  visual: [full]\nproduction:\n"
        "  batch_weight_target: [15,20]\n  max_xl_per_batch: 1\n  max_l_per_batch: 2\n"
        "  max_measurement_tasks: 2\n  max_parallel_writers: 1\nassets:\n  provider: kie\n"
        "  env_key: KIE\n  output_dir: assets\n  fallback: procedural\n  approval:\n"
        "    mode: design_gate\n    max_credits: 0\n    max_jobs: 0\n  models:\n"
        "    text_to_image: a\n    image_to_image: b\n    reference: c\n    image_to_video: d\n"
        "  models_3d:\n    user_glb_dir: assets/models\n    allow_procedural: false\n"
        "orchestration:\n  adapter: cursor\n",
        encoding="utf-8",
    )
    glb = tmp_path / "assets" / "models" / "box.glb"
    glb.parent.mkdir(parents=True)
    glb.write_bytes(b"glb")
    result = _step_glb_import(tmp_path)
    assert result["ok"]
    assert result["evidence"] == ["assets/models/box.glb"]


def test_no_hardcoded_machine_roots():
    hits: list[str] = []
    for path in REPO.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES or part.endswith(".egg-info") for part in path.parts):
            continue
        if path.name == "test_paths.py":
            continue
        if path.suffix.lower() not in {".py", ".md", ".yaml", ".yml", ".json", ".toml", ".ps1", ".mdc", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for needle in MACHINE_PATH_NEEDLES:
            if needle in text:
                hits.append(f"{path.relative_to(REPO).as_posix()}: {needle}")
    assert hits == []


def test_sync_patch_strips_godogen_drive_path():
    spec = importlib.util.spec_from_file_location("sync_upstream", REPO / "scripts" / "vendor" / "sync-upstream.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    sample = (
        '`.env` (canonical: D:\\\\GAMES Creator\\\\godogen\\\\.env).\n'
        'GODOGEN_ROOT = Path(os.environ.get("GODOGEN_ROOT", r"D:\\GAMES Creator\\godogen"))\n'
        '        if parent.name.lower() in {"second games", "godogen"}:\n'
        "            break\n"
        '"KIE_API_KEY is not set. Put it in D:\\\\GAMES Creator\\\\godogen\\\\.env "\n'
    )
    patched = mod._patch_kie_video_env_paths(sample)
    assert "D:\\GAMES Creator" not in patched
    assert "D:\\\\GAMES Creator" not in patched
