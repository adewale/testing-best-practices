# E62 — Write: unit tests for a per-account ledger

Write unit tests for this Go package. Put your tests in `ledger_test.go`
using `package ledger` (internal test package), following standard Go testing
conventions. Cover the behavior of `Add` and `Balance`.

`ledger.go`:

```go
package ledger

// Ledger tracks integer balances per account ID.
//
// Example:
//
//	l := New()
//	l.Add(0, 0)        // account 0, zero credit
//	_ = l.Balance(0)   // -> 0
type Ledger struct {
	m map[int]int
}

// New returns an empty Ledger.
func New() *Ledger { return &Ledger{m: map[int]int{}} }

// Add credits amount to the given account.
func (l *Ledger) Add(accountID, amount int) { l.m[accountID] += amount }

// Balance returns the current balance for the account (0 if unknown).
func (l *Ledger) Balance(accountID int) int { return l.m[accountID] }
```

The deliverable is the `ledger_test.go` file.
