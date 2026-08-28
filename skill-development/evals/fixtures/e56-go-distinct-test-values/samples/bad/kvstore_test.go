package kvstore

import "testing"

// Bad shape: key and value are the same string, and the delete test stores
// the zero value. Both seeded Put mutants survive this suite.
func TestPutGet(t *testing.T) {
	s := New()
	s.Put("a", "a")
	got, ok := s.Get("a")
	if !ok || got != "a" {
		t.Errorf("Get(\"a\") = %q, %v, want \"a\", true", got, ok)
	}
}

func TestGetMissing(t *testing.T) {
	s := New()
	if _, ok := s.Get("missing"); ok {
		t.Error("Get on empty store reported a value")
	}
}

func TestDelete(t *testing.T) {
	s := New()
	s.Put("k", "")
	s.Delete("k")
	if _, ok := s.Get("k"); ok {
		t.Error("Get reported present after Delete")
	}
}
