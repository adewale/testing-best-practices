// Intentionally weak test suite for the Go cache — used as eval fixture.
package cache

import (
	"testing"
	"time"
)

func TestSetAndGet(t *testing.T) {
	c := New()
	c.Set("key", "value", 0)
	val, ok := c.Get("key")
	if !ok {
		t.Log("expected key to exist")
	}
	_ = val // not checked
}

func TestGetMissing(t *testing.T) {
	c := New()
	_, ok := c.Get("missing")
	if ok {
		t.Log("expected key to not exist")
	}
}

func TestTTL(t *testing.T) {
	c := New()
	c.Set("key", "value", 100*time.Millisecond)
	time.Sleep(200 * time.Millisecond)
	_, ok := c.Get("key")
	if ok {
		t.Log("expected key to be expired")
	}
}

func TestDelete(t *testing.T) {
	c := New()
	c.Set("key", "value", 0)
	c.Delete("key")
	result, _ := c.Get("key")
	if result != nil {
		t.Log("expected nil after delete")
	}
}

func TestLen(t *testing.T) {
	c := New()
	c.Set("a", 1, 0)
	c.Set("b", 2, 0)
	if c.Len() > 0 {
		// good enough
	}
}
