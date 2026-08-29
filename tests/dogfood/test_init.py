from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def factory_root():
    return REPO


def _load_init_module():
    import importlib.util

    spec = importlib.util.spec_from_file_location("gf_init", REPO / "install" / "init.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_init_refuses_nonempty(tmp_path: Path, factory_root: Path):
    (tmp_path / "existing.txt").write_text("x", encoding="utf-8")
    init_mod = _load_init_module()

    with pytest.raises(SystemExit):
        init_mod.init_project(factory_root, tmp_path)


def test_init_empty_dir(tmp_path: Path, factory_root: Path):
    target = tmp_path / "game"
    init_mod = _load_init_module()

    init_mod.init_project(factory_root, target)
    assert (target / "game-factory.config.yaml").exists()
    assert (target / ".game-factory" / "state.json").exists()
    assert (target / "AGENTS.md").exists()
    state = json.loads((target / ".game-factory" / "state.json").read_text(encoding="utf-8"))
    assert state["phase"] == "bootstrap"
    assert (target / "docs" / "ONBOARDING.md").exists()
