package metrics

import "testing"

// Sketch: seam = synchronous mode (no goroutine) + Drain() running the SAME
// merge code the background goroutine runs.
type testAggregator struct{ *Aggregator }

func newSyncAggregator() *Aggregator {
	return NewAggregatorWithOptions(Options{StartWorker: false})
}

func TestTotalsAfterForcedDrain(t *testing.T) {
	a := newSyncAggregator()
	for i := 0; i < 1000; i++ {
		a.Record("requests", 1)
	}
	a.Drain() // force the merge; same code path as the worker
	if got := a.Total("requests"); got != 1000 {
		t.Fatalf("Total = %v, want 1000", got)
	}
	if p := a.PendingCount(); p != 0 {
		t.Errorf("pending = %d after drain, want 0", p)
	}
}

func TestDrainOnEmptyQueueIsNoop(t *testing.T) {
	a := newSyncAggregator()
	a.Drain()
	if got := a.Total("anything"); got != 0 {
		t.Errorf("Total = %v on empty aggregator", got)
	}
}
