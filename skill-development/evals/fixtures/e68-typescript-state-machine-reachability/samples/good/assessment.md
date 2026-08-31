# Assessment

## Verdict

The “20,000 transitions” claim is unsupported. `maxCommands` is an upper bound
on generated sequence length, not a count of executed state changes.
`fc.commands` draws command instances (including UUID targets) independently;
during `asyncModelRun`, each command's `check` is its precondition and commands
whose check is false are skipped. Here the checks are coarse, then target
admissibility is hidden inside `run` as an early return. A command can pass
`check`, execute `run`, and still be a silent no-op. The seven deletes are the
relevant evidence, not 200 × 100.

## Changes

Move the exact target-specific precondition into `check`:

- `SelectUser.check` should be `m.users.has(this.id)`.
- `DeleteSelected.check` should require both `m.selected !== null` and
  `this.id === m.selected` (and, defensively, that the set has the id).

Once `check` returns true, `run` should perform and assert the real transition;
remove the early returns. If a no-op is intentional product behavior, represent
it as its own admissible command and assert that state remains unchanged.
Consider generating target-aware commands from a small id domain so creates,
selects, and deletes can form useful histories; `check` remains the source of
truth and command-aware shrinking remains available.

Instrument generated, check-accepted, real-call, and postcondition-success
counts per command. Fail a fixed-seed PR smoke run if critical commands have no
accepted/effective transitions. Report distributions rather than multiplying
`numRuns` by `maxCommands`.

For replay, read `FC_SEED` and `FC_PATH` and pass `{ seed, path }` to
`fc.assert`. Commands need one more artifact: read `FC_REPLAY_PATH` and pass it
as `{ replayPath }` to `fc.commands`. Preserve all three values from the
failure. Inject/forward them explicitly to each Vitest project and worker so
API and browser projects replay the same case. Use a fixed PR/CI seed for a
stable smoke test and a rotating seed in scheduled discovery runs. A failure is
not closed until its exact seed/path/replayPath replays and the minimized case
becomes a named regression where appropriate.
Do not leave target admissibility in `run`, raise `maxCommands` as a substitute
for measured transitions, omit any replay artifact, or rely on implicit worker
inheritance.
