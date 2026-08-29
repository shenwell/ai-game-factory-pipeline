from __future__ import annotations

"""Kie.ai REST client — shared job create/poll/download."""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

import requests

API_BASE = "https://api.kie.ai/api/v1"


class KieJobError(Exception):
    pass


class UnknownSubmission(KieJobError):
    """createTask may have charged but no task id returned."""


def load_api_key(project_root: Path, env_key: str = "KIE_API_KEY") -> str:
    key = os.environ.get(env_key)
    if key:
        return key.strip()
    env_file = project_root / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith(f"{env_key}="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise KieJobError(f"{env_key} not set")


def create_task(api_key: str, model: str, input_payload: dict[str, Any]) -> str:
    url = f"{API_BASE}/jobs/createTask"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {"model": model, "input": input_payload}
    intent_path = None  # caller writes intent sidecar before POST
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=120)
    except requests.RequestException as e:
        raise UnknownSubmission(str(e)) from e
    if resp.status_code != 200:
        raise KieJobError(f"createTask HTTP {resp.status_code}: {resp.text[:500]}")
    data = resp.json()
    task_id = data.get("data", {}).get("taskId") or data.get("taskId")
    if not task_id:
        raise UnknownSubmission(f"No taskId in response: {data}")
    return str(task_id)


def poll_task(api_key: str, task_id: str, timeout_sec: int = 600) -> dict[str, Any]:
    url = f"{API_BASE}/jobs/recordInfo"
    headers = {"Authorization": f"Bearer {api_key}"}
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        resp = requests.get(url, headers=headers, params={"taskId": task_id}, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        status = (data.get("data") or data).get("status", "")
        if status in ("success", "failed", "fail"):
            return data
        time.sleep(5)
    raise KieJobError(f"poll timeout for {task_id}")


def write_sidecar(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
