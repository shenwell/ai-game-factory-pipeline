# ai-game-factory — agent guide

This repository is the **factory** (Python CLI, templates, vendor sync), not a Godot game. Installed games get their own `AGENTS.md` from `templates/project/`.

## What to read first

- `README.md` — quick start, v1.1 commands
- `CHANGELOG.md` — version history
- `docs/ARCHITECTURE.md`, `docs/STATE-MACHINE.md`, `docs/ORCA-ADAPTER.md`
- `pyproject.toml` — package version and entry point `game-factory`

## Development rules

- **Borrow-first:** do not rewrite `vendor/` prose; sync via `python scripts/vendor/sync-upstream.py`; patches only in `vendor/patches/`.
- **Tests:** `pip install -e ".[dev]"` then `pytest tests/` from repo root (use `.venv` on Windows).
- **Init contract:** fresh install = empty dir only; v1.1 adds `--upgrade` and `--into-existing` (Godot overlay).
- **Pipeline state** for *installed games* lives in `.game-factory/state.json` — that is machine state, not agent memory. Do not store factory dev notes there.
- **No game names** in templates, tests, or factory docs.
- **Commits / push** — only when the user explicitly asks.

## CLI (this repo)

```text
game-factory status
game-factory migrate
pytest tests/
python install/init.py --out <path>
python scripts/vendor/sync-upstream.py
```

## Canon vs memory (do not mix)

**Canon** = durable source of truth the agent must obey. Edit in place when facts change; do not copy into `memory/`.

| Kind | Where (this repo) |
|------|-------------------|
| Factory architecture, CLI, schemas | `docs/`, `schemas/`, `src/`, `README.md`, `CHANGELOG.md` |
| Behavior rules for agents | **`AGENTS.md`**, `.cursor/rules/` |
| Shipped game project contract | `templates/project/*` (copied on init) |
| Vendor upstream text | `vendor/` (+ `vendor/patches/`) |

**Memory** = how we work on the factory: approach, procedures, gotchas, open loops, session handoff. **Not** canon.

| Belongs in `memory/` | Does **not** belong in `memory/` |
|----------------------|----------------------------------|
| «Почему выбрали такой diff в init» | Текст схемы или state machine → `docs/` |
| Обходной путь при sync на Windows | Дублирование `AGENTS.md` |
| Открытые задачи по фабрике | Описание игры, GDD, механики |
| ADR по разработке фабрики | `game-factory.config.yaml` шаблона |

Installed **games** keep **game canon** in `GAME.md`, `docs/GDD.md`, `docs/design/LOOPS.md`, `docs/MVP_DONE.md`, `docs/DONE.md` — never in `memory/`. See `templates/project/AGENTS.md`.

## Agent memory

Cross-session knowledge for **this factory repo** lives in git-tracked memory files, not in chat context.

**Read order:** `MEMORY.md` → `memory/hot-cache.md` → as needed `memory/warm-cache.md`, `memory/open-loops.md`, `memory/decisions.md` → `memory/wiki/`.

**Write path:** end-of-session consolidation uses the **memo-session-skill** (wrap up / handoff / save what we learned). It routes durable facts into `MEMORY.md` and `memory/` layers; it does **not** replace `CHANGELOG.md` or git history.

### memo-session-skill — install check

Before relying on wrap-up or `/inbox`, verify the skill is installed **globally** on the host:

| Path | Meaning |
|------|---------|
| `%USERPROFILE%\.cursor\skills\memo-session-skill\SKILL.md` | Cursor global skill |
| `%USERPROFILE%\.agents\skills\memo-session-skill\SKILL.md` | Agents global skill |

If **neither** file exists, tell the user the skill is missing and how to install it:

```bash
npx skills add shenwell/ai-agent-skills --skill memo-session-skill -g -a cursor -y
```

Public source: [memo-session-skill on GitHub](https://github.com/shenwell/ai-agent-skills/tree/main/skills/memo-session-skill) · collection [ai-agent-skills](https://github.com/shenwell/ai-agent-skills).

Do **not** copy `memo-session-skill` into this repo; invoke the global skill only.

**Inbox:** drop files in `memory/inbox/`, then run `/inbox` or “process inbox”.

Portfolio memory (`GLOBAL_MEMORY_ROOT`) is **not** configured for this repo.

## Installed game projects (out of scope here)

Games created by init use `templates/project/AGENTS.md`, `game-factory.config.yaml`, and `.game-factory/state.json`. Develop those in the game repo, not in ai-game-factory.
