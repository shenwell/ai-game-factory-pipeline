# Changelog

## Unreleased

- Agent rule: do not copy another project’s implementation unless the user names the source and what to take (`AGENTS.md`, installed-game template).

## 1.1.3

- UI pipeline: `docs/design/UI.md` owner contract, MVP defer / v1 shell checklist in `MVP_DONE.md` and `DONE.md`.
- Skills: `game-factory-ui` plus vendored `game-ui-ux`, `godot-ui-control`, `input-systems` (Apache-2.0, sync via `scripts/vendor/sync-upstream.py`).
- Gate `ui_contract` on `verify full` / `visual`; config `ui.shell: deferred_mvp`.
- Migration `1.1.x` → `1.1.3` copies UI docs and command on `init --upgrade`.

## 1.1.2

- After init, run onboarding checks (`game-factory onboard`): required files, config, Python, Godot/.NET, `KIE_API_KEY`. Init JSON includes `onboard`; humans read `docs/ONBOARDING.md`.

## 1.1.1

- Paths in docs, vendor sync, gate evidence, and CLI output are project-relative. Local vendor sources default to sibling directories (`../godogen`, `../Second Games`) or `GODOGEN_ROOT` / `GODOT_CLI_CONTROL_ROOT`.

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
