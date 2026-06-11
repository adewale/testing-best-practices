// Package pool provides a connection pool with idle-connection reaping.
// This file contains both a testable sketch of Pool and deterministic tests.
package pool

import (
	"sync"
	"testing"
	"time"
)

// ---------------------------------------------------------------------------
// Production types
// ---------------------------------------------------------------------------

// Conn is the interface a connection must satisfy.
type Conn interface {
	Close() error
}

// clock is an interface for the two time operations Pool needs.
// The real implementation delegates to the standard library; tests supply
// a fake that advances on demand.
type clock interface {
	Now() time.Time
	NewTicker(d time.Duration) *time.Ticker
}

// realClock is the production implementation.
type realClock struct{}

func (realClock) Now() time.Time                  { return time.Now() }
func (realClock) NewTicker(d time.Duration) *time.Ticker { return time.NewTicker(d) }

// ---------------------------------------------------------------------------
// Pool sketch
// ---------------------------------------------------------------------------

type entry struct {
	conn     Conn
	idleSince time.Time
}

// Pool manages a bounded set of connections and closes idle ones.
type Pool struct {
	mu      sync.Mutex
	idle    []entry
	max     int
	clk     clock
	reapFn  func() // exported seam: runs one reap cycle synchronously
	stopCh  chan struct{}
}

// New creates a pool whose background reaper runs every minute.
// For tests, use newWithClock.
func New(max int) *Pool {
	return newWithClock(max, realClock{})
}

// newWithClock is the testable constructor that accepts an injectable clock.
// It also exposes a reapNow() seam so tests can trigger reaping synchronously
// without sleeping.
func newWithClock(max int, clk clock) *Pool {
	p := &Pool{
		max:    max,
		clk:    clk,
		stopCh: make(chan struct{}),
	}
	// reapFn runs the same eviction logic the background loop uses.
	// Seam 1 (forced transition): tests call p.reapNow() directly.
	p.reapFn = p.evictIdleConns

	ticker := clk.NewTicker(time.Minute)
	go func() {
		for {
			select {
			case <-ticker.C:
				p.evictIdleConns()
			case <-p.stopCh:
				ticker.Stop()
				return
			}
		}
	}()
	return p
}

// Stop shuts down the background goroutine.
func (p *Pool) Stop() {
	close(p.stopCh)
}

// Get returns an idle connection, or nil when none are available.
func (p *Pool) Get() Conn {
	p.mu.Lock()
	defer p.mu.Unlock()
	if len(p.idle) == 0 {
		return nil
	}
	e := p.idle[len(p.idle)-1]
	p.idle = p.idle[:len(p.idle)-1]
	return e.conn
}

// Put returns a connection to the pool. If the pool is full the connection
// is closed immediately.
func (p *Pool) Put(c Conn) {
	p.mu.Lock()
	defer p.mu.Unlock()
	if len(p.idle) >= p.max {
		c.Close()
		return
	}
	p.idle = append(p.idle, entry{conn: c, idleSince: p.clk.Now()})
}

// IdleCount returns the number of connections currently in the idle pool.
// Seam 2 (state introspection): tests assert directly on this count.
func (p *Pool) IdleCount() int {
	p.mu.Lock()
	defer p.mu.Unlock()
	return len(p.idle)
}

// reapNow runs one eviction cycle synchronously (test seam).
func (p *Pool) reapNow() {
	p.reapFn()
}

// evictIdleConns closes connections that have been idle for more than one
// minute. This is the shared code path used by both the background ticker
// and the test seam.
func (p *Pool) evictIdleConns() {
	cutoff := p.clk.Now().Add(-time.Minute)
	p.mu.Lock()
	live := p.idle[:0]
	var toClose []Conn
	for _, e := range p.idle {
		if e.idleSince.Before(cutoff) {
			toClose = append(toClose, e.conn)
		} else {
			live = append(live, e)
		}
	}
	p.idle = live
	p.mu.Unlock()

	for _, c := range toClose {
		c.Close()
	}
}

// ---------------------------------------------------------------------------
// Fake helpers for tests
// ---------------------------------------------------------------------------

// fakeConn is a simple Conn implementation that records whether it was closed.
type fakeConn struct {
	mu     sync.Mutex
	closed bool
}

func (fc *fakeConn) Close() error {
	fc.mu.Lock()
	defer fc.mu.Unlock()
	fc.closed = true
	return nil
}

func (fc *fakeConn) isClosed() bool {
	fc.mu.Lock()
	defer fc.mu.Unlock()
	return fc.closed
}

// fakeClock gives tests full control over the current time.
// It does NOT use real timers; NewTicker returns a channel the test never
// needs to drive (the test calls reapNow() directly instead).
type fakeClock struct {
	mu  sync.Mutex
	now time.Time
}

func newFakeClock(t time.Time) *fakeClock { return &fakeClock{now: t} }

func (fc *fakeClock) Now() time.Time {
	fc.mu.Lock()
	defer fc.mu.Unlock()
	return fc.now
}

// Advance moves the fake clock forward by d.
func (fc *fakeClock) Advance(d time.Duration) {
	fc.mu.Lock()
	defer fc.mu.Unlock()
	fc.now = fc.now.Add(d)
}

// NewTicker returns a ticker whose channel is never written to; the background
// goroutine simply blocks. Tests drive reaping via reapNow().
func (fc *fakeClock) NewTicker(d time.Duration) *time.Ticker {
	// Return a ticker with a channel we never send on so the goroutine parks.
	// We stop it in Pool.Stop().
	return &time.Ticker{C: make(chan time.Time)}
}

// epoch is a fixed instant used to pin all test clocks.
var epoch = time.Date(2024, 1, 15, 12, 0, 0, 0, time.UTC)

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

// TestGetFromEmptyPool verifies that Get returns nil when no connections are
// available.
func TestGetFromEmptyPool(t *testing.T) {
	clk := newFakeClock(epoch)
	p := newWithClock(3, clk)
	defer p.Stop()

	if got := p.Get(); got != nil {
		t.Fatalf("expected nil from empty pool, got %v", got)
	}
}

// TestPutAndGetRoundTrip verifies that a connection put into the pool can be
// retrieved.
func TestPutAndGetRoundTrip(t *testing.T) {
	clk := newFakeClock(epoch)
	p := newWithClock(3, clk)
	defer p.Stop()

	c := &fakeConn{}
	p.Put(c)

	if p.IdleCount() != 1 {
		t.Fatalf("expected IdleCount 1 after Put, got %d", p.IdleCount())
	}

	got := p.Get()
	if got != c {
		t.Fatalf("expected to get back the same conn, got %v", got)
	}
	if p.IdleCount() != 0 {
		t.Fatalf("expected IdleCount 0 after Get, got %d", p.IdleCount())
	}
}

// TestPoolFull verifies that Put closes the connection immediately when the
// pool is at capacity.
func TestPoolFull(t *testing.T) {
	clk := newFakeClock(epoch)
	p := newWithClock(2, clk)
	defer p.Stop()

	c1, c2, c3 := &fakeConn{}, &fakeConn{}, &fakeConn{}
	p.Put(c1)
	p.Put(c2)
	p.Put(c3) // pool is full; c3 must be closed immediately

	if !c3.isClosed() {
		t.Fatal("expected c3 to be closed when pool is full")
	}
	if p.IdleCount() != 2 {
		t.Fatalf("expected IdleCount 2, got %d", p.IdleCount())
	}
}

// TestIdleConnectionsNotEvictedBeforeTimeout verifies that connections idle
// for less than one minute survive a reap cycle.
func TestIdleConnectionsNotEvictedBeforeTimeout(t *testing.T) {
	clk := newFakeClock(epoch)
	p := newWithClock(5, clk)
	defer p.Stop()

	c := &fakeConn{}
	p.Put(c)

	// Advance 59 seconds — connection is NOT yet stale.
	clk.Advance(59 * time.Second)
	p.reapNow()

	if c.isClosed() {
		t.Fatal("connection should not be closed before the 1-minute idle timeout")
	}
	if p.IdleCount() != 1 {
		t.Fatalf("expected IdleCount 1, got %d", p.IdleCount())
	}
}

// TestIdleConnectionsEvictedAfterTimeout verifies that connections idle for
// exactly one minute (strictly: idleSince < now-1m) are reaped.
// No sleep is used; time is advanced via the fake clock and eviction is
// triggered via the reapNow() seam.
func TestIdleConnectionsEvictedAfterTimeout(t *testing.T) {
	clk := newFakeClock(epoch)
	p := newWithClock(5, clk)
	defer p.Stop()

	c := &fakeConn{}
	p.Put(c)

	// Advance by exactly 61 seconds so the connection is past the 1-minute
	// idle threshold, then trigger one reap cycle synchronously.
	clk.Advance(61 * time.Second)
	p.reapNow()

	if !c.isClosed() {
		t.Fatal("expected idle connection to be closed after 1-minute timeout")
	}
	if p.IdleCount() != 0 {
		t.Fatalf("expected IdleCount 0 after eviction, got %d", p.IdleCount())
	}
}

// TestOnlyStaleConnectionsEvicted verifies that reaping is selective: a fresh
// connection added after the clock advances is not evicted in the same cycle.
func TestOnlyStaleConnectionsEvicted(t *testing.T) {
	clk := newFakeClock(epoch)
	p := newWithClock(5, clk)
	defer p.Stop()

	old := &fakeConn{}
	p.Put(old)

	// Advance 61 seconds — old is now stale.
	clk.Advance(61 * time.Second)

	fresh := &fakeConn{}
	p.Put(fresh) // added at now+61s; idle for 0s

	p.reapNow()

	if !old.isClosed() {
		t.Fatal("expected stale connection to be closed")
	}
	if fresh.isClosed() {
		t.Fatal("fresh connection should not be closed")
	}
	if p.IdleCount() != 1 {
		t.Fatalf("expected IdleCount 1 (fresh conn remaining), got %d", p.IdleCount())
	}
}

// TestMultipleReapCycles verifies that reaping across two clock advances works
// correctly and does not double-close connections.
func TestMultipleReapCycles(t *testing.T) {
	clk := newFakeClock(epoch)
	p := newWithClock(5, clk)
	defer p.Stop()

	c1 := &fakeConn{}
	p.Put(c1)

	clk.Advance(61 * time.Second)
	p.reapNow() // c1 evicted

	c2 := &fakeConn{}
	p.Put(c2)

	clk.Advance(61 * time.Second)
	p.reapNow() // c2 evicted; c1 must not be double-closed

	if !c1.isClosed() {
		t.Fatal("c1 should be closed")
	}
	if !c2.isClosed() {
		t.Fatal("c2 should be closed")
	}
	if p.IdleCount() != 0 {
		t.Fatalf("expected IdleCount 0, got %d", p.IdleCount())
	}
}

// TestReapDoesNotCloseConnectionsInUse verifies that a connection removed via
// Get is not affected by a subsequent reap cycle.
func TestReapDoesNotCloseConnectionsInUse(t *testing.T) {
	clk := newFakeClock(epoch)
	p := newWithClock(5, clk)
	defer p.Stop()

	c := &fakeConn{}
	p.Put(c)

	inUse := p.Get() // remove from pool before time advances

	clk.Advance(61 * time.Second)
	p.reapNow()

	if inUse.(*fakeConn).isClosed() {
		t.Fatal("connection that was checked out must not be closed by the reaper")
	}
}
