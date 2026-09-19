package kvstore

import "testing"

// Values are distinct and non-default per parameter so a broken Put (dropped
// value, swapped arguments) cannot pass by coincidence.
func TestPutThenGetReturnsStoredValue(t *testing.T) {
	s := New()
	s.Put("user:1", "alice")
	got, ok := s.Get("user:1")
	if !ok {
		t.Fatalf("Get(%q) reported absent after Put", "user:1")
	}
	if got != "alice" {
		t.Errorf("Get(%q) = %q, want %q", "user:1", got, "alice")
	}
}

func TestPutReplacesExistingValue(t *testing.T) {
	s := New()
	s.Put("user:1", "alice")
	s.Put("user:1", "bob")
	got, ok := s.Get("user:1")
	if !ok || got != "bob" {
		t.Errorf("Get(%q) = %q, %v, want %q, true", "user:1", got, ok, "bob")
	}
}

func TestGetAbsentKey(t *testing.T) {
	s := New()
	got, ok := s.Get("missing")
	if ok || got != "" {
		t.Errorf("Get(%q) = %q, %v, want \"\", false", "missing", got, ok)
	}
}

func TestDeleteRemovesKey(t *testing.T) {
	s := New()
	s.Put("session:9", "token-xyz")
	s.Delete("session:9")
	if _, ok := s.Get("session:9"); ok {
		t.Errorf("Get(%q) reported present after Delete", "session:9")
	}
}

func TestDeleteAbsentKeyIsNoOp(t *testing.T) {
	s := New()
	s.Put("keep", "kept-value")
	s.Delete("not-there")
	got, ok := s.Get("keep")
	if !ok || got != "kept-value" {
		t.Errorf("Delete of absent key disturbed other entries: got %q, %v", got, ok)
	}
}
