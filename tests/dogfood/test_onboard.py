from __future__ import annotations

import json
from pathlib import Path

from game_factory.onboard import run_onboard

REPO = Path(__file__).resolve().parents[2]


def _load_init_module():
    import importlib.util

    spec = importlib.util.spec_from_file_location("gf_init", REPO / "install" / "init.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_onboard_after_fresh_init(tmp_path: Path, capsys):
    target = tmp_path / "game"
    _load_init_module().init_project(REPO, target)
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["onboard"]["ready"] is True
    assert payload["onboard"]["ready_for_design"] is True
    assert payload["onboard"]["phase"] == "bootstrap"
    assert (target / "docs" / "ONBOARDING.md").is_file()
    assert (target / ".agents" / "skills" / "game-factory-onboard" / "SKILL.md").is_file()
    names = {c["name"] for c in payload["onboard"]["checks"]}
    assert "config" in names
    assert "python" in names
    report = run_onboard(target)
    assert report["ok"] is True
    warn_names = {w["name"] for w in report["warnings"]}
    assert "project.name" in warn_names
    assert "kie_api_key" in warn_names
    assert payload["onboard"]["reminders"]
    assert any("KIE_API_KEY" in r for r in payload["onboard"]["reminders"])
    assert "KIE_API_KEY" in captured.err


def test_onboard_missing_project(tmp_path: Path):
    report = run_onboard(tmp_path)
    assert report["ok"] is False
    assert any(b["name"].startswith("file:") for b in report["blockers"])
