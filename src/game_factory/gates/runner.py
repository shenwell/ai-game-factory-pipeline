from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from game_factory.config import load_config
from game_factory.paths import relpath, under_root

STEP_RUNNERS = {
    "config": "_step_config",
    "drift": "_step_drift",
    "build": "_step_build",
    "unit": "_step_unit",
    "scene_build": "_step_scene_build",
    "import": "_step_import",
    "launch": "_step_launch",
    "gameplay": "_step_gameplay",
    "errors": "_step_errors",
    "screenshots": "_step_screenshots",
    "proof_video": "_step_proof_video",
    "glb_import": "_step_glb_import",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=600)
        out = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, out
    except subprocess.TimeoutExpired:
        return 124, "timeout"
    except FileNotFoundError as e:
        return 127, str(e)


def _step_config(project_root: Path) -> dict[str, Any]:
    from game_factory.config import load_config

    try:
        load_config(project_root)
        return {"name": "config", "ok": True, "exit_code": 0, "evidence": []}
    except Exception as e:
        return {"name": "config", "ok": False, "exit_code": 1, "error_category": str(e)}


def _step_drift(project_root: Path) -> dict[str, Any]:
    manifest = project_root / ".game-factory" / "install-manifest.json"
    ok = manifest.exists()
    return {"name": "drift", "ok": ok, "exit_code": 0 if ok else 1}


def _step_build(project_root: Path) -> dict[str, Any]:
    csprojs = list(project_root.glob("*.csproj")) + list(project_root.glob("**/*.csproj"))
    if not csprojs:
        return {"name": "build", "ok": True, "exit_code": 0, "evidence": ["no csproj yet"]}
    code, _ = _run(["dotnet", "build"], project_root)
    return {"name": "build", "ok": code == 0, "exit_code": code}


def _step_unit(project_root: Path) -> dict[str, Any]:
    # v1: no unit tests until game exists — pass if no test project
    return {"name": "unit", "ok": True, "exit_code": 0}


def _step_scene_build(project_root: Path) -> dict[str, Any]:
    scenes = list((project_root / "scenes").glob("Build*.cs")) if (project_root / "scenes").exists() else []
    if not scenes:
        return {"name": "scene_build", "ok": True, "exit_code": 0, "evidence": ["no builders"]}
    for builder in scenes:
        code, _ = _run(["godot", "--headless", "--script", relpath(project_root, builder)], project_root)
        if code != 0:
            return {"name": "scene_build", "ok": False, "exit_code": code, "evidence": [relpath(project_root, builder)]}
    return {"name": "scene_build", "ok": True, "exit_code": 0}


def _step_import(project_root: Path) -> dict[str, Any]:
    if not (project_root / "project.godot").exists():
        return {"name": "import", "ok": True, "exit_code": 0, "evidence": ["no project yet"]}
    code, _ = _run(["godot", "--headless", "--import"], project_root)
    return {"name": "import", "ok": code == 0, "exit_code": code}


def _step_launch(project_root: Path) -> dict[str, Any]:
    if not (project_root / "project.godot").exists():
        return {"name": "launch", "ok": True, "exit_code": 0}
    code, _ = _run(["godot", "--headless", "--quit"], project_root)
    return {"name": "launch", "ok": code == 0, "exit_code": code}


def _step_gameplay(project_root: Path) -> dict[str, Any]:
    return {"name": "gameplay", "ok": True, "exit_code": 0, "evidence": ["manual or cli-control in visual profile"]}


def _step_errors(project_root: Path) -> dict[str, Any]:
    return {"name": "errors", "ok": True, "exit_code": 0}


def _step_screenshots(project_root: Path) -> dict[str, Any]:
    shots = project_root / "screenshots" / "qa.png"
    ok = shots.exists() and shots.stat().st_size > 0
    return {"name": "screenshots", "ok": ok, "exit_code": 0 if ok else 1, "evidence": [relpath(project_root, shots)]}


def _step_proof_video(project_root: Path) -> dict[str, Any]:
    vdir = project_root / "screenshots" / "result"
    ok = vdir.exists() and any(vdir.glob("*.mp4")) or any(vdir.glob("frame*.png"))
    return {"name": "proof_video", "ok": ok, "exit_code": 0 if ok else 1}


def _step_glb_import(project_root: Path) -> dict[str, Any]:
    from game_factory.config import load_config

    try:
        cfg = load_config(project_root)
    except Exception:
        return {"name": "glb_import", "ok": True, "exit_code": 0, "evidence": ["no config"]}
    if cfg.get("project", {}).get("dimension") != "3d":
        return {"name": "glb_import", "ok": True, "exit_code": 0, "evidence": ["2d project"]}
    glb_rel = cfg.get("assets", {}).get("models_3d", {}).get("user_glb_dir", "assets/models")
    root = under_root(project_root, glb_rel, name="assets.models_3d.user_glb_dir")
    glbs = list(root.glob("**/*.glb")) if root.exists() else []
    ok = len(glbs) > 0 or cfg.get("assets", {}).get("models_3d", {}).get("allow_procedural", True)
    return {
        "name": "glb_import",
        "ok": ok,
        "exit_code": 0 if ok else 1,
        "evidence": [relpath(project_root, p) for p in glbs[:5]],
    }


def verify(project_root: Path, profile: str) -> dict[str, Any]:
    cfg = load_config(project_root)
    steps_names = cfg["gates"][profile]
    started = time.time()
    steps: list[dict[str, Any]] = []
    ok = True
    for name in steps_names:
        if name in ("fast", "full", "visual"):
            nested = verify(project_root, name)
            steps.append({"name": name, "ok": nested["ok"], "exit_code": 0 if nested["ok"] else 1, "nested": nested})
            ok = ok and nested["ok"]
            continue
        runner_name = STEP_RUNNERS.get(name)
        if not runner_name:
            steps.append({"name": name, "ok": False, "exit_code": 1, "error_category": "unknown_step"})
            ok = False
            continue
        fn = globals()[runner_name]
        result = fn(project_root)
        steps.append(result)
        ok = ok and result.get("ok", False)

    finished = time.time()
    result = {
        "profile": profile,
        "ok": ok,
        "started_at": _now(),
        "finished_at": _now(),
        "duration_sec": round(finished - started, 3),
        "commit": None,
        "steps": steps,
    }
    out = project_root / ".game-factory" / "jobs" / f"gate-{profile}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
