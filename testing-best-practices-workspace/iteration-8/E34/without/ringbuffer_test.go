package ringbuffer

import (
	"testing"
)

// referenceRingBuffer is a simple, obviously-correct slice-based ring buffer
// used as the oracle for differential testing.
type referenceRingBuffer struct {
	capacity int
	data     []int
}

func newReference(capacity int) *referenceRingBuffer {
	return &referenceRingBuffer{capacity: capacity}
}

func (r *referenceRingBuffer) push(v int) {
	if len(r.data) == r.capacity {
		r.data = r.data[1:] // drop oldest
	}
	r.data = append(r.data, v)
}

func (r *referenceRingBuffer) pop() (int, bool) {
	if len(r.data) == 0 {
		return 0, false
	}
	v := r.data[0]
	r.data = r.data[1:]
	return v, true
}

func (r *referenceRingBuffer) len() int {
	return len(r.data)
}

func (r *referenceRingBuffer) snapshot() []int {
	out := make([]int, len(r.data))
	copy(out, r.data)
	return out
}

// conformanceCase describes a sequence of operations and the expected
// observable state after each operation. This serves as the pirate-style
// shared specification.
type op struct {
	kind  string // "push", "pop", "len", "snapshot"
	value int    // used by push
}

// applyOps drives both the real and reference implementations through the
// same sequence and compares results at each step.
func applyOps(t *testing.T, capacity int, ops []op) {
	t.Helper()
	real := New(capacity)
	ref := newReference(capacity)

	for i, o := range ops {
		switch o.kind {
		case "push":
			real.Push(o.value)
			ref.push(o.value)
		case "pop":
			rv, rok := real.Pop()
			ev, eok := ref.pop()
			if rok != eok {
				t.Errorf("op[%d] Pop() ok mismatch: got %v, want %v", i, rok, eok)
			}
			if rok && rv != ev {
				t.Errorf("op[%d] Pop() value mismatch: got %d, want %d", i, rv, ev)
			}
		case "len":
			rl := real.Len()
			el := ref.len()
			if rl != el {
				t.Errorf("op[%d] Len() mismatch: got %d, want %d", i, rl, el)
			}
		case "snapshot":
			rs := real.Snapshot()
			es := ref.snapshot()
			if len(rs) != len(es) {
				t.Errorf("op[%d] Snapshot() length mismatch: got %d, want %d", i, len(rs), len(es))
				break
			}
			for j := range es {
				if rs[j] != es[j] {
					t.Errorf("op[%d] Snapshot()[%d] mismatch: got %d, want %d", i, j, rs[j], es[j])
				}
			}
		}
	}
}

// checkState is a helper that asserts Len and Snapshot agree with the reference.
func checkState(t *testing.T, label string, real *RingBuffer, ref *referenceRingBuffer) {
	t.Helper()
	if got, want := real.Len(), ref.len(); got != want {
		t.Errorf("%s: Len() = %d, want %d", label, got, want)
	}
	rs := real.Snapshot()
	es := ref.snapshot()
	if len(rs) != len(es) {
		t.Errorf("%s: Snapshot() length = %d, want %d", label, len(rs), len(es))
		return
	}
	for i := range es {
		if rs[i] != es[i] {
			t.Errorf("%s: Snapshot()[%d] = %d, want %d", label, i, rs[i], es[i])
		}
	}
}

// --- Data-driven conformance suite (pirate testing style) ---

// conformanceOpsTable drives both implementations through identical sequences.
var conformanceOpsTable = []struct {
	name     string
	capacity int
	ops      []op
}{
	{
		name:     "empty buffer has zero len",
		capacity: 4,
		ops:      []op{{kind: "len"}},
	},
	{
		name:     "single push then pop",
		capacity: 4,
		ops: []op{
			{kind: "push", value: 42},
			{kind: "len"},
			{kind: "pop"},
			{kind: "len"},
		},
	},
	{
		name:     "pop from empty returns false",
		capacity: 4,
		ops:      []op{{kind: "pop"}},
	},
	{
		name:     "fill to capacity",
		capacity: 3,
		ops: []op{
			{kind: "push", value: 1},
			{kind: "push", value: 2},
			{kind: "push", value: 3},
			{kind: "len"},
			{kind: "snapshot"},
		},
	},
	{
		name:     "overflow wraps oldest",
		capacity: 3,
		ops: []op{
			{kind: "push", value: 1},
			{kind: "push", value: 2},
			{kind: "push", value: 3},
			{kind: "push", value: 4}, // 1 is dropped
			{kind: "len"},
			{kind: "snapshot"},
		},
	},
	{
		name:     "overflow by two elements",
		capacity: 3,
		ops: []op{
			{kind: "push", value: 10},
			{kind: "push", value: 20},
			{kind: "push", value: 30},
			{kind: "push", value: 40}, // 10 dropped
			{kind: "push", value: 50}, // 20 dropped
			{kind: "len"},
			{kind: "snapshot"},
		},
	},
	{
		name:     "push pop interleaved",
		capacity: 4,
		ops: []op{
			{kind: "push", value: 1},
			{kind: "push", value: 2},
			{kind: "pop"},
			{kind: "push", value: 3},
			{kind: "pop"},
			{kind: "push", value: 4},
			{kind: "len"},
			{kind: "snapshot"},
		},
	},
	{
		name:     "drain buffer to empty",
		capacity: 3,
		ops: []op{
			{kind: "push", value: 7},
			{kind: "push", value: 8},
			{kind: "push", value: 9},
			{kind: "pop"},
			{kind: "pop"},
			{kind: "pop"},
			{kind: "len"},
			{kind: "pop"}, // empty pop
		},
	},
	{
		name:     "snapshot order is oldest to newest",
		capacity: 5,
		ops: []op{
			{kind: "push", value: 100},
			{kind: "push", value: 200},
			{kind: "push", value: 300},
			{kind: "snapshot"},
		},
	},
	{
		name:     "snapshot after overflow preserves order",
		capacity: 3,
		ops: []op{
			{kind: "push", value: 1},
			{kind: "push", value: 2},
			{kind: "push", value: 3},
			{kind: "push", value: 4},
			{kind: "push", value: 5},
			{kind: "snapshot"},
		},
	},
	{
		name:     "capacity 1 always holds last value",
		capacity: 1,
		ops: []op{
			{kind: "push", value: 1},
			{kind: "push", value: 2},
			{kind: "push", value: 3},
			{kind: "len"},
			{kind: "snapshot"},
			{kind: "pop"},
			{kind: "len"},
		},
	},
	{
		name:     "large sequence with many overwrites",
		capacity: 4,
		ops: func() []op {
			ops := make([]op, 0, 24)
			for i := 1; i <= 20; i++ {
				ops = append(ops, op{kind: "push", value: i})
			}
			ops = append(ops, op{kind: "len"})
			ops = append(ops, op{kind: "snapshot"})
			return ops
		}(),
	},
}

func TestConformance(t *testing.T) {
	for _, tc := range conformanceOpsTable {
		t.Run(tc.name, func(t *testing.T) {
			applyOps(t, tc.capacity, tc.ops)
		})
	}
}

// --- Differential tests: direct state comparison against reference ---

func TestDifferential_PushPopRoundtrip(t *testing.T) {
	// Round-trip: push N items, pop them all, each value must match in FIFO order.
	capacity := 8
	values := []int{3, 1, 4, 1, 5, 9, 2, 6}

	real := New(capacity)
	ref := newReference(capacity)

	for _, v := range values {
		real.Push(v)
		ref.push(v)
	}
	checkState(t, "after pushes", real, ref)

	for i := range values {
		rv, rok := real.Pop()
		ev, eok := ref.pop()
		if rok != eok {
			t.Fatalf("pop[%d] ok: got %v want %v", i, rok, eok)
		}
		if rv != ev {
			t.Errorf("pop[%d] value: got %d want %d", i, rv, ev)
		}
	}
	checkState(t, "after pops", real, ref)
}

func TestDifferential_OverwriteBehavior(t *testing.T) {
	// Push more than capacity; reference oracle determines correct remaining contents.
	capacity := 5
	real := New(capacity)
	ref := newReference(capacity)

	for i := 1; i <= 12; i++ {
		real.Push(i)
		ref.push(i)
		checkState(t, "after each push", real, ref)
	}
}

func TestDifferential_MixedOpsAgainstReference(t *testing.T) {
	// Interleave pushes and pops in a pattern that stresses the internal pointer math.
	capacity := 4
	real := New(capacity)
	ref := newReference(capacity)

	sequence := []struct {
		kind  string
		value int
	}{
		{"push", 10}, {"push", 20}, {"push", 30},
		{"pop", 0}, {"pop", 0},
		{"push", 40}, {"push", 50}, {"push", 60},
		{"push", 70}, // overflow: 30 was oldest after two pops; 40 gets dropped now
		{"pop", 0},
		{"push", 80}, {"push", 90},
		{"pop", 0}, {"pop", 0}, {"pop", 0},
		{"push", 100},
	}

	for i, s := range sequence {
		if s.kind == "push" {
			real.Push(s.value)
			ref.push(s.value)
		} else {
			rv, rok := real.Pop()
			ev, eok := ref.pop()
			if rok != eok {
				t.Errorf("step[%d] Pop() ok: got %v want %v", i, rok, eok)
			}
			if rok && rv != ev {
				t.Errorf("step[%d] Pop() value: got %d want %d", i, rv, ev)
			}
		}
		checkState(t, "after step", real, ref)
	}
}

// --- Snapshot isolation test ---

func TestSnapshot_DoesNotAliasInternalState(t *testing.T) {
	// Mutating the returned snapshot must not affect the buffer.
	rb := New(4)
	rb.Push(1)
	rb.Push(2)
	rb.Push(3)

	snap := rb.Snapshot()
	if len(snap) == 0 {
		t.Fatal("expected non-empty snapshot")
	}
	// Mutate the snapshot.
	for i := range snap {
		snap[i] = 9999
	}

	// Buffer state must be unchanged.
	snap2 := rb.Snapshot()
	ref := newReference(4)
	ref.push(1)
	ref.push(2)
	ref.push(3)
	expected := ref.snapshot()
	if len(snap2) != len(expected) {
		t.Fatalf("Snapshot() length after mutation: got %d want %d", len(snap2), len(expected))
	}
	for i := range expected {
		if snap2[i] != expected[i] {
			t.Errorf("Snapshot()[%d] after mutation: got %d want %d", i, snap2[i], expected[i])
		}
	}
}

// --- Edge case: capacity 2 stress ---

func TestDifferential_CapacityTwo(t *testing.T) {
	real := New(2)
	ref := newReference(2)

	for i := 1; i <= 10; i++ {
		real.Push(i)
		ref.push(i)
		checkState(t, "push", real, ref)
	}
	for {
		rv, rok := real.Pop()
		ev, eok := ref.pop()
		if rok != eok {
			t.Fatalf("Pop() ok mismatch: got %v want %v", rok, eok)
		}
		if !eok {
			break
		}
		if rv != ev {
			t.Errorf("Pop() value: got %d want %d", rv, ev)
		}
	}
	checkState(t, "drained", real, ref)
}

// --- Len consistency with Snapshot ---

func TestLen_MatchesSnapshotLength(t *testing.T) {
	cases := []struct {
		capacity int
		pushes   []int
		pops     int
	}{
		{4, []int{}, 0},
		{4, []int{1, 2, 3}, 0},
		{4, []int{1, 2, 3, 4}, 0},
		{4, []int{1, 2, 3, 4, 5}, 0}, // overflow
		{4, []int{1, 2, 3}, 2},
		{2, []int{10, 20, 30, 40}, 1},
	}

	for _, tc := range cases {
		rb := New(tc.capacity)
		for _, v := range tc.pushes {
			rb.Push(v)
		}
		for i := 0; i < tc.pops; i++ {
			rb.Pop()
		}
		if got, want := rb.Len(), len(rb.Snapshot()); got != want {
			t.Errorf("capacity=%d pushes=%v pops=%d: Len()=%d but len(Snapshot())=%d",
				tc.capacity, tc.pushes, tc.pops, got, want)
		}
	}
}

// --- Negative values and zero ---

func TestDifferential_NegativeAndZeroValues(t *testing.T) {
	capacity := 4
	real := New(capacity)
	ref := newReference(capacity)

	values := []int{0, -1, -100, 0, 42, -42}
	for _, v := range values {
		real.Push(v)
		ref.push(v)
	}
	checkState(t, "mixed values", real, ref)

	for {
		rv, rok := real.Pop()
		ev, eok := ref.pop()
		if rok != eok {
			t.Fatalf("Pop() ok mismatch")
		}
		if !eok {
			break
		}
		if rv != ev {
			t.Errorf("Pop() value: got %d want %d", rv, ev)
		}
	}
}
