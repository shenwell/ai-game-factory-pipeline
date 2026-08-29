# Orca adapter (v1.1)

v1 uses Cursor + `orchestration.adapter: cursor` in config.

Orca will implement the same contract as `src/game_factory/adapters/orca/dispatch.md`:

- `dispatch(work_order.json)`
- `status(job_id)`
- `collect(job_id)`
- `cancel(job_id)`

Config, state, and work-order schemas are unchanged.
