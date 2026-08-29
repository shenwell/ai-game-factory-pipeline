# Gate benchmark

Run on your machine after first Godot project exists:

```powershell
factory verify fast
factory verify full
factory verify visual
```

Record `duration_sec` from `.game-factory/jobs/gate-*.json`. Set `gates.wall_seconds_blocker` in `game-factory.config.yaml` when sequential full gate stabilizes.

Run concurrent benchmark only after worktree isolation is enabled (v1.1 parallelism).
