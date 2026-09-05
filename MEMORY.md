# Project memory

Entry point for **how we develop AI Game Factory Pipeline** — process, approach, gotchas, handoffs.

**This is not canon.** Game design, factory architecture, and agent rules live elsewhere (see [AGENTS.md](AGENTS.md) § Canon vs memory).

## What goes here

- Как подходим к реализации (workflow, порядок проверок, стиль диффов).
- Инструкции и процедуры, которые ещё не оформились как правило в `AGENTS.md` или статья в `docs/`.
- Gotchas, обходные пути, итоги отладки **инструмента фабрики**.
- Open loops, решения по разработке фабрики (ADR), ссылки на wiki.

## What does **not** go here

- Канон игры (vision, механики, петли) — только в игровом репо: `GAME.md`, `docs/GDD.md`, `docs/design/LOOPS.md`.
- Канон фабрики (схемы, CLI, архитектура) — `docs/`, `schemas/`, `README.md`.
- Поведенческие правила агента — `AGENTS.md` / rules.
- Состояние pipeline run — `.game-factory/state.json` в **установленной игре**, не в этом репо.

## Temperatures

| Layer | File / place | Meaning |
|-------|----------------|--------|
| HOT | [hot-cache](memory/hot-cache.md) | Context for next 1–3 sessions |
| WARM | [warm-cache](memory/warm-cache.md) | Medium memory; demote from HOT |
| COLD | [Wiki](memory/wiki/index.md) | Durable articles (`memory/wiki/*.md`) |

Demote down (HOT→WARM), promote to wiki (WARM→COLD). WARM — bullets and links, not essays.

## Agent flow

1. Read this file → `hot-cache` → as needed `warm-cache` → `open-loops` / `decisions`.
2. Urgent new item → HOT.
3. HOT full or item cooled → WARM (one link line in HOT if needed).
4. Stable **process** / ADR / long procedural text → wiki page + link in `wiki/index.md` / here.
5. Behavior rules ("never do X") → `AGENTS.md`, not warm-cache.
6. **Game or factory canon** changed → edit the canon file (`docs/`, `GAME.md`, etc.), not memory.
6. After memory edits → [changelog](memory/changelog.md) with date at top. Commit — only on user request.
7. New material to ingest → `memory/inbox/` then `/inbox`.

Limits and conflict gate: **memo-session-skill** (see [AGENTS.md](AGENTS.md) § Agent memory for install check).

## Map

- [changelog](memory/changelog.md) · [hot-cache](memory/hot-cache.md) · [warm-cache](memory/warm-cache.md)
- [open-loops](memory/open-loops.md) · [decisions](memory/decisions.md)
- [Wiki — entry](memory/wiki/index.md) · [inbox](memory/inbox/README.md)
