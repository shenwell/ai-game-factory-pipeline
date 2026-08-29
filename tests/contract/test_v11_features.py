from __future__ import annotations

from pathlib import Path

import pytest

from game_factory.assets.providers.opensource import search_catalog
from game_factory.production.worktrees import acquire_zone_lease, load_leases, release_zone_lease


def test_catalog_search(tmp_path: Path):
    catalog = Path(__file__).resolve().parents[2] / "vendor" / "asset-catalog" / "kenney-index.json"
    dest = tmp_path / ".game-factory" / "vendor" / "asset-catalog"
    dest.mkdir(parents=True, exist_ok=True)
    import shutil

    shutil.copy(catalog, dest / "kenney-index.json")
    hits = search_catalog(tmp_path, "platformer", "CC0")
    assert any(h["license"] == "CC0" for h in hits)


def test_zone_lease(tmp_path: Path):
    (tmp_path / "game-factory.config.yaml").write_text(
        "schema_version: 2\nproject:\n  name: x\n  display_name: x\n  dimension: 2d\n"
        "  logical_resolution: [1280,720]\ntoolchain:\n  godot: '>=4.7'\n  dotnet: '>=9'\n"
        "  python: '>=3.11'\npipeline:\n  retry_budget: 3\n  on_optional_asset_failure: procedural\n"
        "gates:\n  fast: [config]\n  full: [fast]\n  visual: [full]\nproduction:\n"
        "  batch_weight_target: [15,20]\n  max_xl_per_batch: 1\n  max_l_per_batch: 2\n"
        "  max_measurement_tasks: 2\n  max_parallel_writers: 2\nassets:\n  provider: kie\n"
        "  env_key: KIE\n  output_dir: assets\n  fallback: procedural\n  approval:\n"
        "    mode: design_gate\n    max_credits: 0\n    max_jobs: 0\n  models:\n"
        "    text_to_image: a\n    image_to_image: b\n    reference: c\n    image_to_video: d\n"
        "orchestration:\n  adapter: cursor\n",
        encoding="utf-8",
    )
    acquire_zone_lease(tmp_path, "ui", "w1")
    with pytest.raises(RuntimeError):
        acquire_zone_lease(tmp_path, "ui", "w2")
    release_zone_lease(tmp_path, "ui")
    assert load_leases(tmp_path)["leases"]["ui"]["status"] == "released"
