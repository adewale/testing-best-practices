package pool

import (
	"testing"
	"time"
)

// Sketch: seam = injectable now func + ReapNow() running the SAME sweep the
// background goroutine runs; startReaper=false keeps tests single-threaded.
type testPool struct {
	*Pool
}

func newTestPool(max int, now func() time.Time) *Pool {
	return NewWithOptions(max, Options{Now: now, StartReaper: false})
}

func TestReapClosesIdleConnections(t *testing.T) {
	current := time.Unix(0, 0)
	now := func() time.Time { return current }
	p := newTestPool(4, now)

	c := p.Get()
	p.Put(c)
	if p.IdleCount() != 1 {
		t.Fatalf("idle = %d, want 1", p.IdleCount())
	}

	current = current.Add(2 * time.Minute) // advance injected clock
	p.ReapNow()                            // force the sweep
	if p.IdleCount() != 0 {
		t.Errorf("idle = %d after reap, want 0", p.IdleCount())
	}
}

func TestReapKeepsFreshConnections(t *testing.T) {
	current := time.Unix(0, 0)
	p := newTestPool(4, func() time.Time { return current })
	p.Put(p.Get())
	current = current.Add(10 * time.Second)
	p.ReapNow()
	if p.IdleCount() != 1 {
		t.Errorf("fresh connection was reaped")
	}
}
