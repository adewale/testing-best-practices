// Package order models a simple order state machine. The struct
// allows constructing combinations the business rules forbid:
// status=Paid with items=[] is unrepresentable in the domain but
// fully constructible in Go. This is the perfect fixture for
// tactic-B (model-gap) testing — the challenge is to recognise
// that the zero value and arbitrary field combinations defeat
// the invariant, and to add the constructor that makes the
// model honest.
package order

import "errors"

type Status int

const (
	StatusDraft Status = iota
	StatusSubmitted
	StatusPaid
	StatusCancelled
)

type Item struct {
	SKU      string
	Quantity int
}

type Order struct {
	ID     string
	Status Status
	Items  []Item
}

// Submit transitions Draft -> Submitted. Re-validates that items
// exist, which the type system did not prevent at construction.
func (o *Order) Submit() error {
	if o.Status != StatusDraft {
		return errors.New("can only submit from Draft")
	}
	if len(o.Items) == 0 {
		return errors.New("cannot submit order with no items")
	}
	o.Status = StatusSubmitted
	return nil
}

// Pay transitions Submitted -> Paid. Re-validates items
// (defensive, in case Items was mutated after Submit).
func (o *Order) Pay() error {
	if o.Status != StatusSubmitted {
		return errors.New("can only pay from Submitted")
	}
	if len(o.Items) == 0 {
		return errors.New("cannot pay order with no items")
	}
	o.Status = StatusPaid
	return nil
}

// Cancel transitions any non-Paid status to Cancelled.
func (o *Order) Cancel() error {
	if o.Status == StatusPaid {
		return errors.New("cannot cancel paid order")
	}
	o.Status = StatusCancelled
	return nil
}

// Total returns the order total. Silently returns 0 for invalid items.
func (o *Order) Total(pricer func(sku string) int) int {
	total := 0
	for _, item := range o.Items {
		if item.Quantity < 0 {
			continue // silent fallback for bad data
		}
		total += pricer(item.SKU) * item.Quantity
	}
	return total
}
