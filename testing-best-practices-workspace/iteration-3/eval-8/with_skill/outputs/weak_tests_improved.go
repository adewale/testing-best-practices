package cache

import (
	"fmt"
	"sync"
	"testing"
	"time"
)

// --- helpers ---

func assertGet(t *testing.T, c *Cache, key string, wantVal interface{}, wantOK bool) {
	t.Helper()
	got, ok := c.Get(key)
	if ok != wantOK {
		t.Errorf("Get(%q) ok = %v, want %v", key, ok, wantOK)
	}
	if got != wantVal {
		t.Errorf("Get(%q) value = %v, want %v", key, got, wantVal)
	}
}

// --- Core CRUD ---

func TestSetAndGet(t *testing.T) {
	tests := []struct {
		name  string
		key   string
		value interface{}
	}{
		{"string value", "greeting", "hello"},
		{"int value", "count", 42},
		{"nil value", "nothing", nil},
		{"empty key", "", "empty-key-value"},
		{"struct value", "point", struct{ X, Y int }{1, 2}},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := New()
			c.Set(tt.key, tt.value, 0)

			got, ok := c.Get(tt.key)
			if !ok {
				t.Fatalf("Get(%q) returned ok=false, expected key to exist", tt.key)
			}
			if got != tt.value {
				t.Errorf("Get(%q) = %v (%T), want %v (%T)", tt.key, got, got, tt.value, tt.value)
			}
		})
	}
}

func TestGetMissing(t *testing.T) {
	c := New()

	val, ok := c.Get("nonexistent")
	if ok {
		t.Errorf("Get(nonexistent) ok = true, want false")
	}
	if val != nil {
		t.Errorf("Get(nonexistent) value = %v, want nil", val)
	}
}

func TestSetOverwritesExistingKey(t *testing.T) {
	c := New()
	c.Set("key", "first", 0)
	c.Set("key", "second", 0)

	got, ok := c.Get("key")
	if !ok {
		t.Fatalf("Get(key) ok = false after overwrite")
	}
	if got != "second" {
		t.Errorf("Get(key) = %v, want %q after overwrite", got, "second")
	}
	if c.Len() != 1 {
		t.Errorf("Len() = %d, want 1 after overwrite (not 2)", c.Len())
	}
}

func TestDelete(t *testing.T) {
	c := New()
	c.Set("key", "value", 0)
	c.Delete("key")

	val, ok := c.Get("key")
	if ok {
		t.Errorf("Get(key) ok = true after Delete, want false")
	}
	if val != nil {
		t.Errorf("Get(key) = %v after Delete, want nil", val)
	}
	if c.Len() != 0 {
		t.Errorf("Len() = %d after Delete, want 0", c.Len())
	}
}

func TestDeleteNonexistentKeyDoesNotPanic(t *testing.T) {
	c := New()
	// Should not panic
	c.Delete("never-set")

	if c.Len() != 0 {
		t.Errorf("Len() = %d after deleting nonexistent key, want 0", c.Len())
	}
}

// --- Len ---

func TestLen(t *testing.T) {
	c := New()
	if c.Len() != 0 {
		t.Errorf("new cache Len() = %d, want 0", c.Len())
	}

	c.Set("a", 1, 0)
	if c.Len() != 1 {
		t.Errorf("Len() after 1 Set = %d, want 1", c.Len())
	}

	c.Set("b", 2, 0)
	if c.Len() != 2 {
		t.Errorf("Len() after 2 Sets = %d, want 2", c.Len())
	}

	c.Delete("a")
	if c.Len() != 1 {
		t.Errorf("Len() after Delete = %d, want 1", c.Len())
	}
}

// --- Clear ---

func TestClear(t *testing.T) {
	c := New()
	c.Set("a", 1, 0)
	c.Set("b", 2, 0)
	c.Set("c", 3, 0)

	c.Clear()

	if c.Len() != 0 {
		t.Errorf("Len() after Clear = %d, want 0", c.Len())
	}

	// Verify individual keys are gone
	for _, key := range []string{"a", "b", "c"} {
		val, ok := c.Get(key)
		if ok {
			t.Errorf("Get(%q) ok = true after Clear, want false", key)
		}
		if val != nil {
			t.Errorf("Get(%q) = %v after Clear, want nil", key, val)
		}
	}

	// Verify cache is still usable after Clear
	c.Set("d", 4, 0)
	got, ok := c.Get("d")
	if !ok || got != 4 {
		t.Errorf("cache not usable after Clear: Get(d) = (%v, %v), want (4, true)", got, ok)
	}
}

func TestClearOnEmptyCache(t *testing.T) {
	c := New()
	// Should not panic
	c.Clear()
	if c.Len() != 0 {
		t.Errorf("Len() after Clear on empty cache = %d, want 0", c.Len())
	}
}

// --- TTL ---

func TestTTLExpiry(t *testing.T) {
	c := New()
	c.Set("ephemeral", "gone-soon", 50*time.Millisecond)

	// Should exist immediately
	val, ok := c.Get("ephemeral")
	if !ok {
		t.Fatalf("Get(ephemeral) ok = false immediately after Set")
	}
	if val != "gone-soon" {
		t.Errorf("Get(ephemeral) = %v, want %q", val, "gone-soon")
	}

	// Wait for expiry
	time.Sleep(100 * time.Millisecond)

	val, ok = c.Get("ephemeral")
	if ok {
		t.Errorf("Get(ephemeral) ok = true after TTL expired, want false")
	}
	if val != nil {
		t.Errorf("Get(ephemeral) = %v after TTL expired, want nil", val)
	}
}

func TestTTLZeroNeverExpires(t *testing.T) {
	c := New()
	c.Set("permanent", "forever", 0)

	// Small sleep to confirm zero-TTL items do not expire
	time.Sleep(50 * time.Millisecond)

	val, ok := c.Get("permanent")
	if !ok {
		t.Fatalf("Get(permanent) ok = false, zero-TTL items should never expire")
	}
	if val != "forever" {
		t.Errorf("Get(permanent) = %v, want %q", val, "forever")
	}
}

func TestExpiredItemStillCountedByLen(t *testing.T) {
	// Len() docs say it includes expired items
	c := New()
	c.Set("temp", "x", 50*time.Millisecond)

	time.Sleep(100 * time.Millisecond)

	// Item is expired but Len should still count it (per implementation)
	if c.Len() != 1 {
		t.Errorf("Len() = %d for expired-but-not-purged item, want 1", c.Len())
	}

	// But Get should not return it
	_, ok := c.Get("temp")
	if ok {
		t.Errorf("Get(temp) ok = true for expired item, want false")
	}
}

func TestSetNewTTLOnExistingKey(t *testing.T) {
	c := New()
	c.Set("key", "v1", 50*time.Millisecond)
	// Overwrite with no TTL
	c.Set("key", "v2", 0)

	time.Sleep(100 * time.Millisecond)

	// Should still exist because second Set used ttl=0
	val, ok := c.Get("key")
	if !ok {
		t.Fatalf("Get(key) ok = false, want true (TTL was reset to 0)")
	}
	if val != "v2" {
		t.Errorf("Get(key) = %v, want %q", val, "v2")
	}
}

// --- Concurrency ---

func TestConcurrentSetAndGet(t *testing.T) {
	c := New()
	const goroutines = 50
	const opsPerGoroutine = 100

	var wg sync.WaitGroup
	wg.Add(goroutines)

	for i := 0; i < goroutines; i++ {
		go func(id int) {
			defer wg.Done()
			key := fmt.Sprintf("key-%d", id)
			for j := 0; j < opsPerGoroutine; j++ {
				c.Set(key, j, 0)
				c.Get(key)
			}
		}(i)
	}

	wg.Wait()

	// After all goroutines complete, each key should hold its last-written value
	for i := 0; i < goroutines; i++ {
		key := fmt.Sprintf("key-%d", i)
		val, ok := c.Get(key)
		if !ok {
			t.Errorf("Get(%q) ok = false after concurrent writes", key)
			continue
		}
		if val != opsPerGoroutine-1 {
			t.Errorf("Get(%q) = %v, want %d", key, val, opsPerGoroutine-1)
		}
	}
}

func TestConcurrentDeleteAndGet(t *testing.T) {
	c := New()
	c.Set("shared", "value", 0)

	var wg sync.WaitGroup
	wg.Add(2)

	// One goroutine reads repeatedly
	go func() {
		defer wg.Done()
		for i := 0; i < 1000; i++ {
			c.Get("shared")
		}
	}()

	// Another goroutine deletes and re-sets
	go func() {
		defer wg.Done()
		for i := 0; i < 1000; i++ {
			c.Delete("shared")
			c.Set("shared", "value", 0)
		}
	}()

	wg.Wait()
	// No data race should occur (run with -race flag to verify)
}

// --- Multiple items ---

func TestMultipleKeys(t *testing.T) {
	c := New()
	items := map[string]interface{}{
		"str":  "hello",
		"num":  42,
		"bool": true,
	}

	for k, v := range items {
		c.Set(k, v, 0)
	}

	if c.Len() != len(items) {
		t.Errorf("Len() = %d, want %d", c.Len(), len(items))
	}

	for k, want := range items {
		got, ok := c.Get(k)
		if !ok {
			t.Errorf("Get(%q) ok = false, want true", k)
			continue
		}
		if got != want {
			t.Errorf("Get(%q) = %v, want %v", k, got, want)
		}
	}
}
