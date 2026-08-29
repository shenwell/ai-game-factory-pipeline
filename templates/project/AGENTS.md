# Build Godot game via game-factory

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
