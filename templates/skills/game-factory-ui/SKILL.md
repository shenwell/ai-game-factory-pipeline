---
name: game-factory-ui
description: Route UI work through docs/design/UI.md — inventory at design, Godot shell at production. Loads vendored game-ui-ux, godot-ui-control, input-systems, and game-design interface theory.
---

# game-factory-ui

Owner file: **`docs/design/UI.md`**. Edit it when screen scope changes; never invent a parallel UI spec in `memory/` or chat.

## When to use

| Phase | Action |
|-------|--------|
| `design` | Draft or update screen inventory, navigation stack, popup contract, MVP defer waiver |
| `awaitingDesignApproval` | Human reviews UI.md with GDD and LOOPS |
| `production` | Implement v1 shell per UI.md + `docs/DONE.md` UI checklist |
| Pre-release | UI evidence pass (`screenshots/ui-*.png`) |

## Skills to load (in order)

1. **`game-design`** — command `interface` for lifecycle theory (title, pause, HUD, accessibility). Do not copy long theory into UI.md.
2. **`game-ui-ux`** — engine-neutral: screen stack, safe area, focus, event-driven HUD.
3. **`godot-ui-control`** — Godot 4.7 Control nodes, Theme, containers, focus neighbors.
4. **`input-systems`** — when settings/rebind screen is in v1 inventory.

## Rules

- **MVP:** loop only unless UI.md explicitly marks a screen for MVP. Default factory policy: `ui.shell: deferred_mvp`.
- **One popup pattern** — inform / confirm / blocking per UI.md; no ad-hoc `AcceptDialog` styling per screen.
- **UI does not own game state** — display via signals; player actions emit events.
- **Paths** — follow `godot.md` UI conventions (`scenes/ui/`, `ui/theme/game.tres`, `scripts/ui/`).
- **Production QA** — follow `.game-factory/vendor/gamestudio/roles/ui-developer.md` (focus, EN string fit, touch targets if applicable).

## Design phase checklist

- [ ] Screen inventory table filled (MVP / v1 / N/A)
- [ ] Deferred waiver checked for design gate
- [ ] HUD elements tied to `docs/design/LOOPS.md` moment layer
- [ ] v1 rows match what `docs/DONE.md` will verify

## Production phase checklist

- [ ] Screen stack implemented (push/pop)
- [ ] All v1 inventory rows implemented or N/A documented
- [ ] Modal uses shared shell + focus trap
- [ ] Gamepad navigable on every menu screen
- [ ] Screenshots captured per UI.md evidence section

Do not copy another project’s UI unless the user names the source and what to take.
