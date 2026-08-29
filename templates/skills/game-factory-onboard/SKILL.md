---
name: game-factory-onboard
description: Post-install onboarding — verify files, toolchain, and next steps before /game-factory-mvp.
---

# game-factory-onboard

1. Run `game-factory onboard` from the **game** project root (not the factory repo).
2. Summarize `ready`, blockers, and warnings in plain language.
3. If `ready` is false, fix blockers with the user (missing files, Python/Godot/.NET versions) before starting design.
4. If only warnings (empty `project.name`, no `KIE_API_KEY`), explain them and proceed only if the user agrees.
5. Point at `docs/ONBOARDING.md`. Next command when ready: `/game-factory-mvp`.
