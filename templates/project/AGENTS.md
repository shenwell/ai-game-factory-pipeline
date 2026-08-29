# Build Godot game via game-factory

## Canon (source of truth — not `memory/`)

| Topic | Owner file |
|-------|------------|
| Vision, scope, pillars | `GAME.md` |
| Mechanics, systems | `docs/GDD.md` |
| Loop numbers, project-specific loops | `docs/design/LOOPS.md` |
| MVP / v1 acceptance | `docs/MVP_DONE.md`, `docs/DONE.md` |
| User settings, gates, assets policy | `game-factory.config.yaml` |
| Pipeline phase (machine) | `.game-factory/state.json` |
| Agent behavior & toolchain | **`AGENTS.md`**, `godot.md`, skills |

When game facts change, **edit the owner file**. Do not park design canon in `MEMORY.md` or `memory/`.

## Memory (how we work — not game design)

`MEMORY.md` and `memory/` hold **process**: how we implement, gotchas, open loops, session handoff, debugging notes. Use **memo-session-skill** at wrap-up.

| In memory | Not in memory |
|-----------|----------------|
| «Как в этом проекте дебажим Godot на Windows» | Описание core loop → `LOOPS.md` |
| Открытый баг-обход до фикса | Баланс, числа урона → `GDD.md` |
| Договорённости по workflow в сессии | Pillars и anti-goals → `GAME.md` |

If a rule becomes permanent → move to `AGENTS.md` or the right doc in `docs/`, then drop the duplicate from hot-cache.

### memo-session-skill

Before wrap-up or `/inbox`, check global install:

- `%USERPROFILE%\.cursor\skills\memo-session-skill\SKILL.md`
- `%USERPROFILE%\.agents\skills\memo-session-skill\SKILL.md`

If missing, install:

```bash
npx skills add shenwell/ai-agent-skills --skill memo-session-skill -g -a cursor -y
```

Public: [memo-session-skill](https://github.com/shenwell/ai-agent-skills/tree/main/skills/memo-session-skill).

Read order: `MEMORY.md` → `memory/hot-cache.md` → as needed warm / open-loops / decisions → `memory/wiki/`.

## Runtime

- **Settings:** read `game-factory.config.yaml` only — do not duplicate numbers elsewhere.
- **State:** read `.game-factory/state.json` before each `/game-factory-*` command; resume, do not restart phases.
- **Design loops:** use `.agents/skills/game-design/` for theory; project numbers live in `docs/design/LOOPS.md`.
- **Studio rules:** `.game-factory/vendor/gamestudio/STUDIO.md` during production phase.
- **Engine:** read `godot.md` for Godot 4 .NET / C# traps and capture.
- **Assets:** Kie.ai REST only — skill `asset-gen`; key `KIE_API_KEY` in `.env`. No mcp-kv.
- **Proof:** judge from running game via `godot-cli-control` GUI screenshots, not headless alone.

## Delivery

Two human gates per run: design approval (`awaitingDesignApproval`) and playtest (`awaitingPlaytest`). Finish with evidence in `docs/DONE.md` and `game-factory verify visual`.

## CLI

From project root (with venv or `pip install -e` on ai-game-factory):

```text
game-factory status
game-factory validate-config
game-factory verify fast|full|visual
game-factory transition --to <phase> --reason "..."
```
