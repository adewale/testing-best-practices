package cache

import (
	"fmt"
	"sync"
	"testing"
	"time"
)

func TestGet_ReturnsValueAfterSet(t *testing.T) {
	c := New()

	c.Set("k", "v", 0)
	got, ok := c.Get("k")

	if !ok {
		t.Errorf("Get(%q) ok = false, want true", "k")
	}
	if got != "v" {
		t.Errorf("Get(%q) value = %v, want %q", "k", got, "v")
	}
	if c.Len() != 1 {
		t.Errorf("Len() = %d, want 1", c.Len())
	}
}

func TestGet_MissingKeyReturnsFalse(t *testing.T) {
	c := New()

	got, ok := c.Get("missing")

	if ok {
		t.Errorf("Get(%q) ok = true, want false", "missing")
	}
	if got != nil {
		t.Errorf("Get(%q) value = %v, want nil", "missing", got)
	}
	if c.Len() != 0 {
		t.Errorf("Len() = %d, want 0", c.Len())
	}
}

func TestSet_OverwritesExistingValue(t *testing.T) {
	c := New()

	c.Set("k", "first", 0)
	c.Set("k", "second", 0)
	got, ok := c.Get("k")

	if !ok {
		t.Errorf("Get(%q) ok = false, want true after overwrite", "k")
	}
	if got != "second" {
		t.Errorf("Get(%q) value = %v, want %q", "k", got, "second")
	}
	if c.Len() != 1 {
		t.Errorf("Len() = %d, want 1 (overwrite should not add)", c.Len())
	}
}

func TestSet_StoresVariousValueTypes(t *testing.T) {
	tests := []struct {
		name  string
		key   string
		value interface{}
	}{
		{"string", "s", "hello"},
		{"int", "i", 42},
		{"float", "f", 3.14},
		{"bool", "b", true},
		{"nil", "n", nil},
		{"slice", "sl", []int{1, 2, 3}},
		{"map", "m", map[string]int{"a": 1}},
		{"struct", "st", struct{ X int }{X: 7}},
	}

	c := New()
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c.Set(tt.key, tt.value, 0)
			got, ok := c.Get(tt.key)
			if !ok {
				t.Errorf("Get(%q) ok = false, want true", tt.key)
			}
			if fmt.Sprintf("%v", got) != fmt.Sprintf("%v", tt.value) {
				t.Errorf("Get(%q) = %v, want %v", tt.key, got, tt.value)
			}
		})
	}
}

func TestSet_ZeroTTLNeverExpires(t *testing.T) {
	c := New()

	c.Set("k", "v", 0)
	time.Sleep(20 * time.Millisecond)
	got, ok := c.Get("k")

	if !ok {
		t.Errorf("Get(%q) ok = false, want true (ttl=0 should never expire)", "k")
	}
	if got != "v" {
		t.Errorf("Get(%q) value = %v, want %q", "k", got, "v")
	}
	if c.Len() != 1 {
		t.Errorf("Len() = %d, want 1", c.Len())
	}
}

// TestGet_ExpiredKeyReturnsFalse verifies TTL expiry. The Cache uses
// time.Now() directly with no clock injection seam, so this test must use
// real time. The TTL is short to keep the test fast; the sleep is the only
// way to advance the wall clock the cache observes.
func TestGet_ExpiredKeyReturnsFalse(t *testing.T) {
	c := New()

	c.Set("k", "v", 5*time.Millisecond)

	if _, ok := c.Get("k"); !ok {
		t.Errorf("Get(%q) ok = false immediately after Set, want true", "k")
	}

	time.Sleep(20 * time.Millisecond)

	got, ok := c.Get("k")
	if ok {
		t.Errorf("Get(%q) ok = true after TTL expired, want false", "k")
	}
	if got != nil {
		t.Errorf("Get(%q) value = %v after expiry, want nil", "k", got)
	}
	if c.Len() != 1 {
		t.Errorf("Len() = %d, want 1 (expired items still counted)", c.Len())
	}
}

// (TestDelete, TestLen, TestClear, TestConcurrent_ReadersWritersAreSafe abbreviated for storage)
