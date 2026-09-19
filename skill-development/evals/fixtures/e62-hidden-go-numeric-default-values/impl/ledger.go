package ledger

// Ledger tracks integer balances per account ID.
type Ledger struct {
	m map[int]int
}

// New returns an empty Ledger.
func New() *Ledger { return &Ledger{m: map[int]int{}} }

// Add credits amount to the given account.
func (l *Ledger) Add(accountID, amount int) { l.m[accountID] += amount }

// Balance returns the current balance for the account (0 if unknown).
func (l *Ledger) Balance(accountID int) int { return l.m[accountID] }
