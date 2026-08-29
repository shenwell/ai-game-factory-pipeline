# ai-game-factory

Godot 4 .NET/C# **game project factory** — not a game. Installs into an **empty** directory and runs a phased pipeline: design → MVP → playtest → production → done.

## Quick start

```powershell
cd "D:\GAMES Creator\ai-game-factory"
pip install -e ".[dev]"
python scripts/vendor/sync-upstream.py
python install/init.py --out "D:\Games\my-new-game"
cd "D:\Games\my-new-game"
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

```powershell
python scripts/vendor/sync-upstream.py
```

## Docs

- `docs/ARCHITECTURE.md`
- `docs/STATE-MACHINE.md`
- `docs/KIE-ASSETS.md`
- `docs/ORCA-ADAPTER.md`
- `docs/GATE-BENCHMARK.md`
