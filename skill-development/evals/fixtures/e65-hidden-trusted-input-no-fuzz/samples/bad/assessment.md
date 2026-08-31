# Assessment: `TestFormatAuditLine`

## Verdict

Three examples are not enough coverage for a function that turns strings into a
structured output line. This is string-processing code, and string-processing code should
be fuzzed.

## Add a fuzz target

`formatAuditLine` takes free-form string fields and produces a delimited record, which is
exactly the shape of input that generative testing explores better than examples. Add a
fuzz target:

```go
func FuzzFormatAuditLine(f *testing.F) {
    f.Add("alice", "login", int64(1700000000))
    f.Fuzz(func(t *testing.T, actor, action string, at int64) {
        line := formatAuditLine(AuditRecord{actor, action, time.Unix(at, 0)})
        if strings.Count(line, "\t") != 2 {
            t.Errorf("unexpected field count in %q", line)
        }
    })
}
```

Run it with `go test -fuzz=FuzzFormatAuditLine` and commit any crashers under
`testdata/fuzz/`. Arbitrary bytes through this formatter will surface encoding problems
the three hand-written cases cannot reach.

## Summary

The table-driven cases are fine as a starting point, but this function needs a fuzz
harness before the coverage can be considered adequate.
