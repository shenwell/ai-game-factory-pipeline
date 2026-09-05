# AI Game Factory Pipeline

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Godot 4.7 .NET](https://img.shields.io/badge/Godot-4.7%20.NET-informational)](https://godotengine.org/)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-black)](https://agentskills.io/)

**Agent-driven pipeline that scaffolds a Godot 4 .NET/C# game project and walks it from design to v1** — not a game itself.

Repository: [`shenwell/ai-game-factory-pipeline`](https://github.com/shenwell/ai-game-factory-pipeline) · CLI entry point: `game-factory` · Current version: **1.1.3**

You install the factory into an **empty directory** (or overlay an existing Godot repo). Cursor slash commands and skills drive each phase. Two **human gates** stop the agent before MVP code and before production. Kie.ai generates images and video; `gamestudio` rules govern studio-style production batches.

```
  YOU + CURSOR                    PIPELINE                         SHIPPED GAME
     │                               │                                  │
     │  /game-factory-mvp            │  design → MVP loop → playtest    │
     ├──────────────────────────────►│  → production → UI shell → v1  │
     │                               ├─────────────────────────────────►│
     │                               │     Godot project + docs canon   │
```

---

## What you get

| Layer | What it is |
|-------|------------|
| **Python CLI** | `game-factory` — state machine, gates, config validation, production batching, Kie client |
| **Init** | `install/init.py` — copies templates, vendor skills, gamestudio, godot-cli-control addon |
| **Cursor commands** | `/game-factory-onboard`, `-mvp`, `-playtest`, `-produce`, `-ui`, `-status`, `-config` |
| **Agent skills** | MVP / produce / playtest / UI orchestration + vendored `game-design`, UI, assets, godot-cli-control |
| **Game canon** | `GAME.md`, `GDD.md`, `LOOPS.md`, **`UI.md`**, `MVP_DONE.md`, `DONE.md` in the **game** repo |
| **Machine state** | `.game-factory/state.json` — phase only; resume, never restart from scratch |

Stops the common failure mode: the agent improvises menus, skips design approval, and ships a loop with no path to v1.

---

## Pipeline phases

```text
bootstrap → design → awaitingDesignApproval → mvpBuild → mvpVerify
  → awaitingPlaytest → production → releaseCandidate → done
```

| Phase | Agent does | Human |
|-------|------------|-------|
| `bootstrap` | `game-factory onboard` — files, Python, Godot, .NET checks | Fix blockers |
| `design` | `GAME.md`, `GDD.md`, `LOOPS.md`, **`UI.md`**, `MVP_DONE.md` | — |
| `awaitingDesignApproval` | — | Approve design + UI inventory + asset plan |
| `mvpBuild` | Godot scaffold, **core + session loop only** (no title/pause by default) | — |
| `mvpVerify` | `game-factory verify fast` + `visual` | — |
| `awaitingPlaytest` | `PLAYTEST.md` evidence | Playtest loop; PASS / ITERATE |
| `production` | Studio batches (`STUDIO.md`), **full UI shell** per `UI.md` | Playtest whole game |
| `releaseCandidate` / `done` | `verify full`, `verify-release`, `DONE.md` green | Ship |

**UI policy (`ui.shell: deferred_mvp`):** MVP playtest judges the **loop only**. Title, pause, settings, and popups are specified at design gate in `docs/design/UI.md` and built in **production**.

Details: [`docs/STATE-MACHINE.md`](docs/STATE-MACHINE.md)

---

## Who this is for

- Teams building **Godot 4.7.x .NET / C#** games with **Cursor** (or any agent that reads Agent Skills)
- Developers who want **phased delivery**: design sign-off → playable MVP → human playtest → production → v1 checklist
- Anyone who needs a **repeatable** scaffold (config, gates, skills, studio rules) instead of one-off agent prompts

## Who this is not for

- No-code users (requires Godot, .NET SDK 9, Python 3.11+, and an coding agent)
- Non-Godot engines (templates and `godot.md` are Godot-specific)
- Fully automated “make a game with zero human input” (design and playtest gates are intentional)

---

## Prerequisites

| Tool | Version | Role |
|------|---------|------|
| Python | 3.11+ | CLI and init |
| Godot | 4.7.x **.NET** build | Run and export the game |
| .NET SDK | 9.x | `dotnet build` gate |
| Cursor (recommended) | recent | Slash commands and skills |
| Kie.ai API key | optional | Image/video generation; procedural fallback without it |

---

## Quick start

### 1. Clone and install the factory CLI

```powershell
git clone https://github.com/shenwell/ai-game-factory-pipeline.git
cd ai-game-factory-pipeline
pip install -e ".[dev]"
```

Maintainers updating vendored skills (optional):

```powershell
python scripts/vendor/sync-upstream.py
```

Requires sibling checkouts or `GODOGEN_ROOT` / `GODOT_CLI_CONTROL_ROOT` for local upstreams. **Fresh clones already include committed `vendor/`** — sync is not required to init a game.

### 2. Create a new game project

```powershell
python install/init.py --out ../my-new-game
cd ../my-new-game
game-factory onboard
```

### 3. Run the pipeline in Cursor

```text
/game-factory-onboard
/game-factory-mvp
```

The agent reads `.game-factory/state.json` and **resumes** the current phase.

### Other init modes

```powershell
# Overlay onto existing Godot project (must have project.godot)
python install/init.py --out ../existing-godot-game --into-existing

# Upgrade factory files in an installed game
python install/init.py --out ../my-game --upgrade
game-factory migrate
```

---

## Cursor commands (installed into each game)

| Command | Skill | Purpose |
|---------|-------|---------|
| `/game-factory-onboard` | `game-factory-onboard` | Post-install checks and next steps |
| `/game-factory-mvp` | `game-factory-mvp` | Design → gates → MVP build → verify → playtest stop |
| `/game-factory-playtest` | `game-factory-playtest` | Record playtest verdict in `PLAYTEST.md` |
| `/game-factory-produce` | `game-factory-produce` | Studio production loop after playtest PASS |
| `/game-factory-ui` | `game-factory-ui` | UI inventory (design) or shell implementation (production) |
| `/game-factory-status` | `game-factory-status` | Phase and blockers |
| `/game-factory-config` | `game-factory-config` | Validate `game-factory.config.yaml` |

---

## Skills shipped into each game

Copied to `.agents/skills/` and `.cursor/skills/` on init:

| Skill | Role |
|-------|------|
| `game-factory-mvp` | Resume-aware MVP pipeline |
| `game-factory-produce` | Production batches per `STUDIO.md` |
| `game-factory-playtest` | Playtest gate |
| `game-factory-ui` | Routes UI work through `docs/design/UI.md` |
| `game-factory-onboard` / `-status` / `-config` | Tooling |
| `game-design` | Mechanics, loops, interface theory (vendored) |
| `game-ui-ux`, `godot-ui-control`, `input-systems` | UI architecture and Godot widgets (vendored, Apache-2.0) |
| `asset-gen` | Kie.ai images/video (Kie-only patch) |
| `godot-cli-control` | GUI screenshots and proof capture |

Game design canon lives in the **game repo** (`GAME.md`, `docs/`, `UI.md`). Factory development memory lives only in **this** repo (`MEMORY.md`).

---

## CLI reference

```text
game-factory onboard              # verify game project ready
game-factory status               # phase + config
game-factory validate-config
game-factory verify fast|full|visual
game-factory transition --to <phase> --reason "..."
game-factory produce plan
game-factory produce close --work-order <id>
game-factory produce status
game-factory verify-release
game-factory migrate
game-factory assets search <query> --license CC0
game-factory worktree add --zone <zone> --writer <id>
game-factory worktree remove --zone <zone>
game-factory orca dispatch|status|collect|cancel   # optional Orca adapter
```

### Verification gates

| Profile | Typical steps |
|---------|----------------|
| `fast` | config, drift, build, unit |
| `full` | fast + scene import, launch, gameplay, glb_import, **ui_contract** |
| `visual` | full + screenshots + proof video |

`ui_contract` checks that `docs/design/UI.md` exists with screen inventory and MVP defer policy — not that UI scenes are built yet.

Configure profiles in `game-factory.config.yaml`. Benchmark: [`docs/GATE-BENCHMARK.md`](docs/GATE-BENCHMARK.md)

---

## Configuration

Single file in each **game** project: **`game-factory.config.yaml`**

- `project` — name, display name, 2d/3d, logical resolution
- `gates` — fast / full / visual step lists
- `ui.shell` — `deferred_mvp` (default): menus ship in production, not MVP
- `assets` — Kie.ai models, approval at design gate, optional Kenney catalog
- `production` — batch weights, worktree dir for parallel writers

Runtime phase: **`.game-factory/state.json`** (only `game-factory transition` writes it).

---

## Assets (Kie.ai)

Images and video via REST only. Set `KIE_API_KEY` in the game’s `.env` (see `.env.example`).

Design can start without a key (procedural fallback). See [`docs/KIE-ASSETS.md`](docs/KIE-ASSETS.md).

---

## Production and studio

After playtest `PASS`, `production` uses vendored **gamestudio** (`STUDIO.md`, role files, `ui-diff-check.sh`). Work orders come from `tasks/open/`. Optional:

- **Zone worktrees** — `game-factory worktree add` for parallel writers
- **Orca adapter** — dispatch/status for external orchestration ([`docs/ORCA-ADAPTER.md`](docs/ORCA-ADAPTER.md))
- **Open-source catalog** — `game-factory assets search`

---

## Repository layout

```text
src/game_factory/          # CLI, gates, state machine, Kie, production
install/init.py            # fresh | --into-existing | --upgrade
templates/project/         # copied into each new game
templates/skills/          # factory-owned Agent Skills
vendor/                    # game-design, gamestudio, UI skills, godot_cli_control, …
schemas/                   # JSON Schema for config, state, gates
docs/                      # architecture, state machine, adapters
tests/                     # contract + dogfood
```

Architecture: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

---

## Related projects

- [ai-agent-skills](https://github.com/shenwell/ai-agent-skills) — public Agent Skills collection (`memo-session-skill`, `goal-mode`, `software-factory`)
- [awesome-gamedev-agent-skills](https://github.com/gamedev-skills/awesome-gamedev-agent-skills) — source of vendored `game-ui-ux` / `godot-ui-control` / `input-systems`

---

## Development (this repo)

```powershell
pip install -e ".[dev]"
pytest tests/
```

Agent guide: [`AGENTS.md`](AGENTS.md). Factory process memory: [`MEMORY.md`](MEMORY.md) (not copied into games).

---

## License

MIT — [LICENSE](LICENSE). Vendored components: [THIRD_PARTY.md](THIRD_PARTY.md), [vendor/NOTICE](vendor/NOTICE).
