---
name: game-factory-mvp
description: Resume-aware MVP pipeline — design bundle, human design gate, Godot scaffold, verify, playtest gate. Reads game-factory.config.yaml and .game-factory/state.json.
---

# game-factory-mvp

1. Read `game-factory.config.yaml`, `.game-factory/state.json`, `AGENTS.md`.
2. Phase `bootstrap` → `game-factory onboard` (fix blockers); then `game-factory transition --to design`.
3. Phase `design` → draft `GAME.md`, `docs/GDD.md`, `docs/design/LOOPS.md`, `docs/design/UI.md`, `docs/MVP_DONE.md` using skill `game-design` (and `game-factory-ui` for UI inventory).
   - Run `game-design` command `interface` for lifecycle screens; put project-specific decisions in `docs/design/UI.md` only.
   - Design gate checklist for human: UI inventory agreed, MVP defer waiver checked, v1 shell rows filled.
4. `game-factory transition --to awaitingDesignApproval` — **stop for human approval** (asset plan + design + UI.md).
5. After approval → `mvpBuild`: scaffold Godot per `godot.md`; **core+session loops only** — no title/pause/settings unless `docs/design/UI.md` was changed to require them on MVP.
6. `game-factory transition --to mvpVerify`; run `game-factory verify fast` then `game-factory verify visual`.
7. `game-factory transition --to awaitingPlaytest` — **stop for human playtest** (`docs/PLAYTEST.md`; loop only, not menus).

Do not start production until playtest `PASS`. Do not copy another project’s implementation unless the user names the source and what to take.
