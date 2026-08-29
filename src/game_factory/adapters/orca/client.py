from __future__ import annotations

import json
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _jobs_dir(project_root: Path) -> Path:
    d = project_root / ".game-factory" / "jobs" / "orca"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_job(project_root: Path, job_id: str) -> dict[str, Any]:
    path = _jobs_dir(project_root) / f"{job_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Orca job not found: {job_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def _save_job(project_root: Path, job: dict[str, Any]) -> None:
    path = _jobs_dir(project_root) / f"{job['job_id']}.json"
    path.write_text(json.dumps(job, indent=2), encoding="utf-8")


def _orca_available() -> bool:
    try:
        subprocess.run(["orca", "--version"], capture_output=True, check=False, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def dispatch(project_root: Path, work_order_path: Path, *, orca_project_id: str | None = None) -> dict[str, Any]:
    wo = json.loads(work_order_path.read_text(encoding="utf-8"))
    job_id = f"orca-{uuid.uuid4().hex[:12]}"
    job: dict[str, Any] = {
        "job_id": job_id,
        "status": "queued",
        "work_order": wo,
        "created_at": _now(),
        "orca_task_id": None,
        "result": None,
    }
    if _orca_available() and orca_project_id:
        try:
            spec = json.dumps(wo, ensure_ascii=False)
            proc = subprocess.run(
                [
                    "orca",
                    "orchestration",
                    "task-create",
                    "--spec",
                    spec,
                    "--task-title",
                    wo.get("id", "work-order"),
                    "--display-name",
                    wo.get("zone", "batch"),
                    "--json",
                ],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=project_root,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                payload = json.loads(proc.stdout)
                job["orca_task_id"] = payload.get("id") or payload.get("taskId")
                job["status"] = "dispatched"
        except (json.JSONDecodeError, subprocess.TimeoutExpired):
            job["status"] = "queued_local"
    else:
        job["status"] = "queued_local"
    _save_job(project_root, job)
    return {"job_id": job_id, "status": job["status"], "orca_task_id": job.get("orca_task_id")}


def status(project_root: Path, job_id: str) -> dict[str, Any]:
    job = _load_job(project_root, job_id)
    if job.get("orca_task_id") and _orca_available():
        try:
            proc = subprocess.run(
                ["orca", "orchestration", "task-status", "--task", job["orca_task_id"], "--json"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=project_root,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                job["orca_status"] = json.loads(proc.stdout)
                job["status"] = job["orca_status"].get("status", job["status"])
                _save_job(project_root, job)
        except (json.JSONDecodeError, subprocess.TimeoutExpired):
            pass
    return {"job_id": job_id, "status": job["status"], "orca_task_id": job.get("orca_task_id")}


def collect(project_root: Path, job_id: str) -> dict[str, Any]:
    job = _load_job(project_root, job_id)
    if job.get("status") not in ("complete", "dispatched", "queued_local"):
        status(project_root, job_id)
        job = _load_job(project_root, job_id)
    if job.get("orca_task_id") and _orca_available():
        try:
            proc = subprocess.run(
                ["orca", "orchestration", "task-collect", "--task", job["orca_task_id"], "--json"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=project_root,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                job["result"] = json.loads(proc.stdout)
                job["status"] = "complete"
                job["collected_at"] = _now()
                _save_job(project_root, job)
        except (json.JSONDecodeError, subprocess.TimeoutExpired):
            pass
    if job["status"] == "queued_local":
        job["status"] = "complete"
        job["result"] = {"mode": "local", "work_order_id": job["work_order"].get("id")}
        job["collected_at"] = _now()
        _save_job(project_root, job)
    return {"job_id": job_id, "status": job["status"], "result": job.get("result")}


def cancel(project_root: Path, job_id: str) -> dict[str, Any]:
    job = _load_job(project_root, job_id)
    if job.get("orca_task_id") and _orca_available():
        try:
            subprocess.run(
                ["orca", "orchestration", "task-cancel", "--task", job["orca_task_id"]],
                capture_output=True,
                timeout=30,
                cwd=project_root,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
    job["status"] = "cancelled"
    job["cancelled_at"] = _now()
    _save_job(project_root, job)
    return {"job_id": job_id, "status": "cancelled"}
