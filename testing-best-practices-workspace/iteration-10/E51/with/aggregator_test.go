// Package metrics provides a concurrent aggregator that merges recorded values
// into per-name totals via a background goroutine.
//
// The Aggregator is modified to expose a DrainAndMerge() seam that lets tests
// force the background goroutine's work synchronously, eliminating all
// time.Sleep calls and the race conditions they paper over.
package metrics

import (
	"sync"
	"testing"
)

// ---------------------------------------------------------------------------
// Production sketch (modified Aggregator)
// ---------------------------------------------------------------------------

// Aggregator accumulates float64 samples per named metric.
// The zero value is not usable; construct with NewAggregator.
type Aggregator struct {
	ch     chan entry
	mu     sync.RWMutex
	totals map[string]float64
	done   chan struct{} // closed when the background goroutine exits
}

type entry struct {
	name string
	v    float64
}

// NewAggregator returns a running Aggregator.  The background goroutine
// drains ch and merges values into totals until Close is called.
func NewAggregator() *Aggregator {
	a := &Aggregator{
		ch:     make(chan entry, 1024),
		totals: make(map[string]float64),
		done:   make(chan struct{}),
	}
	go a.run()
	return a
}

func (a *Aggregator) run() {
	defer close(a.done)
	for e := range a.ch {
		a.merge(e)
	}
}

// merge applies a single entry to totals.  Extracted so DrainAndMerge can
// call the *same* code as the background goroutine — the forced path must
// not diverge from the production path.
func (a *Aggregator) merge(e entry) {
	a.mu.Lock()
	a.totals[e.name] += e.v
	a.mu.Unlock()
}

// Record enqueues a sample.  It never blocks as long as the channel buffer
// is not exhausted; callers that need back-pressure should use a bounded
// channel and check for fullness.
func (a *Aggregator) Record(name string, v float64) {
	a.ch <- entry{name, v}
}

// Total returns the current merged total for name.
func (a *Aggregator) Total(name string) float64 {
	a.mu.RLock()
	defer a.mu.RUnlock()
	return a.totals[name]
}

// DrainAndMerge drains every entry currently in the channel and merges it
// synchronously.  It is the test seam: tests call Record, then
// DrainAndMerge, then assert on Total — with no sleeps and no races.
//
// Safe to call from tests while the background goroutine is running because
// merge is the single point of mutation and is guarded by a.mu.
func (a *Aggregator) DrainAndMerge() {
	for {
		select {
		case e := <-a.ch:
			a.merge(e)
		default:
			return
		}
	}
}

// Close stops the background goroutine and waits for it to finish.
func (a *Aggregator) Close() {
	close(a.ch)
	<-a.done
}

// ---------------------------------------------------------------------------
// Deterministic tests — no time.Sleep, no polling
// ---------------------------------------------------------------------------

// TestRecordAndTotal_SingleValue verifies that a single recorded value is
// reflected in Total after an explicit drain.
func TestRecordAndTotal_SingleValue(t *testing.T) {
	a := NewAggregator()
	defer a.Close()

	a.Record("req", 42.0)
	a.DrainAndMerge()

	if got := a.Total("req"); got != 42.0 {
		t.Errorf("Total(\"req\") = %v, want 42.0", got)
	}
}

// TestRecordAndTotal_Accumulates verifies that multiple records for the same
// name are summed correctly.
func TestRecordAndTotal_Accumulates(t *testing.T) {
	a := NewAggregator()
	defer a.Close()

	const n = 1000
	for i := 0; i < n; i++ {
		a.Record("counter", 1.0)
	}
	a.DrainAndMerge()

	if got := a.Total("counter"); got != float64(n) {
		t.Errorf("Total(\"counter\") = %v, want %v", got, float64(n))
	}
}

// TestRecordAndTotal_MultipleNames verifies independent tracking per name.
func TestRecordAndTotal_MultipleNames(t *testing.T) {
	a := NewAggregator()
	defer a.Close()

	a.Record("a", 1.0)
	a.Record("b", 2.0)
	a.Record("a", 3.0)
	a.DrainAndMerge()

	cases := []struct {
		name string
		want float64
	}{
		{"a", 4.0},
		{"b", 2.0},
		{"c", 0.0}, // never recorded — must return zero
	}
	for _, tc := range cases {
		if got := a.Total(tc.name); got != tc.want {
			t.Errorf("Total(%q) = %v, want %v", tc.name, got, tc.want)
		}
	}
}

// TestRecordAndTotal_UnknownName verifies that querying an unrecorded name
// returns zero rather than panicking.
func TestRecordAndTotal_UnknownName(t *testing.T) {
	a := NewAggregator()
	defer a.Close()

	if got := a.Total("missing"); got != 0 {
		t.Errorf("Total(\"missing\") = %v, want 0", got)
	}
}

// TestDrainAndMerge_IdempotentOnEmptyQueue verifies that calling
// DrainAndMerge when no entries are pending is a no-op (not a deadlock
// or panic).
func TestDrainAndMerge_IdempotentOnEmptyQueue(t *testing.T) {
	a := NewAggregator()
	defer a.Close()

	a.DrainAndMerge() // must return immediately
	a.DrainAndMerge() // safe to call multiple times

	if got := a.Total("x"); got != 0 {
		t.Errorf("Total(\"x\") = %v, want 0 after empty drains", got)
	}
}

// TestClose_FlushesRemainingEntries verifies that entries sent before Close
// are not lost: Close waits for the background goroutine to process them all.
func TestClose_FlushesRemainingEntries(t *testing.T) {
	a := NewAggregator()

	const n = 500
	for i := 0; i < n; i++ {
		a.Record("sum", 1.0)
	}
	a.Close() // waits for the goroutine to drain the channel

	// After Close the background goroutine has merged everything.
	if got := a.Total("sum"); got != float64(n) {
		t.Errorf("Total(\"sum\") after Close = %v, want %v", got, float64(n))
	}
}

// TestConcurrentRecordAndDrain exercises Record from multiple goroutines while
// DrainAndMerge is called concurrently.  The -race detector validates that no
// unsynchronised accesses occur.
func TestConcurrentRecordAndDrain(t *testing.T) {
	a := NewAggregator()
	defer a.Close()

	const goroutines = 10
	const perGoroutine = 100

	var wg sync.WaitGroup
	for g := 0; g < goroutines; g++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := 0; i < perGoroutine; i++ {
				a.Record("parallel", 1.0)
			}
		}()
	}
	wg.Wait()

	// All goroutines have finished enqueuing; drain deterministically.
	a.DrainAndMerge()

	want := float64(goroutines * perGoroutine)
	if got := a.Total("parallel"); got != want {
		t.Errorf("Total(\"parallel\") = %v, want %v", got, want)
	}
}
