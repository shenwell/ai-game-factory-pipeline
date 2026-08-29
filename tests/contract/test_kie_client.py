from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from game_factory.assets.kie.client import KieJobError, UnknownSubmission, create_task


def test_create_task_returns_id():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"data": {"taskId": "abc123"}}
    with patch("game_factory.assets.kie.client.requests.post", return_value=mock_resp):
        assert create_task("key", "model/x", {"prompt": "test"}) == "abc123"


def test_unknown_submission_no_task_id():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"data": {}}
    with patch("game_factory.assets.kie.client.requests.post", return_value=mock_resp):
        with pytest.raises(UnknownSubmission):
            create_task("key", "model/x", {})


def test_create_task_http_error():
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "fail"
    with patch("game_factory.assets.kie.client.requests.post", return_value=mock_resp):
        with pytest.raises(KieJobError):
            create_task("key", "model/x", {})
