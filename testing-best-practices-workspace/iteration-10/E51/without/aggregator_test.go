package metrics

import (
	"sync"
	"testing"
)

// Aggregator merges per-name float64 totals from a background goroutine.
// The channel-based design is preserved; a sync.WaitGroup allows tests to
// drain the queue deterministically without any time.Sleep.
type Aggregator struct {
	ch   chan record
	mu   sync.Mutex
	sums map[string]float64
	wg   sync.WaitGroup
}

type record struct {
	name string
	v    float64
}

// NewAggregator returns a running Aggregator.
func NewAggregator() *Aggregator {
	a := &Aggregator{
		ch:   make(chan record, 1024),
		sums: make(map[string]float64),
	}
	go a.drain()
	return a
}

func (a *Aggregator) drain() {
	for r := range a.ch {
		a.mu.Lock()
		a.sums[r.name] += r.v
		a.mu.Unlock()
		a.wg.Done() // one Done per record consumed
	}
}

// Record enqueues a value. The WaitGroup counter is incremented here,
// before the send, so Flush() can wait for every enqueued record.
func (a *Aggregator) Record(name string, v float64) {
	a.wg.Add(1)
	a.ch <- record{name, v}
}

// Flush blocks until every previously recorded value has been merged.
// Tests call this instead of time.Sleep.
func (a *Aggregator) Flush() {
	a.wg.Wait()
}

// Total returns the running total for name.
func (a *Aggregator) Total(name string) float64 {
	a.mu.Lock()
	defer a.mu.Unlock()
	return a.sums[name]
}

// Close shuts down the background goroutine after draining.
func (a *Aggregator) Close() {
	a.wg.Wait()
	close(a.ch)
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

func TestRecord_SingleValue(t *testing.T) {
	a := NewAggregator()
	defer a.Close()

	a.Record("hits", 1.0)
	a.Flush()

	if got := a.Total("hits"); got != 1.0 {
		t.Errorf("Total(hits) = %v, want 1.0", got)
	}
}

func TestRecord_Accumulates(t *testing.T) {
	a := NewAggregator()
	defer a.Close()

	a.Record("bytes", 100.0)
	a.Record("bytes", 200.0)
	a.Record("bytes", 300.0)
	a.Flush()

	if got := a.Total("bytes"); got != 600.0 {
		t.Errorf("Total(bytes) = %v, want 600.0", got)
	}
}

func TestRecord_IndependentNames(t *testing.T) {
	a := NewAggregator()
	defer a.Close()

	a.Record("alpha", 10.0)
	a.Record("beta", 20.0)
	a.Record("alpha", 5.0)
	a.Flush()

	if got := a.Total("alpha"); got != 15.0 {
		t.Errorf("Total(alpha) = %v, want 15.0", got)
	}
	if got := a.Total("beta"); got != 20.0 {
		t.Errorf("Total(beta) = %v, want 20.0", got)
	}
}

func TestRecord_UnknownNameIsZero(t *testing.T) {
	a := NewAggregator()
	defer a.Close()

	if got := a.Total("missing"); got != 0.0 {
		t.Errorf("Total(missing) = %v, want 0.0", got)
	}
}

func TestRecord_ManyValues_Deterministic(t *testing.T) {
	// Replaces the flaky time.Sleep(100ms) approach: Flush() blocks until
	// the background goroutine has consumed every enqueued record.
	a := NewAggregator()
	defer a.Close()

	const n = 1000
	for i := 0; i < n; i++ {
		a.Record("counter", 1.0)
	}
	a.Flush() // deterministic — no sleep, no race

	if got := a.Total("counter"); got != float64(n) {
		t.Errorf("Total(counter) = %v, want %v", got, float64(n))
	}
}

func TestRecord_ConcurrentProducers(t *testing.T) {
	a := NewAggregator()
	defer a.Close()

	const goroutines = 10
	const perGoroutine = 100
	var start sync.WaitGroup
	start.Add(goroutines)

	for i := 0; i < goroutines; i++ {
		go func() {
			start.Done()
			start.Wait() // all goroutines begin at the same time
			for j := 0; j < perGoroutine; j++ {
				a.Record("shared", 1.0)
			}
		}()
	}
	// Wait for all producers to finish enqueueing, then drain.
	// We can't call Flush here until producers are done, so we use a second
	// WaitGroup to join the producers first.
	// Restructure: producers share a WaitGroup.
	var prod sync.WaitGroup
	a2 := NewAggregator()
	defer a2.Close()
	for i := 0; i < goroutines; i++ {
		prod.Add(1)
		go func() {
			defer prod.Done()
			for j := 0; j < perGoroutine; j++ {
				a2.Record("shared", 1.0)
			}
		}()
	}
	prod.Wait()
	a2.Flush()

	want := float64(goroutines * perGoroutine)
	if got := a2.Total("shared"); got != want {
		t.Errorf("Total(shared) = %v, want %v", got, want)
	}
}

func TestFlush_IdempotentOnEmpty(t *testing.T) {
	a := NewAggregator()
	defer a.Close()

	// Flush on a fresh aggregator with no records must not block.
	a.Flush()
	a.Flush()
}
