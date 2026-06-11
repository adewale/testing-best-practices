# E53 Assess a Go test behind fault-masking code

Assess the quality of this Go test. The function and its test:

```go
func ParseAndScore(raw string) (score int) {
    defer func() {
        if recover() != nil {
            score = 0
        }
    }()
    s := mustParseAndScore(raw) // may panic on bad data
    if s < 0 {
        s = 0
    } else if s > 100 {
        s = 100
    }
    return s
}

func TestParseAndScore(t *testing.T) {
    for _, raw := range samples {
        if got := ParseAndScore(raw); got < 0 {
            t.Errorf("negative score %d", got)
        }
    }
}
```

Write an assessment (assessment.md) of how well this test verifies `ParseAndScore`.
