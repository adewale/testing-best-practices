package metrics

import (
	"testing"
	"time"
)

func TestTotals(t *testing.T) {
	a := NewAggregator()
	for i := 0; i < 1000; i++ {
		a.Record("requests", 1)
	}
	time.Sleep(100 * time.Millisecond) // hope the goroutine drained
	if got := a.Total("requests"); got != 1000 {
		t.Errorf("Total = %v", got)
	}
}
