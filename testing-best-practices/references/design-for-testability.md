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
