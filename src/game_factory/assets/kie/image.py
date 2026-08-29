from __future__ import annotations

"""Kie text-to-image and image-to-image adapters."""

import json
from pathlib import Path
from typing import Any

from game_factory.assets.kie.client import (
    KieJobError,
    UnknownSubmission,
    create_task,
    poll_task,
    write_sidecar,
)


def sidecar_path(output: Path) -> Path:
    return output.with_suffix(output.suffix + ".kie.json")


def generate_text_to_image(
    api_key: str,
    model: str,
    prompt: str,
    output: Path,
    *,
    aspect_ratio: str = "1:1",
) -> dict[str, Any]:
    output.parent.mkdir(parents=True, exist_ok=True)
    intent = {
        "kind": "t2i",
        "model": model,
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "status": "pending",
    }
    write_sidecar(sidecar_path(output), intent)
    try:
        task_id = create_task(api_key, model, {"prompt": prompt, "aspect_ratio": aspect_ratio})
    except UnknownSubmission as e:
        intent["status"] = "unknown_submission"
        intent["error"] = str(e)
        write_sidecar(sidecar_path(output), intent)
        raise
    intent["task_id"] = task_id
    write_sidecar(sidecar_path(output), intent)
    result = poll_task(api_key, task_id)
    url = _extract_image_url(result)
    _download(url, output)
    intent["status"] = "complete"
    write_sidecar(sidecar_path(output), intent)
    return {"ok": True, "path": str(output), "task_id": task_id}


def generate_image_to_image(
    api_key: str,
    model: str,
    prompt: str,
    image_path: Path,
    output: Path,
    *,
    aspect_ratio: str = "1:1",
) -> dict[str, Any]:
    output.parent.mkdir(parents=True, exist_ok=True)
    intent = {
        "kind": "i2i",
        "model": model,
        "prompt": prompt,
        "source": str(image_path),
        "aspect_ratio": aspect_ratio,
        "status": "pending",
    }
    write_sidecar(sidecar_path(output), intent)
    import base64

    b64 = base64.b64encode(image_path.read_bytes()).decode()
    mime = "image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"
    payload = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "image": f"data:{mime};base64,{b64}",
    }
    try:
        task_id = create_task(api_key, model, payload)
    except UnknownSubmission as e:
        intent["status"] = "unknown_submission"
        intent["error"] = str(e)
        write_sidecar(sidecar_path(output), intent)
        raise
    intent["task_id"] = task_id
    write_sidecar(sidecar_path(output), intent)
    result = poll_task(api_key, task_id)
    url = _extract_image_url(result)
    _download(url, output)
    intent["status"] = "complete"
    write_sidecar(sidecar_path(output), intent)
    return {"ok": True, "path": str(output), "task_id": task_id}


def _extract_image_url(result: dict[str, Any]) -> str:
    if result.get("result_urls"):
        return str(result["result_urls"][0])
    data = result.get("data") or result
    for key in ("resultUrl", "imageUrl", "url"):
        if data.get(key):
            return str(data[key])
    output = data.get("output") or data.get("result")
    if isinstance(output, dict):
        for key in ("url", "imageUrl", "resultUrl"):
            if output.get(key):
                return str(output[key])
    if isinstance(output, str) and output.startswith("http"):
        return output
    raise KieJobError(f"No image URL in Kie response: {json.dumps(result)[:500]}")


def _download(url: str, output: Path) -> None:
    import requests

    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    output.write_bytes(resp.content)
