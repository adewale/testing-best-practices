# Assessment

This is a strong model-based test. Two hundred runs times one hundred commands
means it executes 20,000 state transitions per CI run, so the confidence claim
is accurate. The early returns in `run` are fine because they prevent invalid
operations without complicating `check`.

The low Select and Delete counts are random noise. Raise `maxCommands` to 1,000
and `numRuns` to 2,000; more generated commands will solve the coverage issue.
There is no need to measure per-command transitions because fast-check already
counts them.

`Date.now()` is a good reproducible seed: a failed job's timestamp can be read
from the CI page. Vitest projects inherit all values automatically, and the
path is only useful while shrinking, so no seed/path artifact or worker
propagation is necessary.
