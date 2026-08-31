# UI & screens (project contract)

Owner for screens, HUD, popups, and navigation. Theory: `.agents/skills/game-design/references/interface/`. Implementation skills: `game-ui-ux`, `godot-ui-control`, `input-systems`. Pipeline skill: `game-factory-ui`.

Do not duplicate this inventory in `GDD.md` or `memory/` — link here.

## Scope split

| Phase | UI obligation |
|-------|----------------|
| **MVP / playtest** | Core loop only — game may boot straight into gameplay. No title, pause, or settings menu required. |
| **Production → v1** | Full shell per **Screen inventory** below and **v1 checklist** in `docs/DONE.md`. |

Policy flag: `game-factory.config.yaml` → `ui.shell: deferred_mvp` (default for factory template).

## Deferred waiver (MVP)

MVP playtest evaluates **core loop only** (see `docs/PLAYTEST.md`). Lifecycle UI is intentionally deferred until production.

- [ ] Human approved at `awaitingDesignApproval` with this section reviewed
- [ ] No title/pause/settings scenes added during `mvpBuild` unless this file is updated first

## Screen inventory

Mark each row: **MVP** (in MVP build), **v1** (required for release), or **N/A** (+ reason).

Required states adapted from [threejs-game-ui-designer ui-patterns](https://github.com/majidmanzarpour/threejs-game-skills/blob/main/skills/threejs-game-ui-designer/references/ui-patterns.md) (MIT).

| Screen / state | MVP | v1 | Notes |
|----------------|-----|-----|-------|
| Gameplay HUD | | | Moment-layer feedback from `docs/design/LOOPS.md` |
| Title / main menu | defer | | Play, settings entry |
| Pause / resume | defer | | Resume primary; settings secondary |
| Settings (audio, accessibility) | defer | | At least volume + text size if applicable |
| Fail / retry | defer | | Or N/A if no fail state in v1 scope |
| Win / milestone | defer | | Or N/A |
| Loading / error | defer | | Required if async asset load |
| Modal / popup (shared) | defer | | One pattern for inform + confirm |
| Touch controls | defer | | N/A unless mobile target |
| Debug / tuning UI | N/A | N/A | Dev-only, never player-facing |

## Navigation stack

Use a **screen stack** (push/pop), not boolean flags (`isPaused`, `inSettings`, …).

```text
title → game → pause → settings
              └→ modal (confirm / inform)
```

- Top screen owns input and visibility.
- Back pops one level; pause overlays game without destroying it.
- See `game-ui-ux` → `references/layout-and-flow.md` for focus trap on modals.

## Popup contract

One modal shell for the whole game:

| Kind | Use | Primary action | Secondary |
|------|-----|----------------|-----------|
| **inform** | FYI, no choice | OK / Continue | — |
| **confirm** | Irreversible or high stakes | Destructive or commit | Cancel |
| **blocking** | Must resolve before play | Per context | — |

Rules:

- Primary action first (resume, retry, continue).
- Trap focus inside modal; restore focus on close.
- Do not add a second popup style without updating this section.

## HUD contract

- Elements driven by **signals/events**, not per-frame polling of gameplay internals.
- Show only what the moment loop needs (see `docs/design/LOOPS.md`).
- Anchor to corners; scale with `project.logical_resolution` and stretch settings in `godot.md`.

## Input & focus

- Support keyboard + gamepad on every **v1** menu screen.
- Set initial focus when a screen opens; define focus neighbors.
- Respect safe area / display insets on notched or TV targets.

## Accessibility floor

- Text size option or scalable UI; no tiny fixed fonts.
- Do not encode state by color alone — add icon, shape, or text.
- See `.agents/skills/game-design/references/interface/accessibility.md`.

## v1 evidence

When shell is complete, capture under `screenshots/`:

- `ui-title.png`, `ui-hud.png`, `ui-pause.png`, `ui-modal.png` (as applicable per inventory)
- `game-factory verify visual`

---

Attribution: required-states list adapted from [majidmanzarpour/threejs-game-skills](https://github.com/majidmanzarpour/threejs-game-skills) (MIT).
