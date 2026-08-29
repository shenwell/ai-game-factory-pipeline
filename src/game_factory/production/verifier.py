from __future__ import annotations

from pathlib import Path
from typing import Any

from game_factory.gates.runner import verify
from game_factory.production.producer import production_status


def independent_verify(project_root: Path) -> dict[str, Any]:
    """Verifier pass before transition to done."""
    status = production_status(project_root)
    full = verify(project_root, "full")
    done_md = project_root / "docs" / "DONE.md"
    done_exists = done_md.exists() and done_md.stat().st_size > 0
    ok = full["ok"] and status["can_release"] and done_exists
    return {
        "ok": ok,
        "production": status,
        "gates": full,
        "done_md": done_exists,
    }
