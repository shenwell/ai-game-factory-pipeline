from __future__ import annotations

from typing import Any

from game_factory.events import append_event
from game_factory.state import load_state, save_state

ALLOWED: dict[str, set[str]] = {
    "bootstrap": {"design"},
    "design": {"awaitingDesignApproval"},
    "awaitingDesignApproval": {"mvpBuild", "design"},
    "mvpBuild": {"mvpVerify"},
    "mvpVerify": {"mvpBuild", "awaitingPlaytest"},
    "awaitingPlaytest": {"production", "mvpBuild"},
    "production": {"releaseCandidate"},
    "releaseCandidate": {"production", "done"},
    "done": {"production"},  # reopen via bug-*
}


def transition(project_root, new_phase: str, reason: str, **extra: Any) -> dict[str, Any]:
    state = load_state(project_root)
    current = state["phase"]
    allowed = ALLOWED.get(current, set())
    if new_phase not in allowed:
        raise ValueError(f"Illegal transition {current} -> {new_phase}: {reason}")
    state["phase"] = new_phase
    state["iteration"] = int(state.get("iteration", 0)) + 1
    for key, value in extra.items():
        state[key] = value
    save_state(project_root, state)
    append_event(project_root, "transition", {"from": current, "to": new_phase, "reason": reason})
    return state
