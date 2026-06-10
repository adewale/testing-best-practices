package ringbuffer

import (
	"math/rand"
	"testing"
)

// shadowRingBuffer is a deliberately dumb reference implementation that is
// obviously correct. It uses a plain slice and trades performance for clarity,
// serving as the oracle in shadow-model tests.
type shadowRingBuffer struct {
	capacity int
	items    []int
}

func newShadow(capacity int) *shadowRingBuffer {
	return &shadowRingBuffer{capacity: capacity}
}

func (s *shadowRingBuffer) push(v int) {
	s.items = append(s.items, v)
	if len(s.items) > s.capacity {
		// Drop the oldest element to honour fixed-capacity overwrite behaviour.
		s.items = s.items[len(s.items)-s.capacity:]
	}
}

func (s *shadowRingBuffer) pop() (int, bool) {
	if len(s.items) == 0 {
		return 0, false
	}
	v := s.items[0]
	s.items = s.items[1:]
	return v, true
}

func (s *shadowRingBuffer) len() int {
	return len(s.items)
}

func (s *shadowRingBuffer) snapshot() []int {
	out := make([]int, len(s.items))
	copy(out, s.items)
	return out
}

// intSlicesEqual returns true when a and b have the same length and elements.
func intSlicesEqual(a, b []int) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}

// ---------------------------------------------------------------------------
// Shadow-model test: drive both implementations with the same seeded random
// operations and assert they agree on every observable after every operation.
// ---------------------------------------------------------------------------

func TestShadowModel(t *testing.T) {
	const seed = int64(1234)
	const capacity = 8
	const iterations = 10_000

	rng := rand.New(rand.NewSource(seed))
	rb := New(capacity)
	shadow := newShadow(capacity)

	for i := 0; i < iterations; i++ {
		op := rng.Intn(3) // 0=push, 1=pop, 2=snapshot/len check

		switch op {
		case 0, 1: // bias toward pushes (two cases map to push)
			v := rng.Intn(1_000)
			rb.Push(v)
			shadow.push(v)

		case 2:
			// Pop from both and compare return values.
			gotVal, gotOk := rb.Pop()
			wantVal, wantOk := shadow.pop()
			if gotOk != wantOk {
				t.Fatalf("iter %d Pop() ok: got %v, want %v (seed=%d)", i, gotOk, wantOk, seed)
			}
			if gotOk && gotVal != wantVal {
				t.Fatalf("iter %d Pop() value: got %d, want %d (seed=%d)", i, gotVal, wantVal, seed)
			}
		}

		// After every operation, compare all observables.
		if got, want := rb.Len(), shadow.len(); got != want {
			t.Fatalf("iter %d Len(): got %d, want %d (seed=%d)", i, got, want, seed)
		}
		if got, want := rb.Snapshot(), shadow.snapshot(); !intSlicesEqual(got, want) {
			t.Fatalf("iter %d Snapshot(): got %v, want %v (seed=%d)", i, got, want, seed)
		}
	}
}

// ---------------------------------------------------------------------------
// Targeted example tests for specific behaviours.
// ---------------------------------------------------------------------------

// TestNewEmptyBuffer checks that a freshly created buffer is empty.
func TestNewEmptyBuffer(t *testing.T) {
	rb := New(4)
	if rb.Len() != 0 {
		t.Errorf("Len() = %d, want 0", rb.Len())
	}
	snap := rb.Snapshot()
	if len(snap) != 0 {
		t.Errorf("Snapshot() = %v, want []", snap)
	}
}

// TestPopFromEmpty checks that Pop on an empty buffer returns false.
func TestPopFromEmpty(t *testing.T) {
	rb := New(4)
	v, ok := rb.Pop()
	if ok {
		t.Errorf("Pop() ok = true on empty buffer, want false (value %d)", v)
	}
}

// TestPushAndPopOrdering verifies FIFO ordering within capacity.
func TestPushAndPopOrdering(t *testing.T) {
	rb := New(5)
	for _, v := range []int{10, 20, 30} {
		rb.Push(v)
	}
	for _, want := range []int{10, 20, 30} {
		got, ok := rb.Pop()
		if !ok {
			t.Fatalf("Pop() ok = false, want true")
		}
		if got != want {
			t.Errorf("Pop() = %d, want %d", got, want)
		}
	}
	if rb.Len() != 0 {
		t.Errorf("Len() = %d after draining, want 0", rb.Len())
	}
}

// TestOverwriteOldestWhenFull verifies that when Push is called on a full
// buffer the oldest element is dropped and the new element is appended.
func TestOverwriteOldestWhenFull(t *testing.T) {
	rb := New(3)
	rb.Push(1)
	rb.Push(2)
	rb.Push(3) // buffer is now full: [1,2,3]
	rb.Push(4) // should drop 1, giving [2,3,4]

	want := []int{2, 3, 4}
	got := rb.Snapshot()
	if !intSlicesEqual(got, want) {
		t.Errorf("Snapshot() = %v, want %v", got, want)
	}
	if rb.Len() != 3 {
		t.Errorf("Len() = %d, want 3", rb.Len())
	}
}

// TestOverwriteMultipleElements pushes many more elements than the capacity and
// verifies only the most-recent capacity elements remain.
func TestOverwriteMultipleElements(t *testing.T) {
	capacity := 4
	rb := New(capacity)
	for i := 1; i <= 10; i++ {
		rb.Push(i)
	}
	// After pushing 1..10 into capacity-4, the snapshot must be [7,8,9,10].
	want := []int{7, 8, 9, 10}
	got := rb.Snapshot()
	if !intSlicesEqual(got, want) {
		t.Errorf("Snapshot() = %v, want %v", got, want)
	}
	if rb.Len() != capacity {
		t.Errorf("Len() = %d, want %d", rb.Len(), capacity)
	}
}

// TestSnapshotOrder confirms oldest-to-newest ordering in Snapshot.
func TestSnapshotOrder(t *testing.T) {
	rb := New(5)
	rb.Push(100)
	rb.Push(200)
	rb.Push(300)

	snap := rb.Snapshot()
	if len(snap) != 3 {
		t.Fatalf("Snapshot() len = %d, want 3", len(snap))
	}
	if snap[0] != 100 || snap[1] != 200 || snap[2] != 300 {
		t.Errorf("Snapshot() = %v, want [100 200 300]", snap)
	}
}

// TestSnapshotIsolation verifies that mutating the returned snapshot slice
// does not corrupt the ring buffer's internal state.
func TestSnapshotIsolation(t *testing.T) {
	rb := New(4)
	rb.Push(1)
	rb.Push(2)

	snap := rb.Snapshot()
	snap[0] = 999 // mutate the returned slice

	snap2 := rb.Snapshot()
	if snap2[0] != 1 {
		t.Errorf("Snapshot() = %v after external mutation, want first element 1 (snapshot must be a copy)", snap2)
	}
}

// TestLenTracksCorrectly checks that Len returns the right value across
// pushes and pops including the full-buffer overwrite scenario.
func TestLenTracksCorrectly(t *testing.T) {
	rb := New(3)
	if rb.Len() != 0 {
		t.Errorf("initial Len = %d, want 0", rb.Len())
	}
	rb.Push(1)
	if rb.Len() != 1 {
		t.Errorf("Len after 1 push = %d, want 1", rb.Len())
	}
	rb.Push(2)
	rb.Push(3)
	if rb.Len() != 3 {
		t.Errorf("Len after 3 pushes = %d, want 3", rb.Len())
	}
	// Pushing beyond capacity must not increase Len past capacity.
	rb.Push(4)
	if rb.Len() != 3 {
		t.Errorf("Len after overwrite push = %d, want 3", rb.Len())
	}
	rb.Pop()
	if rb.Len() != 2 {
		t.Errorf("Len after pop = %d, want 2", rb.Len())
	}
}

// TestCapacityOne exercises a degenerate ring buffer with capacity 1.
func TestCapacityOne(t *testing.T) {
	rb := New(1)
	rb.Push(42)
	if rb.Len() != 1 {
		t.Errorf("Len() = %d, want 1", rb.Len())
	}
	rb.Push(99) // should overwrite 42
	if rb.Len() != 1 {
		t.Errorf("Len() after overwrite = %d, want 1", rb.Len())
	}
	snap := rb.Snapshot()
	if !intSlicesEqual(snap, []int{99}) {
		t.Errorf("Snapshot() = %v, want [99]", snap)
	}
	v, ok := rb.Pop()
	if !ok || v != 99 {
		t.Errorf("Pop() = (%d, %v), want (99, true)", v, ok)
	}
	if rb.Len() != 0 {
		t.Errorf("Len() after pop = %d, want 0", rb.Len())
	}
}

// TestNegativeValues ensures the buffer handles negative integers correctly.
func TestNegativeValues(t *testing.T) {
	rb := New(3)
	rb.Push(-1)
	rb.Push(-2)
	rb.Push(-3)
	want := []int{-1, -2, -3}
	if got := rb.Snapshot(); !intSlicesEqual(got, want) {
		t.Errorf("Snapshot() = %v, want %v", got, want)
	}
}

// TestZeroValue ensures that zero is a valid element and is distinguishable
// from "not present" via the ok return of Pop.
func TestZeroValue(t *testing.T) {
	rb := New(2)
	rb.Push(0)
	v, ok := rb.Pop()
	if !ok {
		t.Errorf("Pop() ok = false, want true")
	}
	if v != 0 {
		t.Errorf("Pop() = %d, want 0", v)
	}
}

// TestInterleavedPushPop exercises mixed push/pop patterns and verifies the
// shadow model agrees throughout.
func TestInterleavedPushPop(t *testing.T) {
	rb := New(4)
	shadow := newShadow(4)

	ops := []struct {
		push bool
		val  int
	}{
		{true, 1},
		{true, 2},
		{false, 0},
		{true, 3},
		{true, 4},
		{true, 5}, // 5th push with capacity 4: 2,3,4,5 after first pop already happened
		{false, 0},
		{false, 0},
		{true, 6},
		{true, 7},
		{true, 8},
		{false, 0},
	}

	for idx, op := range ops {
		if op.push {
			rb.Push(op.val)
			shadow.push(op.val)
		} else {
			gotVal, gotOk := rb.Pop()
			wantVal, wantOk := shadow.pop()
			if gotOk != wantOk {
				t.Fatalf("op %d Pop() ok: got %v, want %v", idx, gotOk, wantOk)
			}
			if gotOk && gotVal != wantVal {
				t.Fatalf("op %d Pop() value: got %d, want %d", idx, gotVal, wantVal)
			}
		}
		if got, want := rb.Len(), shadow.len(); got != want {
			t.Fatalf("op %d Len(): got %d, want %d", idx, got, want)
		}
		if got, want := rb.Snapshot(), shadow.snapshot(); !intSlicesEqual(got, want) {
			t.Fatalf("op %d Snapshot(): got %v, want %v", idx, got, want)
		}
	}
}

// TestDrainAndRefill verifies that a fully drained buffer can be used again.
func TestDrainAndRefill(t *testing.T) {
	rb := New(3)
	rb.Push(1)
	rb.Push(2)
	rb.Push(3)
	rb.Pop()
	rb.Pop()
	rb.Pop()

	if rb.Len() != 0 {
		t.Fatalf("Len() = %d after full drain, want 0", rb.Len())
	}

	rb.Push(10)
	rb.Push(20)
	want := []int{10, 20}
	got := rb.Snapshot()
	if !intSlicesEqual(got, want) {
		t.Errorf("Snapshot() after refill = %v, want %v", got, want)
	}
}

// TestShadowModelHighContention runs a seed-varied shadow-model pass that
// biases heavily toward the full-buffer overwrite edge case (all pushes,
// rare pops) to maximise eviction coverage.
func TestShadowModelHighContention(t *testing.T) {
	const seed = int64(9999)
	const capacity = 3
	const iterations = 5_000

	rng := rand.New(rand.NewSource(seed))
	rb := New(capacity)
	shadow := newShadow(capacity)

	for i := 0; i < iterations; i++ {
		// 90 % push, 10 % pop — stress the overwrite path.
		if rng.Intn(10) < 9 {
			v := rng.Intn(500)
			rb.Push(v)
			shadow.push(v)
		} else {
			gotVal, gotOk := rb.Pop()
			wantVal, wantOk := shadow.pop()
			if gotOk != wantOk {
				t.Fatalf("iter %d Pop() ok: got %v, want %v (seed=%d)", i, gotOk, wantOk, seed)
			}
			if gotOk && gotVal != wantVal {
				t.Fatalf("iter %d Pop() value: got %d, want %d (seed=%d)", i, gotVal, wantVal, seed)
			}
		}

		if got, want := rb.Len(), shadow.len(); got != want {
			t.Fatalf("iter %d Len(): got %d, want %d (seed=%d)", i, got, want, seed)
		}
		if got, want := rb.Snapshot(), shadow.snapshot(); !intSlicesEqual(got, want) {
			t.Fatalf("iter %d Snapshot(): got %v, want %v (seed=%d)", i, got, want, seed)
		}
	}
}
