from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from game_factory.assets.kie.image import generate_text_to_image
from game_factory.assets.kie.ledger import load_ledger, record_job


def test_ledger_records_job(tmp_path: Path):
    record_job(tmp_path, {"task_id": "t1", "credits": 2, "model": "grok-imagine/text-to-image"})
    ledger = load_ledger(tmp_path)
    assert len(ledger["jobs"]) == 1
    assert ledger["credits_estimated"] == 2


def test_t2i_mock(tmp_path: Path):
    out = tmp_path / "out.png"
    fake_poll = {"result_urls": ["http://example.com/x.png"]}
    with (
        patch("game_factory.assets.kie.image.create_task", return_value="abc"),
        patch("game_factory.assets.kie.image.poll_task", return_value=fake_poll),
        patch("game_factory.assets.kie.image._download"),
    ):
        result = generate_text_to_image("key", "grok-imagine/text-to-image", "hero", out)
    assert result["task_id"] == "abc"
    assert out.with_suffix(out.suffix + ".kie.json").exists()
