// Package payment is a small payment service. Two operations with
// primitive-typed parameters and heavy runtime validation that could be
// lifted into named types with smart constructors.
package payment

import (
	"errors"
	"strings"
)

type Payment struct {
	UserID      int
	AmountCents int64
	Currency    string
}

// ProcessPayment validates inputs and returns a Payment.
func ProcessPayment(userID int, amountCents int64, currency string) (*Payment, error) {
	if userID <= 0 {
		return nil, errors.New("userID must be positive")
	}
	if amountCents <= 0 {
		return nil, errors.New("amount must be positive")
	}
	if amountCents > 1_000_000_000 {
		return nil, errors.New("amount exceeds max")
	}
	currency = strings.ToUpper(strings.TrimSpace(currency))
	if currency == "" {
		return nil, errors.New("currency required")
	}
	if currency != "USD" && currency != "EUR" && currency != "GBP" {
		return nil, errors.New("unsupported currency")
	}
	return &Payment{UserID: userID, AmountCents: amountCents, Currency: currency}, nil
}

// RefundPayment processes a partial or full refund.
func RefundPayment(p *Payment, refundCents int64) (*Payment, error) {
	if p == nil {
		return nil, errors.New("payment required")
	}
	if refundCents <= 0 {
		return nil, errors.New("refund must be positive")
	}
	if refundCents > p.AmountCents {
		return nil, errors.New("refund exceeds payment amount")
	}
	if p.Currency != "USD" && p.Currency != "EUR" && p.Currency != "GBP" {
		return nil, errors.New("payment has unsupported currency")
	}
	return &Payment{
		UserID:      p.UserID,
		AmountCents: p.AmountCents - refundCents,
		Currency:    p.Currency,
	}, nil
}
