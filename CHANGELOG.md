# Changelog

## 1.1.0

- `install/init.py --upgrade` — migrations from 1.0.0 (config schema v2, ASSETS-3D.md, asset catalog).
- `install/init.py --into-existing` — overlay factory onto existing Godot project (`project.godot` required).
- Orca adapter: `game-factory orca dispatch|status|collect|cancel` (local envelope + optional `orca` CLI).
- Open-source asset catalog search: `game-factory assets search`.
- 3D: `glb_import` gate, `docs/ASSETS-3D.md`, `assets.models_3d` config.
- Production parallelism: zone leases + `game-factory worktree add|remove`.
- Config `schema_version: 2` with `hosts`, `production.worktree_dir`, `assets.opensource`.

## 1.0.0

- Fresh-only init, state machine, Kie-only assets, one-writer production, Cursor skills/commands.
