package ringbuffer

import (
	"math/rand"
	"reflect"
	"testing"
)

func TestRingBufferMatchesShadowModel(t *testing.T) {
	rng := rand.New(rand.NewSource(1234)) // seed: failures replay exactly
	rb := New(8)
	var model []int // trivial slice-backed "always tells the truth" model
	for i := 0; i < 5000; i++ {
		if rng.Float64() < 0.7 {
			v := rng.Intn(1000)
			rb.Push(v)
			model = append(model, v)
			if len(model) > 8 {
				model = model[1:]
			}
		} else if len(model) > 0 {
			got, _ := rb.Pop()
			want := model[0]
			model = model[1:]
			if got != want {
				t.Fatalf("pop mismatch: got %d want %d", got, want)
			}
		}
		if rb.Len() != len(model) {
			t.Fatalf("len mismatch: got %d want %d", rb.Len(), len(model))
		}
	}
	if !reflect.DeepEqual(rb.Snapshot(), model) {
		t.Fatalf("contents mismatch: %v vs %v", rb.Snapshot(), model)
	}
}
