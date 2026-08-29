from __future__ import annotations

"""Post-install onboarding: verify the game project can start the pipeline."""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from game_factory import __version__
from game_factory.assets.kie.client import load_api_key
from game_factory.config import load_config
from game_factory.state import load_state

REQUIRED_FILES = (
    "game-factory.config.yaml",
    "AGENTS.md",
    "GAME.md",
    "godot.md",
    ".env.example",
    "docs/ONBOARDING.md",
    "docs/GDD.md",
    "docs/design/LOOPS.md",
    "docs/MVP_DONE.md",
    ".game-factory/state.json",
    ".game-factory/install-manifest.json",
    ".agents/skills/game-factory-mvp/SKILL.md",
    ".agents/skills/game-design/SKILL.md",
    ".agents/skills/game-factory-onboard/SKILL.md",
    ".cursor/commands/game-factory-mvp.md",
    ".cursor/commands/game-factory-onboard.md",
)

NEXT_STEPS = [
    "Work in this game folder, not in the ai-game-factory repo.",
    "Set project.name and project.display_name in game-factory.config.yaml.",
    "Copy .env.example to .env and set KIE_API_KEY (https://kie.ai/api-key) if you will generate assets.",
    "Install Godot 4.7.x .NET and .NET SDK 9 so they are on PATH.",
    "Open this folder in Cursor and run /game-factory-mvp (or: game-factory onboard).",
    "Human gates later: awaitingDesignApproval, then awaitingPlaytest.",
]


def _check(name: str, ok: bool, *, level: str, detail: str) -> dict[str, Any]:
    return {"name": name, "ok": ok, "level": level, "detail": detail}


def _version_tuple(raw: str) -> tuple[int, int, int]:
    nums = [int(p) for p in re.findall(r"\d+", raw)[:3]]
    while len(nums) < 3:
        nums.append(0)
    return nums[0], nums[1], nums[2]


def _spec_ok(installed: tuple[int, int, int], spec: str) -> bool:
    for clause in spec.split(","):
        clause = clause.strip()
        if not clause:
            continue
        if clause.startswith(">="):
            if installed < _version_tuple(clause[2:]):
                return False
        elif clause.startswith("<="):
            if installed > _version_tuple(clause[2:]):
                return False
        elif clause.startswith("=="):
            if installed != _version_tuple(clause[2:]):
                return False
        elif clause.startswith(">"):
            if installed <= _version_tuple(clause[1:]):
                return False
        elif clause.startswith("<"):
            if installed >= _version_tuple(clause[1:]):
                return False
        else:
            if installed != _version_tuple(clause):
                return False
    return True


def _cmd_version(cmd: list[str]) -> str | None:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None
    text = (proc.stdout or "") + (proc.stderr or "")
    return text.strip() or None


def _which_godot() -> str | None:
    for name in ("godot", "godot.exe"):
        found = shutil.which(name)
        if found:
            return found
    return os.environ.get("GODOT") or os.environ.get("GODOT_BIN")


def run_onboard(project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    checks: list[dict[str, Any]] = []

    for rel in REQUIRED_FILES:
        path = root / rel
        checks.append(
            _check(
                f"file:{rel}",
                path.is_file(),
                level="blocker",
                detail="present" if path.is_file() else f"missing {rel}",
            )
        )

    cfg = None
    try:
        cfg = load_config(root)
        checks.append(_check("config", True, level="blocker", detail="game-factory.config.yaml valid"))
    except Exception as e:
        checks.append(_check("config", False, level="blocker", detail=str(e)))

    try:
        state = load_state(root)
        checks.append(
            _check(
                "state",
                True,
                level="blocker",
                detail=f"phase={state.get('phase')}",
            )
        )
    except Exception as e:
        checks.append(_check("state", False, level="blocker", detail=str(e)))
        state = {}

    py_spec = (cfg or {}).get("toolchain", {}).get("python", ">=3.11")
    py_ver = sys.version_info[:3]
    checks.append(
        _check(
            "python",
            _spec_ok(py_ver, py_spec),
            level="blocker",
            detail=f"{py_ver[0]}.{py_ver[1]}.{py_ver[2]} (need {py_spec})",
        )
    )

    name = ((cfg or {}).get("project") or {}).get("name") or ""
    checks.append(
        _check(
            "project.name",
            bool(str(name).strip()),
            level="warn",
            detail="set in game-factory.config.yaml" if not str(name).strip() else str(name),
        )
    )

    godot_bin = _which_godot()
    godot_spec = (cfg or {}).get("toolchain", {}).get("godot", ">=4.7.2,<4.8")
    if not godot_bin:
        checks.append(
            _check("godot", False, level="warn", detail="not on PATH — needed before mvpBuild (Godot 4.7.x .NET)")
        )
    else:
        raw = _cmd_version([godot_bin, "--version"])
        ok = bool(raw) and _spec_ok(_version_tuple(raw), godot_spec)
        checks.append(
            _check(
                "godot",
                ok,
                level="warn",
                detail=f"{raw.splitlines()[0] if raw else 'no --version'} (need {godot_spec})",
            )
        )

    dotnet = shutil.which("dotnet")
    dotnet_spec = (cfg or {}).get("toolchain", {}).get("dotnet", ">=9,<10")
    if not dotnet:
        checks.append(_check("dotnet", False, level="warn", detail="dotnet not on PATH — needed before mvpBuild (SDK 9)"))
    else:
        raw = _cmd_version(["dotnet", "--version"])
        ok = bool(raw) and _spec_ok(_version_tuple(raw or ""), dotnet_spec)
        checks.append(
            _check(
                "dotnet",
                ok,
                level="warn",
                detail=f"{raw or 'unknown'} (need {dotnet_spec})",
            )
        )

    env_key = (cfg or {}).get("assets", {}).get("env_key", "KIE_API_KEY")
    try:
        key = load_api_key(root, env_key)
        checks.append(_check("kie_api_key", bool(key), level="warn", detail=f"{env_key} set"))
    except Exception:
        checks.append(
            _check(
                "kie_api_key",
                False,
                level="warn",
                detail=(
                    "KIE_API_KEY is not set. Copy .env.example → .env and paste the key from "
                    "https://kie.ai/api-key — required for image/video generation; design can start without it"
                ),
            )
        )

    addon = root / "addons" / "godot_cli_control" / "plugin.cfg"
    checks.append(
        _check(
            "godot_cli_control",
            addon.is_file(),
            level="warn",
            detail="present" if addon.is_file() else "missing addons/godot_cli_control (needed for visual proof)",
        )
    )

    blockers = [c for c in checks if c["level"] == "blocker" and not c["ok"]]
    warnings = [c for c in checks if c["level"] == "warn" and not c["ok"]]
    toolchain_ok = all(
        c["ok"] for c in checks if c["name"] in {"godot", "dotnet"}
    )
    ok = len(blockers) == 0
    reminders: list[str] = []
    if any(w["name"] == "kie_api_key" for w in warnings):
        reminders.append(
            "Set KIE_API_KEY in .env (copy from .env.example). Get a key at https://kie.ai/api-key"
        )
    if any(w["name"] == "project.name" for w in warnings):
        reminders.append("Set project.name and project.display_name in game-factory.config.yaml")
    return {
        "ok": ok,
        "factory_version": __version__,
        "ready": ok,
        "ready_for_design": ok,
        "ready_for_mvp_build": ok and toolchain_ok,
        "phase": state.get("phase"),
        "blockers": blockers,
        "warnings": warnings,
        "reminders": reminders,
        "checks": checks,
        "next_steps": NEXT_STEPS,
        "docs": "docs/ONBOARDING.md",
    }


def format_onboard_line(report: dict[str, Any]) -> str:
    reminders = report.get("reminders") or []
    hint = f" Reminder: {reminders[0]}" if reminders else ""
    if report.get("ok"):
        n = len(report.get("warnings") or [])
        extra = f" ({n} warning{'s' if n != 1 else ''})" if n else ""
        return f"Onboard: ready to start the pipeline{extra}. Read docs/ONBOARDING.md.{hint}"
    n = len(report.get("blockers") or [])
    return (
        f"Onboard: not ready ({n} blocker{'s' if n != 1 else ''}). "
        f"Fix onboard.blockers, then: game-factory onboard.{hint}"
    )
