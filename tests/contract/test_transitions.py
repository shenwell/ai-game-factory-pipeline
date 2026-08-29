from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from game_factory.state import load_state, save_state
from game_factory.transitions import transition


@pytest.fixture
def project(tmp_path: Path):
    (tmp_path / ".game-factory").mkdir()
    save_state(tmp_path, load_state(tmp_path))
    return tmp_path


def test_transition_bootstrap_to_design(project: Path):
    transition(project, "design", "toolchain ok")
    assert load_state(project)["phase"] == "design"


def test_illegal_transition(project: Path):
    with pytest.raises(ValueError):
        transition(project, "done", "skip")
