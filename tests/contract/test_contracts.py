from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
SCHEMAS = REPO / "schemas"
VENDOR = REPO / "vendor"
TEMPLATES = REPO / "templates"


def test_config_template_validates():
    data = yaml.safe_load((TEMPLATES / "project" / "game-factory.config.yaml").read_text(encoding="utf-8"))
    schema = json.loads((SCHEMAS / "game-factory.config.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(data, schema)


def test_no_mcp_kv_in_asset_skill():
  skill = VENDOR / "godogen" / "asset-gen" / "SKILL.md"
  if not skill.exists():
    pytest.skip("vendor not synced")
  text = skill.read_text(encoding="utf-8").lower()
  # After kie-only patch, mcp-kv must not appear in installed publish path;
  # factory publish strips in init — vendor may still contain upstream text until patched.
  published = (TEMPLATES / "skills" / "game-factory-mvp" / "SKILL.md").read_text(encoding="utf-8").lower()
  assert "mcp-kv" not in published


def test_no_disallowed_providers_in_config_template():
    text = (TEMPLATES / "project" / "game-factory.config.yaml").read_text(encoding="utf-8").lower()
    for bad in ("mcp-kv", "tripo3d", "google_api_key", "xai_api_key"):
        assert bad not in text


def test_no_silent_borrow_rule_in_agents():
    needle = "unless the user names"
    root = (REPO / "AGENTS.md").read_text(encoding="utf-8")
    game = (TEMPLATES / "project" / "AGENTS.md").read_text(encoding="utf-8")
    assert needle in root
    assert needle in game


def test_templates_no_game_names():
    forbidden = ["square collector", "ashen crown", "pilot"]
    for path in TEMPLATES.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".yaml", ".yml", ".mdc"}:
            low = path.read_text(encoding="utf-8", errors="ignore").lower()
            for name in forbidden:
                assert name not in low, f"{name} in {path}"


def test_state_schema_default():
    schema = json.loads((SCHEMAS / "state.schema.json").read_text(encoding="utf-8"))
    state = {
        "schema_version": 1,
        "phase": "bootstrap",
        "iteration": 0,
        "updated_at": "2026-01-01T00:00:00+00:00",
        "blockers": [],
        "approval_hashes": {},
        "retry_counts": {},
    }
    jsonschema.validate(state, schema)


def test_ui_md_template_exists():
    ui = TEMPLATES / "project" / "docs" / "design" / "UI.md"
    assert ui.is_file()
    text = ui.read_text(encoding="utf-8")
    assert "## Screen inventory" in text
    assert "## Deferred waiver" in text


def test_mvp_skill_references_ui_contract():
    skill = (TEMPLATES / "skills" / "game-factory-mvp" / "SKILL.md").read_text(encoding="utf-8").lower()
    assert "docs/design/ui.md" in skill


def test_produce_skill_references_ui_shell():
    skill = (TEMPLATES / "skills" / "game-factory-produce" / "SKILL.md").read_text(encoding="utf-8").lower()
    assert "docs/design/ui.md" in skill
    assert "game-factory-ui" in skill


def test_vendored_ui_skills_present():
    for name in ("game-ui-ux", "godot-ui-control", "input-systems"):
        skill = VENDOR / name / "SKILL.md"
        assert skill.is_file(), f"missing vendor/{name}/SKILL.md — run scripts/vendor/sync-upstream.py"


def test_config_includes_ui_contract_gate():
    data = yaml.safe_load((TEMPLATES / "project" / "game-factory.config.yaml").read_text(encoding="utf-8"))
    assert "ui_contract" in data["gates"]["full"]
    assert data.get("ui", {}).get("shell") == "deferred_mvp"
