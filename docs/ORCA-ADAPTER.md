# Orca adapter (v1.1)

Host-neutral contract implemented in `src/game_factory/adapters/orca/client.py`.

## CLI

```text
game-factory orca dispatch --work-order .game-factory/jobs/wo-ui-2.json
game-factory orca status --job-id orca-abc123
game-factory orca collect --job-id orca-abc123
game-factory orca cancel --job-id orca-abc123
```

Set `orchestration.adapter: orca` and `orchestration.orca_project_id` in `game-factory.config.yaml`.

When the `orca` CLI is on PATH, `dispatch` calls `orca orchestration task-create`; otherwise jobs stay in `queued_local` mode under `.game-factory/jobs/orca/`.

Config, state, and work-order schemas are unchanged.
