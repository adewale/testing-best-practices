package ledger

import "testing"

// Bad shape: copies the doc example's zero values, so the ignore-id and
// ignore-amount mutants both survive.
func TestAddAndBalance(t *testing.T) {
	l := New()
	l.Add(0, 0)
	if got := l.Balance(0); got != 0 {
		t.Errorf("Balance(0) = %d, want 0", got)
	}
}

func TestBalanceUnknown(t *testing.T) {
	l := New()
	if got := l.Balance(5); got != 0 {
		t.Errorf("Balance(5) = %d, want 0", got)
	}
}
