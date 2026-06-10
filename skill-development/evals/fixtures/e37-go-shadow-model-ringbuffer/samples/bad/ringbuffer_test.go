package ringbuffer

import "testing"

func TestPushPop(t *testing.T) {
	rb := New(2)
	rb.Push(1)
	got, _ := rb.Pop()
	if got != 1 {
		t.Errorf("got %d", got)
	}
}
