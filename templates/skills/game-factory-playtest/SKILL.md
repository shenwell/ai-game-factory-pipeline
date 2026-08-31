---
name: game-factory-playtest
description: Prepare playtest evidence and record human verdict in PLAYTEST.md.
---

# game-factory-playtest

1. Ensure `game-factory verify visual` evidence exists (gameplay / loop — not lifecycle UI).
2. Fill `docs/PLAYTEST.md` template for the user. Scope: **core loop only**; UI shell is deferred per `docs/design/UI.md`.
3. After user verdict: `PASS` → scope lock + full `docs/DONE.md`; `game-factory transition --to production`.
4. `ITERATE_MVP` → `game-factory transition --to mvpBuild`.

Do not require title/pause/settings evidence at this gate.
