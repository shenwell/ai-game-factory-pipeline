# Onboarding

This folder is the **game**. The factory (`ai-game-factory`) stays in its own repo.

## After install

1. Stay here (this directory). Run `game-factory onboard`.
2. Set `project.name` and `project.display_name` in `game-factory.config.yaml`.
3. Copy `.env.example` → `.env`. Put `KIE_API_KEY` there if you will generate images/video. Design can start without it (procedural fallback).
4. Godot **4.7.x .NET** and **.NET SDK 9** must be on `PATH`.
5. In Cursor, run **`/game-factory-mvp`**. The agent reads `.game-factory/state.json` and resumes; do not skip phases.
6. The agent must not copy another game’s code or design unless you name that project and what to reuse.

## What must be present

| Item | Role |
|------|------|
| `game-factory.config.yaml` | Settings (single file) |
| `.game-factory/state.json` | Pipeline phase |
| `AGENTS.md`, `GAME.md`, `godot.md` | Agent + design canon |
| `docs/design/UI.md` | Screen inventory, popups, MVP defer / v1 shell |
| `.agents/skills/` | MVP, produce, game-design, asset-gen |
| `.cursor/commands/game-factory-*` | Slash commands |

## Human gates

- Design approval (`awaitingDesignApproval`)
- Playtest (`awaitingPlaytest`)

Re-check anytime: `game-factory onboard`.
