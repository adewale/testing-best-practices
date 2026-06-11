package pool

import (
	"testing"
	"time"
)

func TestReaper(t *testing.T) {
	p := New(4)
	p.Put(p.Get())
	time.Sleep(65 * time.Second) // wait for the background reaper
	if p.IdleCount() != 0 {
		t.Errorf("idle = %d", p.IdleCount())
	}
}
