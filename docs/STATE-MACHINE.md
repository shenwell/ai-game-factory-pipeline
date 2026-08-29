# State machine

Phases: `bootstrap` (run `game-factory onboard`) → `design` → `awaitingDesignApproval` → `mvpBuild` → `mvpVerify` → `awaitingPlaytest` → `production` → `releaseCandidate` → `done`.

Human gates: `awaitingDesignApproval`, `awaitingPlaytest`.

Transitions: `factory transition --to <phase> --reason "..."`

Illegal transitions raise `ValueError`.
