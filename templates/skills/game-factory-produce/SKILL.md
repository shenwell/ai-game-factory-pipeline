---
name: game-factory-produce
description: Studio production loop — batches from tasks/open per STUDIO.md. One writer v1. Uses game-factory CLI and vendor gamestudio rules.
---

# game-factory-produce

1. Read `.game-factory/state.json` — must be `production` or use `game-factory transition --to production` after playtest PASS.
2. Read `.game-factory/vendor/gamestudio/STUDIO.md`, `roles/_common.md`, and **`docs/design/UI.md`** (v1 shell contract).
3. Before the first UI batch: invoke skill `game-factory-ui` (loads `game-ui-ux`, `godot-ui-control`, `input-systems`). One Theme, one modal pattern — no second popup style.
4. `game-factory produce plan` — work orders from `tasks/open/` (15–20 weights, one zone per batch).
5. Writer implements batch; `game-factory produce close --work-order <id>` after `game-factory verify fast`.
6. Producer merges; `game-factory verify full`; QA playtests whole game including UI checklist in `docs/DONE.md`.
7. Repeat until `docs/DONE.md` green and no `NN-*`/`bug-*`.
8. `game-factory transition --to releaseCandidate` then verifier → `done`.

Reopen: `bug-*` tasks → `game-factory transition --to production --reason reopen`.

Do not copy another project’s implementation unless the user names the source and what to take.
