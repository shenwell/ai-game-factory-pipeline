# Architecture

Portable core: `src/game_factory/` (Python CLI, schemas, gates, Kie client, production batching).

Vendored upstream: `vendor/` — sync via `scripts/vendor/sync-upstream.py`.

Installed project layout: see `templates/project/`. After init, `game-factory onboard` checks files and toolchain.

Adapters:

- `adapters/cursor/` — thin command aliases (installed into `.cursor/commands/`)
- `adapters/orca/` — v1.1 `dispatch/status/collect/cancel` via `game-factory orca`

Host-neutral: no Cursor tool names in `src/game_factory/`.
