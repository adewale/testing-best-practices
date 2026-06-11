// Package pool provides a connection pool with idle-connection cleanup.
// The Pool struct is modified to accept an injectable clock so that the
// background reaper can be tested deterministically without real sleeps.
package pool

import (
	"sync"
	"testing"
	"time"
)

// ---------------------------------------------------------------------------
// Clock abstraction (the architectural seam)
// ---------------------------------------------------------------------------

// Clock is the interface the Pool uses to read the current time and create
// tickers. Production code passes realClock{}; tests pass fakeClock.
type Clock interface {
	Now() time.Time
	NewTicker(d time.Duration) (<-chan time.Time, func())
}

// realClock delegates to the standard library.
type realClock struct{}

func (realClock) Now() time.Time { return time.Now() }
func (realClock) NewTicker(d time.Duration) (<-chan time.Time, func()) {
	t := time.NewTicker(d)
	return t.C, t.Stop
}

// fakeClock is a controllable clock for tests.
type fakeClock struct {
	mu      sync.Mutex
	now     time.Time
	tickers []*fakeTicker
}

type fakeTicker struct {
	ch   chan time.Time
	stop chan struct{}
}

func newFakeClock(start time.Time) *fakeClock {
	return &fakeClock{now: start}
}

func (fc *fakeClock) Now() time.Time {
	fc.mu.Lock()
	defer fc.mu.Unlock()
	return fc.now
}

func (fc *fakeClock) NewTicker(d time.Duration) (<-chan time.Time, func()) {
	ft := &fakeTicker{
		ch:   make(chan time.Time, 1),
		stop: make(chan struct{}),
	}
	fc.mu.Lock()
	fc.tickers = append(fc.tickers, ft)
	fc.mu.Unlock()
	stopFn := func() { close(ft.stop) }
	return ft.ch, stopFn
}

// Advance moves the fake clock forward by d and fires all registered tickers
// (simulating that the ticker interval has elapsed).
func (fc *fakeClock) Advance(d time.Duration) {
	fc.mu.Lock()
	fc.now = fc.now.Add(d)
	t := fc.now
	tickers := make([]*fakeTicker, len(fc.tickers))
	copy(tickers, fc.tickers)
	fc.mu.Unlock()

	for _, ft := range tickers {
		select {
		case ft.ch <- t:
		default:
		}
	}
}

// ---------------------------------------------------------------------------
// Conn and Pool sketch
// ---------------------------------------------------------------------------

// Conn represents an opaque connection managed by the Pool.
type Conn interface {
	Close() error
}

// fakeConn is a simple Conn used in tests.
type fakeConn struct {
	closed bool
	mu     sync.Mutex
}

func (c *fakeConn) Close() error {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.closed = true
	return nil
}

func (c *fakeConn) isClosed() bool {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.closed
}

// idleEntry pairs a connection with the time it was returned to the pool.
type idleEntry struct {
	conn     Conn
	idleSince time.Time
}

// Pool is the connection pool. The clock field is the injectable time seam.
type Pool struct {
	mu      sync.Mutex
	idle    []idleEntry
	max     int
	clock   Clock
	stopCh  chan struct{}
	stopped chan struct{}
}

// New creates a Pool that uses the real system clock and starts the background
// reaper. It is the production constructor.
func New(max int) *Pool {
	return newWithClock(max, realClock{})
}

// newWithClock is the internal constructor used by both New and tests.
func newWithClock(max int, clk Clock) *Pool {
	p := &Pool{
		max:     max,
		clock:   clk,
		stopCh:  make(chan struct{}),
		stopped: make(chan struct{}),
	}
	go p.reaper()
	return p
}

// reaper runs a loop that closes connections idle for more than a minute.
func (p *Pool) reaper() {
	defer close(p.stopped)
	tickCh, stopTick := p.clock.NewTicker(time.Minute)
	defer stopTick()
	for {
		select {
		case <-p.stopCh:
			return
		case now := <-tickCh:
			p.mu.Lock()
			kept := p.idle[:0]
			for _, e := range p.idle {
				if now.Sub(e.idleSince) > time.Minute {
					_ = e.conn.Close()
				} else {
					kept = append(kept, e)
				}
			}
			p.idle = kept
			p.mu.Unlock()
		}
	}
}

// Stop shuts down the background reaper. Call in tests to avoid goroutine leaks.
func (p *Pool) Stop() {
	close(p.stopCh)
	<-p.stopped
}

// Get returns an idle connection if one is available, or nil otherwise.
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

// Put returns a connection to the pool. If the pool is full the connection is
// closed immediately.
func (p *Pool) Put(c Conn) {
	p.mu.Lock()
	defer p.mu.Unlock()
	if len(p.idle) >= p.max {
		_ = c.Close()
		return
	}
	p.idle = append(p.idle, idleEntry{conn: c, idleSince: p.clock.Now()})
}

// IdleCount returns the number of connections currently sitting idle.
func (p *Pool) IdleCount() int {
	p.mu.Lock()
	defer p.mu.Unlock()
	return len(p.idle)
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

// epoch is a fixed instant used to pin the fake clock so tests are not
// sensitive to the actual wall-clock time.
var epoch = time.Date(2024, 1, 15, 12, 0, 0, 0, time.UTC)

// TestPutAndGet verifies basic Put/Get round-trip behaviour.
func TestPutAndGet(t *testing.T) {
	clk := newFakeClock(epoch)
	p := newWithClock(5, clk)
	defer p.Stop()

	c := &fakeConn{}
	p.Put(c)

	if got := p.IdleCount(); got != 1 {
		t.Fatalf("IdleCount after Put: got %d, want 1", got)
	}

	got := p.Get()
	if got == nil {
		t.Fatal("Get returned nil, want the connection we Put")
	}
	if got != c {
		t.Fatal("Get returned a different connection than the one Put")
	}
	if p.IdleCount() != 0 {
		t.Fatalf("IdleCount after Get: got %d, want 0", p.IdleCount())
	}
}

// TestGetOnEmptyPool verifies that Get returns nil when no connections are idle.
func TestGetOnEmptyPool(t *testing.T) {
	clk := newFakeClock(epoch)
	p := newWithClock(5, clk)
	defer p.Stop()

	if got := p.Get(); got != nil {
		t.Fatalf("Get on empty pool: got %v, want nil", got)
	}
}

// TestPoolMaxCapacity verifies that Put closes the connection when the pool is full.
func TestPoolMaxCapacity(t *testing.T) {
	clk := newFakeClock(epoch)
	p := newWithClock(2, clk)
	defer p.Stop()

	c1, c2, c3 := &fakeConn{}, &fakeConn{}, &fakeConn{}
	p.Put(c1)
	p.Put(c2)
	p.Put(c3) // pool is full; c3 must be closed immediately

	if p.IdleCount() != 2 {
		t.Fatalf("IdleCount after overflow Put: got %d, want 2", p.IdleCount())
	}
	if !c3.isClosed() {
		t.Fatal("overflowing connection was not closed")
	}
}

// TestReaperClosesIdleConnections verifies that connections idle for more than
// one minute are closed by the background reaper.
// The fake clock is advanced by just over a minute, which causes the fake
// ticker to fire. No real time passes.
func TestReaperClosesIdleConnections(t *testing.T) {
	clk := newFakeClock(epoch)
	p := newWithClock(5, clk)
	defer p.Stop()

	c := &fakeConn{}
	p.Put(c) // idleSince = epoch

	// Advance the clock past the one-minute idle threshold and fire the ticker.
	clk.Advance(61 * time.Second)

	// Give the reaper goroutine a moment to process the ticker event.
	// We use a poll loop with a very short real sleep (microseconds) rather
	// than a fixed sleep, so the test stays fast even on slow machines.
	deadline := time.Now().Add(5 * time.Second)
	for time.Now().Before(deadline) {
		if p.IdleCount() == 0 {
			break
		}
		time.Sleep(time.Millisecond)
	}

	if p.IdleCount() != 0 {
		t.Fatalf("IdleCount after reaper tick: got %d, want 0", p.IdleCount())
	}
	if !c.isClosed() {
		t.Fatal("idle connection was not closed by the reaper")
	}
}

// TestReaperKeepsFreshConnections verifies that connections idle for less than
// one minute are NOT closed by the reaper.
func TestReaperKeepsFreshConnections(t *testing.T) {
	clk := newFakeClock(epoch)
	p := newWithClock(5, clk)
	defer p.Stop()

	c := &fakeConn{}
	p.Put(c) // idleSince = epoch

	// Advance by only 30 seconds — still within the one-minute window.
	clk.Advance(30 * time.Second)

	// Give the reaper goroutine a brief moment to process (it should do nothing).
	deadline := time.Now().Add(100 * time.Millisecond)
	for time.Now().Before(deadline) {
		time.Sleep(time.Millisecond)
	}

	if p.IdleCount() != 1 {
		t.Fatalf("IdleCount after partial advance: got %d, want 1 (fresh connection should be kept)", p.IdleCount())
	}
	if c.isClosed() {
		t.Fatal("fresh connection was incorrectly closed by the reaper")
	}
}

// TestReaperMixedConnections verifies that only stale connections are removed
// when the pool contains a mix of fresh and stale connections.
func TestReaperMixedConnections(t *testing.T) {
	clk := newFakeClock(epoch)
	p := newWithClock(5, clk)
	defer p.Stop()

	stale := &fakeConn{}
	p.Put(stale) // idleSince = epoch

	// Advance 45 seconds, then add a fresh connection.
	clk.Advance(45 * time.Second)
	fresh := &fakeConn{}
	p.Put(fresh) // idleSince = epoch + 45s

	// Advance another 20 seconds: total elapsed = 65s for stale, 20s for fresh.
	clk.Advance(20 * time.Second)

	// The ticker fires; stale is over 60s idle, fresh is only 20s idle.
	deadline := time.Now().Add(5 * time.Second)
	for time.Now().Before(deadline) {
		if p.IdleCount() == 1 {
			break
		}
		time.Sleep(time.Millisecond)
	}

	if p.IdleCount() != 1 {
		t.Fatalf("IdleCount after mixed reaper tick: got %d, want 1", p.IdleCount())
	}
	if !stale.isClosed() {
		t.Fatal("stale connection was not closed by the reaper")
	}
	if fresh.isClosed() {
		t.Fatal("fresh connection was incorrectly closed by the reaper")
	}
}

// TestIdleCountEmptyPool is a basic sanity check.
func TestIdleCountEmptyPool(t *testing.T) {
	clk := newFakeClock(epoch)
	p := newWithClock(5, clk)
	defer p.Stop()

	if got := p.IdleCount(); got != 0 {
		t.Fatalf("IdleCount on new pool: got %d, want 0", got)
	}
}
