package ledger

import "testing"

// Values are distinct and non-default despite the doc example's zeros, so a
// broken Add (ignored ID, ignored amount) cannot pass by coincidence.
func TestAddCreditsTheGivenAccount(t *testing.T) {
	l := New()
	l.Add(7, 250)
	if got := l.Balance(7); got != 250 {
		t.Errorf("Balance(7) = %d, want 250", got)
	}
}

func TestAddDoesNotTouchOtherAccounts(t *testing.T) {
	l := New()
	l.Add(7, 250)
	if got := l.Balance(3); got != 0 {
		t.Errorf("Balance(3) = %d, want 0 (untouched account)", got)
	}
	if got := l.Balance(0); got != 0 {
		t.Errorf("Balance(0) = %d, want 0 (untouched account)", got)
	}
}

func TestAddAccumulates(t *testing.T) {
	l := New()
	l.Add(42, 100)
	l.Add(42, 35)
	if got := l.Balance(42); got != 135 {
		t.Errorf("Balance(42) = %d, want 135", got)
	}
}

func TestBalanceUnknownAccountIsZero(t *testing.T) {
	l := New()
	if got := l.Balance(99); got != 0 {
		t.Errorf("Balance(99) = %d, want 0", got)
	}
}
