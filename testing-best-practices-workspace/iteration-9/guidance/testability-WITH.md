# Deterministic Time Testing

For any code that depends on time — timers, TTLs, retry backoffs, cache
expiry, timeouts, scheduled jobs, "last seen" tracking — tests must never
depend on wall-clock time. Two strategies remove that dependence:
**virtualization** (intercept the system clock) and **injection** (pass
a clock object explicitly).

## The bug class this catches

Tests that depend on real time produce:
- `time.sleep(5)` waiting for a timer — slow AND occasionally flaky
- Assertions that pass on a fast machine but fail on a busy CI runner
- Tests that fail at midnight UTC or during DST transitions
- Cache TTL tests that pass most of the time but fire once a month

The universal rule, before any strategy: **never call real `sleep()` /
`Thread.sleep()` / `setTimeout` with real time in tests**. If you can't
remove it, your code has a time seam in the wrong place.

## Strategy 1: Process-level virtualization

Intercept the system clock without changing production code. Best when
you're retrofitting tests onto existing code, or when there's a single
clock in the system.

### Python: `freezegun` or `time-machine`

```python
from freezegun import freeze_time

@freeze_time("2024-01-15 12:00:00")
def test_cache_expiry():
    cache.set("key", "value", ttl=60)
    assert cache.get("key") == "value"
    with freeze_time("2024-01-15 12:01:01"):  # 61s later
        assert cache.get("key") is None
```

`time-machine` is faster; `freezegun` is more widely deployed.

### JavaScript/TypeScript: `vi.useFakeTimers()` / `@sinonjs/fake-timers`

```typescript
import { vi } from 'vitest';

test('cache expires after TTL', () => {
  vi.useFakeTimers();
  cache.set('key', 'value', { ttl: 60_000 });
  expect(cache.get('key')).toBe('value');
  vi.advanceTimersByTime(60_001);
  expect(cache.get('key')).toBeUndefined();
  vi.useRealTimers();
});
```

### Ruby: `timecop`. C/C++: `libfaketime` (LD_PRELOAD).

### When virtualization is the wrong tool
- Multiple independent clocks need to advance differently (server vs client time)
- Third-party native code calls `gettimeofday` directly and bypasses the hook
- The system under test is a library that may be embedded in any time context

Switch to injection.

## Strategy 2: Architectural injection

Pass a `Clock` object at architectural seams — the places where time enters
the system. Production uses the real clock; tests pass a controllable fake.
**Don't thread a clock through every function** — only at the seams.

### Java: built-in `java.time.Clock`

```java
public class Cache {
    private final Clock clock;
    public Cache(Clock clock) { this.clock = clock; }
    public void set(String key, V value, Duration ttl) {
        entries.put(key, new Entry(value, clock.instant().plus(ttl)));
    }
}

// Test
var fixed = Clock.fixed(Instant.parse("2024-01-15T12:00:00Z"), ZoneOffset.UTC);
var cache = new Cache(fixed);
```

### Go: `clock.Clock` interface (`clockwork` or `benbjohnson/clock`)

```go
type Cache struct { clock clockwork.Clock }

// Production
cache := &Cache{clock: clockwork.NewRealClock()}

// Test
fake := clockwork.NewFakeClock()
cache := &Cache{clock: fake}
fake.Advance(time.Minute)
```

Go's standard library has no virtualization hook, so injection is idiomatic.

### TypeScript: when sinon isn't enough

```typescript
type Now = () => number;

class Cache {
  constructor(private readonly now: Now = Date.now) {}
}

// Test with two independent clocks
let serverTime = 1_000_000;
let clientTime = 1_000_000;
const server = new Cache(() => serverTime);
const client = new Cache(() => clientTime);
serverTime += 60_000;  // server advances, client doesn't — model clock skew
```

### Python: when freezegun isn't enough

```python
class Cache:
    def __init__(self, clock: Callable[[], float] = time.monotonic):
        self._clock = clock
```

### Rust: pass a trait

```rust
trait Clock { fn now(&self) -> Instant; }
```

No standard `Clock` trait yet. Define one per project or take a `fn() -> Instant`.

## Choosing between strategies

| Situation | Strategy |
|-----------|----------|
| Single app, single clock, retrofit existing tests | Virtualization |
| New code, library author | Injection |
| Distributed system test modeling clock skew | Injection (one clock per component) |
| Code under test uses third-party timers | Virtualization |
| Test needs server time ≠ client time | Injection |
| Multiple time scales (monotonic vs wall) | Injection |

## Lint to keep the seam in place

Once time-dependent code is behind a seam, ban wall-clock APIs everywhere else.
A code review rule is too leaky — make it a compile-time / lint-time error.

- ESLint: `no-restricted-properties` on `Date.now`, `new Date()`, `performance.now`
- Ruff (Python): custom rule banning `time.time()`, `datetime.now()` (require explicit clock or `freeze_time`)
- Go: `golangci-lint` with `forbidigo` banning `time.Now`, `time.Since`, `time.After`
- Java: ArchUnit restricting `Instant.now()`, `System.currentTimeMillis()`
- Rust: clippy `disallowed_methods` for `Instant::now`, `SystemTime::now`

Allow the wall-clock API only inside the one module that constructs the real
clock for production.

## Rules that apply to both strategies

1. **Pin the test's starting time.** Tests using "now" become unstable across
   dates and time zones. Fix to a known instant.
2. **Advance by the exact amount needed.** Don't `advance(0.1)` "to be safe."
   If the test needs T+60s, advance exactly 60s.
3. **Watch for multiple time sources.** Server time, DB time, request
   timestamps, audit logs — each is a separate clock. Freezing one but not
   another produces confusing failures.
4. **Verify timer-fire ordering.** Advancing time by 10s with timers at 1s,
   3s, 7s should fire them in scheduled order, not all at once. Most
   virtualization libraries do this; check yours.
5. **Don't mix strategies in one test.** A test that uses `freezegun` but
   passes a real `time.time()` to a helper has two clocks. Pick one.

## What this looks like at the extreme

Jane Street's OCaml `Time_source` makes the clock an explicit parameter of
every Async API. The compiler enforces it: `open! Require_explicit_time_source`
deprecates wall-clock APIs at the type level. Tests construct independent
time sources for each component:

```ocaml
let server_time_source = Synchronous_time_source.create ~now:Time_ns.epoch ()
let client_time_source = Synchronous_time_source.create ~now:Time_ns.epoch ()
(* Advance server clock independently of client — models clock skew *)
Synchronous_time_source.advance_by_alarms_by server_time_source heartbeat_timeout
```

This is the gold standard but takes a decade-long architectural commitment.
For most projects: virtualization for existing code, injection at the few
new architectural boundaries that need independent clocks.

## Anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
| `time.sleep(5)` waiting for a timer | Virtualize or inject; advance time directly |
| `time.sleep(0.1)` "just to be safe" | Race condition; fix synchronization, don't paper over it |
| Hard-coded timestamps that match `now()` | Pin the clock first, then assert exact equality |
| `assert abs(ts - now()) < 1` | Freeze time; assert exact equality |
| Test that depends on the day of week | Pin the clock to a fixed weekday |
| Mock the clock in one test but use real time in its helper | Mixed clocks; pick one strategy per test |
| Test that runs reliably only during business hours | DST or business-hours logic uses wall clock; freeze it |


---

# Design for Testability

When a test is hard to write — it sleeps, polls, guesses at timing, or can't
observe what actually happened — the fix is usually in the **system under
test**, not the test. Add a small, guarded seam that lets tests force events
and observe state deterministically. (Pattern source: Redis's `DEBUG` command
surface — `DEBUG RELOAD`, `DEBUG SET-ACTIVE-EXPIRE`, `OBJECT ENCODING` exist
so tests can introspect and control the engine instead of waiting on it.)

Time-driven behavior has its own reference (`deterministic-time.md`, clock
injection/virtualization). This one covers the other seams.

## Seam 1: Forced transitions

Background or asynchronous work — flush threads, eviction sweeps, connection
reapers, compaction — should be callable synchronously from a test:

```python
class WriteBuffer:
    def __init__(self, path, auto_flush=True):
        self._auto_flush = auto_flush          # tests pass False
        ...
    def flush_now(self):
        """Run one flush cycle synchronously. Used by production shutdown
        and by tests; does exactly what the background loop does."""
        ...
```

```python
def test_flush_writes_batch():
    buf = WriteBuffer(path, auto_flush=False)   # no background thread
    buf.write(record_a); buf.write(record_b)
    buf.flush_now()                              # force the transition
    assert read_records(path) == [record_a, record_b]
```

The forced path must execute the *same code* the background loop runs — a
separate "test path" tests nothing.

## Seam 2: State introspection

If correctness depends on internal representation (an index was used, a
small-size encoding engaged, a buffer actually emptied), expose it read-only
and assert on it — don't infer it from timing or side effects:

```python
assert buf.pending_count() == 0          # not "sleep then hope"
assert cache.encoding_of("k") == "intset"  # the optimization actually engaged
```

A silent fallback to a slower/larger representation is a real bug; a test can
only catch it if the representation is observable.

## Seam 3: Poll a predicate (only when you can't force)

For genuinely concurrent conditions that no seam can force (another process,
real network), poll a cheap observable predicate with a bounded retry budget
and a clear failure message. Never bare-sleep:

```python
def wait_for(predicate, tries=50, delay_s=0.1, msg="condition not met"):
    for _ in range(tries):
        if predicate():
            return
        time.sleep(delay_s)
    raise AssertionError(msg)
```

Prefer seams 1–2; reach for polling last. A test that *can* force the event
but polls instead is slower and flakier for no benefit.

## Guardrails — a seam must not weaken the system

- **Never bypass security or business rules.** A "test mode" that disables
  auth, rate limiting, or validation — especially via an environment variable
  a production deploy can set — is a vulnerability, not a seam. Make the
  *clock or scheduler* injectable instead, so the rule itself stays intact
  and the test controls what the rule observes.
- **Seams control scheduling and observation, not outcomes.** `flush_now()`
  forces *when* work happens; it must not change *what* the work does.
- **Gate the surface.** Constructor parameters with safe defaults
  (`auto_flush=True`), test-only build tags, or a namespaced debug surface
  that hardened builds disable (Redis's `needs:debug` tagging lets the same
  suite run against builds without `DEBUG`).
- **Keep introspection read-only** and don't let tests reach into private
  state by name (`obj._internal`) — that couples tests to implementation
  details a refactor will break. The seam is a public, documented contract.

## When NOT to add a seam

- The behavior is already synchronous and observable through the public API —
  test it directly.
- The "hard to test" part is time itself — use `deterministic-time.md`.
- The seam would expose secrets, PII, or a security bypass — redesign so the
  test controls inputs (clock, scheduler) rather than disabling the rule.
