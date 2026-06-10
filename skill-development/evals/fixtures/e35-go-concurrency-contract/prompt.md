# E35 Go Concurrency-Contract Fixture

Write Go tests for a `Cache` whose `GetOrCompute(key, compute)` is documented to
compute a missing key's value **once** and is intended to be safe for concurrent
use by many goroutines. The implementation reads under a lock, computes the
value *outside* the lock, then stores under the lock.

A strong suite must exercise the cache from many concurrent goroutines AND pin
the concurrency contract: assert that `compute` runs at most once per key under
contention (a failing test that surfaces the double-compute TOCTOU race), run
under `go test -race`, rather than logging the observed compute count and
tolerating whatever happens.
