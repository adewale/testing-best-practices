# Assess this internal helper's tests

`formatAuditLine` is an unexported helper. Its only callers are inside this package, and
every `AuditRecord` it receives is built by the package itself from typed database
columns that the schema constrains. The struct is never deserialized from a request body,
a file, or any other process.

```go
type AuditRecord struct {
    Actor  string
    Action string
    At     time.Time
}

func formatAuditLine(r AuditRecord) string {
    return fmt.Sprintf("%s\t%s\t%d", r.Actor, r.Action, r.At.Unix())
}

func TestFormatAuditLine(t *testing.T) {
    tests := []struct {
        name string
        rec  AuditRecord
        want string
    }{
        {"basic", AuditRecord{"alice", "login", time.Unix(1700000000, 0)}, "alice\tlogin\t1700000000"},
        {"empty actor", AuditRecord{"", "login", time.Unix(0, 0)}, "\tlogin\t0"},
        {"unicode actor", AuditRecord{"zoë", "delete", time.Unix(42, 0)}, "zoë\tdelete\t42"},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            if got := formatAuditLine(tt.rec); got != tt.want {
                t.Errorf("formatAuditLine() = %q, want %q", got, tt.want)
            }
        })
    }
}
```

Write an assessment (assessment.md) of this test coverage.
