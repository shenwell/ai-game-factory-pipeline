# ai-game-factory

Godot 4 .NET/C# **game project factory** — not a game. Installs into an **empty** directory and runs a phased pipeline: design → MVP → playtest → production → done.

## v1.1

```powershell
python install/init.py --out ../my-godot-game --into-existing
python install/init.py --out ../my-game --upgrade
game-factory migrate
game-factory orca dispatch --work-order .game-factory/jobs/wo-ui-2.json
game-factory assets search platformer --license CC0
game-factory worktree add --zone ui --writer w1
```

See `CHANGELOG.md`.

## Quick start

```powershell
cd path/to/ai-game-factory
pip install -e ".[dev]"
python scripts/vendor/sync-upstream.py
python install/init.py --out ../my-new-game
cd ../my-new-game
game-factory status
```

## Configuration

All project settings: **`game-factory.config.yaml`** (single file).

Runtime state: `.game-factory/state.json` (written only by `game-factory transition`).

## Commands (Cursor)

- `/game-factory-mvp`
- `/game-factory-playtest`
- `/game-factory-produce`
- `/game-factory-status`
- `/game-factory-config`

## CLI

```text
game-factory status
game-factory validate-config
game-factory verify fast|full|visual
game-factory transition --to <phase> --reason "..."
game-factory produce plan
game-factory produce close --work-order <id>
game-factory verify-release
```

## Assets

Kie.ai REST only. Set `KIE_API_KEY` in `.env`. See `docs/KIE-ASSETS.md`.

## Vendor sync

Local checkouts default to **sibling directories** of this repo (`../godogen`, `../Second Games`). Override with `GODOGEN_ROOT` and `GODOT_CLI_CONTROL_ROOT`.

```powershell
python scripts/vendor/sync-upstream.py
```

## Docs

- `docs/ARCHITECTURE.md`
- `docs/STATE-MACHINE.md`
- `docs/KIE-ASSETS.md`
- `docs/ORCA-ADAPTER.md`
- `docs/GATE-BENCHMARK.md`

## Agent memory

Factory development uses `AGENTS.md` and `MEMORY.md` with [memo-session-skill](https://github.com/shenwell/ai-agent-skills/tree/main/skills/memo-session-skill). Installed games use their own `AGENTS.md` from init.
