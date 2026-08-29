---
name: game-factory-playtest
description: Prepare playtest evidence and record human verdict in PLAYTEST.md.
---

# game-factory-playtest

1. Ensure `game-factory verify visual` evidence exists.
2. Fill `docs/PLAYTEST.md` template for the user.
3. After user verdict: `PASS` → scope lock + full `docs/DONE.md`; `game-factory transition --to production`.
4. `ITERATE_MVP` → `game-factory transition --to mvpBuild`.
