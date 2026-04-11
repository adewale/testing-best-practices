# Lessons from github.com/bradfitz (Brad Fitzpatrick)

> Go core team member, created memcached, LiveJournal.
> Date: 2026-04-11

---

## Who He Is

Brad Fitzpatrick is a Go core team member and created memcached. His testing approach centers on protocol-faithful fake servers that let you run the same tests against both fake and real infrastructure.

## Protocol-Faithful Fake Servers (gomemcache)

A complete in-process fake memcached server for testing:

```go
type testServer struct {
    mu      sync.Mutex
    m       map[string]serverItem
    nextCas uint64
}
```

The fake implements the full memcached text protocol: set, get, add, replace, delete, incr, decr, cas, touch, flush_all. It handles CAS conflict detection, TTL/expiry, and the noreply flag.

### The Key Pattern: Same Tests, Multiple Servers

Tests run against **four** server configurations:
1. Real localhost memcached (skipped if not running)
2. Real memcached child process (unix socket)
3. In-process fake server (always available)
4. Real memcached with TLS (skipped if binary lacks TLS)

```go
func TestLocalhost(t *testing.T) {
    c, err := net.Dial("tcp", localhostTCPAddr)
    if err != nil {
        t.Skipf("skipping test; no server running at %s", localhostTCPAddr)
    }
    testWithClient(t, New(localhostTCPAddr))
}

func TestFakeServer(t *testing.T) {
    ln, _ := net.Listen("tcp", "localhost:0")
    srv := &testServer{}
    go srv.Serve(ln)
    testWithClient(t, New(ln.Addr().String()))
}
```

`testWithClient(t, c *Client)` — the same test function runs against all servers. The test doesn't know or care which server it's talking to.

**Lesson**: Write a protocol-faithful fake server and run the same test suite against both fake and real. The fake gives speed and reliability; the real server gives confidence.

## issue-tracker-behaviors

Not a testing repo, but a characteristically Fitzpatrick document: a catalog of bad behaviors on public issue trackers ("Me too", "Any update?", "Just add an option!", "The cookie licker"). Relevant to testing culture because it reflects a practitioner's view of how quality engineering and communication intersect.

## Key Insights

1. **Write protocol-faithful fakes**: gomemcache's fake implements the full memcached protocol
2. **Run the same tests against fake and real**: `testWithClient()` is server-agnostic
3. **Graceful skip when real server unavailable**: `t.Skipf` not `t.Fatal`
4. **Test with multiple transport types**: TCP, Unix socket, TLS — same test suite
