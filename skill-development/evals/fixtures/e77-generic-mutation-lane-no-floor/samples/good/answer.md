I wouldn't add a floor to this lane. Sixteen runs on the same commit gave the same 73.86%:
re-running a mutation score on unchanged code tells you nothing new, and a `break: 70`
could only ever fire on noise (a timeout counted differently, a runner change), not on a
change you made. It isn't a dead gate so much as a diagnostic nobody reads.

What I'd change:

1. Delete the weekly `schedule:` trigger.
2. Run the 12 defect-replay probes on pull requests that touch `src/core/**`, the probes,
   or the test config. They take about 2 minutes and they fail when a shipped bug comes
   back, so they can block a merge.
3. Make the Stryker job `workflow_dispatch` only (or scope it to changed files with
   `--incremental`), and run it when someone has a question about specific tests.
4. Keep `break: null`. If you later run it on changed code in PRs and want a floor, derive
   it from those CI runs, not from a local run or a round number.
