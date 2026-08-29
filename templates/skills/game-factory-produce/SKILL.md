---
name: game-factory-produce
description: Studio production loop — batches from tasks/open per STUDIO.md. One writer v1. Uses game-factory CLI and vendor gamestudio rules.
---

# game-factory-produce

1. Read `.game-factory/state.json` — must be `production` or use `game-factory transition --to production` after playtest PASS.
2. Read `.game-factory/vendor/gamestudio/STUDIO.md` and `roles/_common.md`.
3. `game-factory produce plan` — work orders from `tasks/open/` (15–20 weights, one zone per batch).
4. Writer implements batch; `game-factory produce close --work-order <id>` after `game-factory verify fast`.
5. Producer merges; `game-factory verify full`; QA playtests whole game.
6. Repeat until `docs/DONE.md` green and no `NN-*`/`bug-*`.
7. `game-factory transition --to releaseCandidate` then verifier → `done`.

Reopen: `bug-*` tasks → `game-factory transition --to production --reason reopen`.
