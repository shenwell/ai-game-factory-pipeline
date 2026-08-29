# Orca dispatch contract

Input: path to `work-order.schema.json` compliant JSON.

## Operations

| Operation | CLI | Output |
|-----------|-----|--------|
| dispatch | `game-factory orca dispatch --work-order <path>` | `{ job_id, status, orca_task_id? }` |
| status | `game-factory orca status --job-id <id>` | `{ job_id, status }` |
| collect | `game-factory orca collect --job-id <id>` | `{ job_id, status, result? }` |
| cancel | `game-factory orca cancel --job-id <id>` | `{ job_id, status: cancelled }` |

Jobs persist under `.game-factory/jobs/orca/<job_id>.json`.

When `orca` CLI is unavailable, `queued_local` mode completes on `collect` without external orchestration.
