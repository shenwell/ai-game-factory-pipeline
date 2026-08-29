# Project memory

**How we work on this game** — process, approach, gotchas, handoffs. **Not** game design canon.

## Canon (edit there, not here)

- `GAME.md`, `docs/GDD.md`, `docs/design/LOOPS.md`, `docs/MVP_DONE.md`, `docs/DONE.md`
- `game-factory.config.yaml`, `AGENTS.md`, `godot.md`

## What belongs in `memory/`

- Подход к реализации, порядок проверок, локальные процедуры.
- Gotchas, обходные пути, open loops, итоги отладки.
- Сессионный handoff (memo-session-skill).

## Agent flow

1. Read `AGENTS.md` (rules) → canon docs for game facts → `MEMORY.md` → `memory/hot-cache.md`.
2. Permanent rule → `AGENTS.md` or the right `docs/` file; then remove duplicate from hot-cache.
3. Wrap-up: **memo-session-skill** (see `AGENTS.md`).

Create `memory/hot-cache.md`, `memory/open-loops.md`, etc. on first memo-session bootstrap.
