# Go Testing Reference

## Framework: testing (stdlib)

### Test file conventions

- Test files: `*_test.go` in the same package
- Test functions: `func TestXxx(t *testing.T)`
- Benchmarks: `func BenchmarkXxx(b *testing.B)`
- Examples: `func ExampleXxx()`

### Running tests

```bash
go test ./...                    # All tests
go test ./... -v                 # Verbose
go test -race ./...              # Race detector
go test -cover ./...             # Coverage summary
go test -tags=network ./...      # Include tagged tests
go test -count=1 ./...           # Disable test caching
```

### Coverage

```bash
go test -coverprofile=cover.out ./...
go tool cover -html=cover.out         # HTML report
go tool cover -func=cover.out         # Per-function summary
```

## Table-Driven Tests

The standard Go pattern. Every test should use this:

```go
func TestValidateURL(t *testing.T) {
    tests := []struct {
        name    string
        url     string
        wantErr bool
    }{
        {"valid http", "http://example.com", false},
        {"valid https", "https://example.com", false},
        {"localhost blocked", "http://localhost", true},
        {"private IP blocked", "http://192.168.1.1", true},
        {"empty string", "", true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            err := ValidateURL(tt.url)
            if (err != nil) != tt.wantErr {
                t.Errorf("ValidateURL(%q) error = %v, wantErr %v", tt.url, err, tt.wantErr)
            }
        })
    }
}
```

## Test Isolation

### Use t.TempDir() for filesystem tests

```go
func TestDatabaseOperations(t *testing.T) {
    dir := t.TempDir()  // Auto-cleaned after test
    dbPath := filepath.Join(dir, "test.db")
    repo, err := repository.New(dbPath)
    if err != nil {
        t.Fatalf("failed to create repo: %v", err)
    }
    defer repo.Close()
    // ... test with real SQLite database
}
```

### Use httptest.NewServer for HTTP tests

```go
func TestFetchWithConditionalRequest(t *testing.T) {
    srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        if r.Header.Get("If-None-Match") == `"abc123"` {
            w.WriteHeader(http.StatusNotModified)
            return
        }
        w.Header().Set("ETag", `"abc123"`)
        w.Write([]byte("response body"))
    }))
    defer srv.Close()

    // Test against real HTTP server
    result, err := Fetch(srv.URL)
    // ...
}
```

### Testing constructors for testability

```go
// Production constructor with security checks
func New(opts Options) *Crawler { ... }

// Test constructor that disables SSRF checks
func NewForTesting(opts Options) *Crawler {
    c := New(opts)
    c.disableSSRF = true
    return c
}
```

## Build Tags for Conditional Tests

```go
//go:build network

package crawler

// These tests require internet access
func TestLiveFeedFetch(t *testing.T) { ... }
```

Run with: `go test -tags=network ./pkg/crawler`

## Assertion Patterns

Go has no assertion library in stdlib. Use `t.Errorf` (continue) or
`t.Fatalf` (stop):

```go
// WRONG: t.Log never fails the test
if got != want {
    t.Logf("got %v, want %v", got, want)  // BUG: should be t.Errorf
}

// RIGHT: t.Errorf fails the test but continues
if got != want {
    t.Errorf("got %v, want %v", got, want)
}

// RIGHT: t.Fatalf fails and stops this test immediately
if err != nil {
    t.Fatalf("setup failed: %v", err)
}
```

## Test Output Injection

Make CLI output testable by accepting `io.Writer`:

```go
type Options struct {
    Output io.Writer  // Production: os.Stdout, Tests: &bytes.Buffer{}
}

func Run(opts Options) error {
    fmt.Fprintf(opts.Output, "result: %d\n", count)
    return nil
}

// In tests:
var buf bytes.Buffer
err := Run(Options{Output: &buf})
if !strings.Contains(buf.String(), "result: 42") {
    t.Errorf("unexpected output: %s", buf.String())
}
```

## Fake Server Pattern

For protocol testing, write an in-process fake:

```go
type testServer struct {
    mu   sync.Mutex
    data map[string][]byte
}

func (s *testServer) Serve(ln net.Listener) { ... }

func TestWithFakeServer(t *testing.T) {
    ln, _ := net.Listen("tcp", "localhost:0")
    srv := &testServer{data: make(map[string][]byte)}
    go srv.Serve(ln)
    defer ln.Close()

    client := New(ln.Addr().String())
    testOperations(t, client)  // Same tests run against fake AND real
}
```

## testdata/ Convention

Go has a standard convention: the `testdata/` directory is ignored by the Go
tool and is used for test fixtures (saved feed snapshots, golden files, etc.).

```go
func TestParseRealFeed(t *testing.T) {
    data, err := os.ReadFile("testdata/daringfireball-feed.xml")
    if err != nil {
        t.Fatalf("failed to read fixture: %v", err)
    }
    result := Parse(data)
    // ... assertions against real-world feed data
}
```

Commit fixtures to the repo. This eliminates network flakiness and makes
tests reproducible.

## t.Helper(), t.Cleanup(), TestMain

### t.Helper() — better error reporting for test helpers

```go
func assertContains(t *testing.T, haystack, needle string) {
    t.Helper()  // Error reports the caller's line, not this line
    if !strings.Contains(haystack, needle) {
        t.Errorf("expected %q to contain %q", haystack, needle)
    }
}
```

### t.Cleanup() — alternative to defer

```go
func TestWithResource(t *testing.T) {
    db := openTestDB(t)
    t.Cleanup(func() { db.Close() })
    // ... test runs, db.Close() called even on failure
}
```

### TestMain — suite-level setup/teardown

```go
func TestMain(m *testing.M) {
    // Setup (runs once before all tests)
    db := setupGlobalTestDB()
    defer db.Close()

    // Run all tests
    os.Exit(m.Run())
}
```

## Example Tests as Documentation

```go
func ExampleReverse() {
    fmt.Println(Reverse("hello"))
    // Output: olleh
}
```

Example tests are both tests AND documentation — they appear in `go doc`
output and on pkg.go.dev. The `// Output:` comment is the assertion.

## Parallel Tests and Serial Markers

```go
func TestParallel(t *testing.T) {
    t.Parallel()  // Can run alongside other parallel tests
    // ...
}
```

For tests that must run serially (shared state, ports), don't call
`t.Parallel()`. In CI, split: `go test -parallel 4` for parallel,
separate run for serial tests.

## Makefile Targets

```makefile
test:          go test ./...
test-race:     go test -race ./...
test-cover:    go test -coverprofile=cover.out ./... && go tool cover -html=cover.out
test-network:  go test -tags=network ./...
quick:         go fmt ./... && go vet ./... && go test ./...
check:         go fmt ./... && go vet ./... && go test -race ./...
```
