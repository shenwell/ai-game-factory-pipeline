"""Kie.ai video wrapper (Grok Imagine I2V / T2V).

Independent of mcp-kv. Auth: KIE_API_KEY from the environment or a gitignored
`.env` (project root, `GODOGEN_ROOT`, or the current working directory).

Docs:
  https://docs.kie.ai/market/grok-imagine/image-to-video
  https://docs.kie.ai/market/grok-imagine/text-to-video
  https://docs.kie.ai/file-upload-api/upload-file-stream
  https://docs.kie.ai/market/common/get-task-detail
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

JOBS_BASE = "https://api.kie.ai"
UPLOAD_URLS = (
    "https://kieai.redpandaai.co/api/file-stream-upload",
    "https://api.kie.ai/api/file-stream-upload",
)
CREDIT_URL = f"{JOBS_BASE}/api/v1/chat/credit"
CREATE_URL = f"{JOBS_BASE}/api/v1/jobs/createTask"
RECORD_URL = f"{JOBS_BASE}/api/v1/jobs/recordInfo"

MODEL_I2V = "grok-imagine/image-to-video"
MODEL_T2V = "grok-imagine/text-to-video"

DURATION_MIN = 6
DURATION_MAX = 30
MAX_IMAGE_BYTES = 10 * 1024 * 1024
POLL_TIMEOUT_S = 15 * 60
UPLOAD_PATH = "images/godogen"

GODOGEN_ROOT = Path(os.environ["GODOGEN_ROOT"]) if os.environ.get("GODOGEN_ROOT") else Path.cwd()

_IMAGE_MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


class KieError(RuntimeError):
    pass


def sidecar_path(output: Path) -> Path:
    return output.with_suffix(output.suffix + ".kie.json")


def write_sidecar(output: Path, data: dict) -> None:
    sidecar_path(output).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def read_sidecar(output: Path) -> dict:
    sc = sidecar_path(output)
    if not sc.exists():
        raise FileNotFoundError(f"Sidecar not found: {sc}")
    return json.loads(sc.read_text(encoding="utf-8"))


def _parse_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, rest = line.partition("=")
        key = key.strip()
        if key.startswith("export "):
            key = key[len("export ") :].strip()
        value = rest.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key] = value
    return values


def _candidate_env_files() -> list[Path]:
    seen: set[Path] = set()
    out: list[Path] = []
    candidates = [
        GODOGEN_ROOT / ".env",
        Path.cwd() / ".env",
        Path(__file__).resolve().parents[2] / ".env",  # …/godogen/asset-gen/tools → godogen
        Path(__file__).resolve().parents[3] / ".env" if len(Path(__file__).resolve().parents) > 3 else None,
    ]
    here = Path.cwd()
    for parent in [here, *here.parents]:
        candidates.append(parent / ".env")
    for item in candidates:
        if item is None:
            continue
        resolved = item.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        out.append(item)
    return out


def load_kie_api_key() -> str:
    env_key = (os.environ.get("KIE_API_KEY") or "").strip()
    if env_key:
        return env_key
    for path in _candidate_env_files():
        if not path.is_file():
            continue
        parsed = _parse_dotenv(path)
        value = (parsed.get("KIE_API_KEY") or "").strip()
        if value:
            os.environ["KIE_API_KEY"] = value
            return value
    raise KieError(
        "KIE_API_KEY is not set. Put it in the project `.env` (gitignored) or export "
        "KIE_API_KEY. Create the key at https://kie.ai/api-key"
    )


def mask_key(key: str) -> str:
    if len(key) <= 8:
        return "****"
    return f"{key[:4]}…{key[-4:]}"


def _headers(json_body: bool = True) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {load_kie_api_key()}"}
    if json_body:
        headers["Content-Type"] = "application/json"
    return headers


def _raise_for_kie(resp: requests.Response, context: str) -> dict[str, Any]:
    try:
        payload = resp.json()
    except ValueError:
        payload = {"msg": resp.text[:500]}
    code = payload.get("code", resp.status_code)
    msg = payload.get("msg") or payload.get("message") or resp.reason
    if resp.status_code == 401 or code == 401:
        raise KieError(f"{context}: unauthorized (check KIE_API_KEY). {msg}")
    if resp.status_code == 402 or code == 402:
        raise KieError(f"{context}: insufficient Kie credits. {msg}")
    if resp.status_code == 429 or code == 429:
        raise KieError(f"{context}: rate limited. {msg}")
    if not resp.ok:
        raise KieError(f"{context}: HTTP {resp.status_code} code={code} {msg}")
    if payload.get("success") is False:
        raise KieError(f"{context}: code={code} {msg}")
    return payload


def get_credits() -> dict[str, Any]:
    resp = requests.get(CREDIT_URL, headers=_headers(), timeout=30)
    payload = _raise_for_kie(resp, "credit lookup")
    return payload.get("data") if isinstance(payload.get("data"), dict) else payload


def is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def clamp_duration(seconds: int) -> int:
    return max(DURATION_MIN, min(DURATION_MAX, int(seconds)))


def upload_local_image(image_path: Path) -> str:
    image_path = image_path.resolve()
    if not image_path.is_file():
        raise KieError(f"Reference image not found: {image_path}")
    suffix = image_path.suffix.lower()
    mime = _IMAGE_MIME.get(suffix)
    if mime is None:
        raise KieError(f"Unsupported image type {suffix}; use JPEG, PNG, or WebP")
    size = image_path.stat().st_size
    if size > MAX_IMAGE_BYTES:
        raise KieError(f"Image is {size} bytes; Kie limit is 10MB")

    last_error: Exception | None = None
    for url in UPLOAD_URLS:
        with image_path.open("rb") as fh:
            files = {"file": (image_path.name, fh, mime)}
            data = {
                "uploadPath": UPLOAD_PATH,
                "fileName": image_path.name,
            }
            try:
                resp = requests.post(
                    url,
                    headers={"Authorization": f"Bearer {load_kie_api_key()}"},
                    files=files,
                    data=data,
                    timeout=120,
                )
            except requests.RequestException as exc:
                last_error = exc
                continue
        payload = _raise_for_kie(resp, f"upload via {url}")
        data_obj = payload.get("data") or {}
        download_url = data_obj.get("downloadUrl") or data_obj.get("fileUrl") or data_obj.get("url")
        if not download_url:
            last_error = KieError(f"Upload succeeded but no URL in response: {payload}")
            continue
        return str(download_url)
    raise KieError(f"File upload failed: {last_error}")


def resolve_image_url(image: str | Path | None) -> str | None:
    if image is None:
        return None
    text = str(image).strip()
    if not text:
        return None
    if is_http_url(text):
        return text
    return upload_local_image(Path(text))


def create_task(model: str, input_payload: dict[str, Any]) -> str:
    body = {"model": model, "input": input_payload}
    resp = requests.post(CREATE_URL, headers=_headers(), json=body, timeout=60)
    payload = _raise_for_kie(resp, f"createTask {model}")
    data = payload.get("data") or {}
    task_id = data.get("taskId") or data.get("task_id")
    if not task_id:
        raise KieError(f"createTask returned no taskId: {payload}")
    return str(task_id)


def create_i2v_task(
    *,
    prompt: str,
    image_url: str | None = None,
    source_task_id: str | None = None,
    index: int = 0,
    duration: int = DURATION_MIN,
    resolution: str = "720p",
    mode: str = "normal",
    aspect_ratio: str | None = None,
) -> str:
    if bool(image_url) == bool(source_task_id):
        raise KieError("I2V needs exactly one source: --image (path/URL) or --task-id")
    if mode == "spicy" and image_url:
        raise KieError("Kie spicy mode is not available for external images; use --task-id or --mode normal")
    duration = clamp_duration(duration)
    payload: dict[str, Any] = {
        "prompt": prompt,
        "mode": mode,
        "duration": str(duration),
        "resolution": resolution,
    }
    if image_url:
        payload["image_urls"] = [image_url]
    else:
        payload["task_id"] = source_task_id
        payload["index"] = index
    if aspect_ratio:
        payload["aspect_ratio"] = aspect_ratio
    return create_task(MODEL_I2V, payload)


def create_t2v_task(
    *,
    prompt: str,
    duration: int = DURATION_MIN,
    resolution: str = "720p",
    mode: str = "normal",
    aspect_ratio: str = "1:1",
) -> str:
    duration = clamp_duration(duration)
    return create_task(
        MODEL_T2V,
        {
            "prompt": prompt,
            "mode": mode,
            "duration": str(duration),
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
        },
    )


def _parse_result_urls(result_json: Any) -> list[str]:
    if not result_json:
        return []
    if isinstance(result_json, str):
        try:
            result_json = json.loads(result_json)
        except json.JSONDecodeError:
            return []
    if not isinstance(result_json, dict):
        return []
    urls = result_json.get("resultUrls") or result_json.get("result_urls") or []
    if isinstance(urls, str):
        return [urls]
    return [str(u) for u in urls if u]


def poll_task(task_id: str, *, timeout_s: int = POLL_TIMEOUT_S) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_s
    delay = 3.0
    last_state = "unknown"
    while time.monotonic() < deadline:
        resp = requests.get(RECORD_URL, headers=_headers(), params={"taskId": task_id}, timeout=30)
        payload = _raise_for_kie(resp, f"recordInfo {task_id}")
        data = payload.get("data") or {}
        state = (data.get("state") or "").lower()
        last_state = state or last_state
        if state == "success":
            urls = _parse_result_urls(data.get("resultJson"))
            if not urls:
                raise KieError(f"Task {task_id} succeeded but resultUrls is empty")
            data["result_urls"] = urls
            return data
        if state == "fail":
            raise KieError(
                f"Task {task_id} failed: {data.get('failCode') or ''} {data.get('failMsg') or payload.get('msg')}"
            )
        print(f"  Kie {task_id[:8]}… {state or 'pending'}", flush=True)
        time.sleep(delay)
        delay = min(delay * 1.4, 15.0)
    raise TimeoutError(
        f"Kie task {task_id} still {last_state} after {timeout_s}s. Resume with the sidecar (no extra createTask)."
    )


def download_url(url: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, timeout=180, stream=True)
    resp.raise_for_status()
    tmp = output.with_suffix(output.suffix + ".part")
    with tmp.open("wb") as fh:
        for chunk in resp.iter_content(chunk_size=1024 * 256):
            if chunk:
                fh.write(chunk)
    tmp.replace(output)


def generate_video(
    *,
    prompt: str,
    output: Path,
    image: str | Path | None = None,
    source_task_id: str | None = None,
    index: int = 0,
    duration: int = DURATION_MIN,
    resolution: str = "720p",
    mode: str = "normal",
    aspect_ratio: str | None = None,
) -> dict[str, Any]:
    requested = int(duration)
    duration = clamp_duration(requested)
    if duration != requested:
        print(f"  duration clamped {requested}s → {duration}s (Kie allows {DURATION_MIN}–{DURATION_MAX})", flush=True)

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    image_url = None
    if image:
        print("  Uploading pose to Kie…", flush=True)
        image_url = resolve_image_url(image)

    if image_url or source_task_id:
        model = MODEL_I2V
        task_id = create_i2v_task(
            prompt=prompt,
            image_url=image_url,
            source_task_id=source_task_id,
            index=index,
            duration=duration,
            resolution=resolution,
            mode=mode,
            aspect_ratio=aspect_ratio,
        )
    else:
        model = MODEL_T2V
        task_id = create_t2v_task(
            prompt=prompt,
            duration=duration,
            resolution=resolution,
            mode=mode,
            aspect_ratio=aspect_ratio or "1:1",
        )

    sidecar = {
        "kind": "kie-video",
        "model": model,
        "taskId": task_id,
        "status": "submitted",
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
        "mode": mode,
        "image_url": image_url,
        "source_task_id": source_task_id,
        "index": index,
        "aspect_ratio": aspect_ratio,
    }
    write_sidecar(output, sidecar)
    print(f"  Kie task {task_id} accepted ({model})", flush=True)

    result = poll_task(task_id)
    video_url = result["result_urls"][0]
    print("  Downloading mp4…", flush=True)
    download_url(video_url, output)

    sidecar["status"] = "complete"
    sidecar["result_url"] = video_url
    sidecar["creditsConsumed"] = result.get("creditsConsumed")
    write_sidecar(output, sidecar)

    return {
        "path": str(output),
        "task_id": task_id,
        "model": model,
        "credits": result.get("creditsConsumed"),
        "duration": duration,
        "resolution": resolution,
    }


def resume_video(output: Path) -> dict[str, Any]:
    output = Path(output)
    sidecar = read_sidecar(output)
    if sidecar.get("status") == "complete" and output.is_file():
        return {
            "path": str(output),
            "task_id": sidecar.get("taskId"),
            "model": sidecar.get("model"),
            "credits": 0,
            "resumed": True,
        }
    task_id = sidecar.get("taskId")
    if not task_id:
        raise KieError(f"Kie sidecar has no taskId: {sidecar_path(output)}")
    print(f"  resuming Kie video {task_id}", flush=True)
    result = poll_task(task_id)
    video_url = result["result_urls"][0]
    download_url(video_url, output)
    sidecar["status"] = "complete"
    sidecar["result_url"] = video_url
    sidecar["creditsConsumed"] = result.get("creditsConsumed")
    write_sidecar(output, sidecar)
    return {
        "path": str(output),
        "task_id": task_id,
        "model": sidecar.get("model"),
        "credits": result.get("creditsConsumed"),
        "resumed": True,
    }
