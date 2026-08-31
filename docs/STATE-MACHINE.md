# State machine

Phases: `bootstrap` (run `game-factory onboard`) → `design` → `awaitingDesignApproval` → `mvpBuild` → `mvpVerify` → `awaitingPlaytest` → `production` → `releaseCandidate` → `done`.

Human gates: `awaitingDesignApproval`, `awaitingPlaytest`.

**UI:** `docs/design/UI.md` is drafted at `design` and approved at `awaitingDesignApproval`. MVP builds the core loop only (`ui.shell: deferred_mvp`); title/pause/settings ship in `production` through `docs/DONE.md`.

Transitions: `factory transition --to <phase> --reason "..."`

Illegal transitions raise `ValueError`.
