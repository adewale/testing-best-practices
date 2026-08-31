# Assessment

## Verdict

The cadence is proportional and the target inventory is complete. Keep it.

`go test ./...` replays committed seed-corpus entries as ordinary regression
cases; it does not perform active fuzz discovery. The separate PR matrix does
that active work with `-fuzz`, and its two entries exactly match the discovered
targets `FuzzDecodeFrame` and `FuzzParseHeader`. Each matrix job runs one target
per invocation, which matches the Go engine's operating model and gives each
target its own time and process budget.

The 20-second bounded PR smoke catches harness breakage and cheap discoveries
without turning normal feedback into a campaign. The scheduled matrix then
gives both targets a longer 20-minute discovery budget with a hard timeout and
bounded parallelism. Moving those long runs onto every pull request would add
large, variable latency for little extra gating signal; the short-PR plus
longer-scheduled split is the right cadence.

The failure lifecycle is also sound: upload the minimized failing artifact and
replay command, reproduce it, then promote/commit the input under the matching
`testdata/fuzz/<target>` corpus so `go test ./...` replays the regression on
every future PR. Verify periodically that the `rg '^func Fuzz'` inventory and
both matrices remain identical; that drift check is the only material
automation improvement I would add.

One operational check: ensure artifact upload captures a newly written failure
even when `go test` exits non-zero, and retain the scheduled artifacts long
enough for triage. Neither warrants increasing PR fuzz time.
Do not remove the scheduled fuzz campaign or `go test ./...` seed replay.
