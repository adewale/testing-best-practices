# Audit this Go test setup

Write an `assessment.md` for the following repository evidence. Recommend any
changes that materially improve defect detection or reproducibility.

Fuzz-target inventory produced by `rg '^func Fuzz'`:

```text
wire/frame_fuzz_test.go:func FuzzDecodeFrame(f *testing.F) {
wire/header_fuzz_test.go:func FuzzParseHeader(f *testing.F) {
```

Both targets have reviewed seed files committed under their respective
`wire/testdata/fuzz/<target>/` directories.

`.github/workflows/test.yml`:

```yaml
on: pull_request
jobs:
  regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
      - run: go test ./...

  fuzz-smoke:
    strategy:
      matrix:
        target: [FuzzDecodeFrame, FuzzParseHeader]
    runs-on: ubuntu-latest
    timeout-minutes: 3
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
      - run: go test ./wire -run=^$ -fuzz=^${{ matrix.target }}$ -fuzztime=20s
      - if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: fuzz-${{ matrix.target }}-${{ github.run_id }}
          path: wire/testdata/fuzz/${{ matrix.target }}/
```

`.github/workflows/fuzz-scheduled.yml`:

```yaml
on:
  schedule:
    - cron: '17 2 * * *'
jobs:
  fuzz:
    strategy:
      fail-fast: false
      matrix:
        target: [FuzzDecodeFrame, FuzzParseHeader]
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
      - run: go test ./wire -run=^$ -fuzz=^${{ matrix.target }}$ -fuzztime=20m -parallel=2
      - if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: scheduled-fuzz-${{ matrix.target }}-${{ github.run_id }}
          path: wire/testdata/fuzz/${{ matrix.target }}/
```

The incident runbook requires the minimized failing input and exact replay
command to be attached to the issue; the fix PR must commit that input to the
target's corpus and demonstrate it fails before the fix.
