# State machine

Phases: `bootstrap` → `design` → `awaitingDesignApproval` → `mvpBuild` → `mvpVerify` → `awaitingPlaytest` → `production` → `releaseCandidate` → `done`.

Human gates: `awaitingDesignApproval`, `awaitingPlaytest`.

Transitions: `factory transition --to <phase> --reason "..."`

Illegal transitions raise `ValueError`.
