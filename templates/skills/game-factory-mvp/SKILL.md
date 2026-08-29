---
name: game-factory-mvp
description: Resume-aware MVP pipeline — design bundle, human design gate, Godot scaffold, verify, playtest gate. Reads game-factory.config.yaml and .game-factory/state.json.
---

# game-factory-mvp

1. Read `game-factory.config.yaml`, `.game-factory/state.json`, `AGENTS.md`.
2. Phase `bootstrap` → `game-factory onboard` (fix blockers); then `game-factory transition --to design`.
3. Phase `design` → draft `GAME.md`, `docs/GDD.md`, `docs/design/LOOPS.md`, `docs/MVP_DONE.md` using skill `game-design`.
4. `game-factory transition --to awaitingDesignApproval` — **stop for human approval** (asset plan + design).
5. After approval → `mvpBuild`: scaffold Godot per `godot.md`; core+session loops only.
6. `game-factory transition --to mvpVerify`; run `game-factory verify fast` then `game-factory verify visual`.
7. `game-factory transition --to awaitingPlaytest` — **stop for human playtest** (`docs/PLAYTEST.md`).

Do not start production until playtest `PASS`.
