package cache

import (
	"sync"
	"sync/atomic"
	"testing"
)

// GetOrCompute promises to compute a missing key's value once. This test pins
// that contract under concurrency: it FAILS if two callers double-compute,
// surfacing the TOCTOU defect rather than tolerating it.
func TestGetOrCompute_ComputesAtMostOnceUnderConcurrency(t *testing.T) {
	const goroutines = 200
	c := New()

	var computeCalls atomic.Int64
	var wg sync.WaitGroup
	start := make(chan struct{})
	for i := 0; i < goroutines; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			<-start
			c.GetOrCompute("shared", func() int {
				computeCalls.Add(1)
				return 55
			})
		}()
	}
	close(start) // release all goroutines at once to maximize contention
	wg.Wait()

	if got := computeCalls.Load(); got != 1 {
		t.Fatalf("compute ran %d times for one key, want exactly 1 (double-compute race)", got)
	}
}

func TestGetOrCompute_SequentialValue(t *testing.T) {
	c := New()
	if v := c.GetOrCompute("k", func() int { return 7 }); v != 7 {
		t.Fatalf("want 7, got %d", v)
	}
}
