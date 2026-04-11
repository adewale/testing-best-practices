package cache

import (
	"fmt"
	"sync"
	"testing"
	"time"
)

// ---------------------------------------------------------------------------
// Set + Get: happy path
// ---------------------------------------------------------------------------

func TestSetAndGet_BasicTypes(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name  string
		key   string
		value interface{}
	}{
		{"string value", "greeting", "hello"},
		{"integer value", "count", 42},
		{"float value", "pi", 3.14},
		{"bool value", "flag", true},
		{"nil value", "nothing", nil},
		{"slice value", "nums", []int{1, 2, 3}},
		{"struct value", "point", struct{ X, Y int }{1, 2}},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()
			c := New()

			c.Set(tt.key, tt.value, 0)

			got, ok := c.Get(tt.key)
			if !ok {
				t.Fatalf("Get(%q) returned ok=false, want ok=true", tt.key)
			}
			if fmt.Sprintf("%v", got) != fmt.Sprintf("%v", tt.value) {
				t.Errorf("Get(%q) = %v, want %v", tt.key, got, tt.value)
			}
		})
	}
}

// ---------------------------------------------------------------------------
// Get: sad path (missing keys)
// ---------------------------------------------------------------------------

func TestGet_MissingKey(t *testing.T) {
	t.Parallel()
	c := New()

	got, ok := c.Get("nonexistent")

	if ok {
		t.Errorf("Get(nonexistent) ok = true, want false")
	}
	if got != nil {
		t.Errorf("Get(nonexistent) value = %v, want nil", got)
	}
}

func TestGet_MissingKeyInPopulatedCache(t *testing.T) {
	t.Parallel()
	c := New()
	c.Set("exists", "value", 0)

	got, ok := c.Get("does-not-exist")

	if ok {
		t.Errorf("Get(does-not-exist) ok = true, want false")
	}
	if got != nil {
		t.Errorf("Get(does-not-exist) value = %v, want nil", got)
	}
	// Verify the existing key is unaffected.
	existsVal, existsOk := c.Get("exists")
	if !existsOk || existsVal != "value" {
		t.Errorf("Get(exists) = (%v, %v), want (value, true)", existsVal, existsOk)
	}
}

// ---------------------------------------------------------------------------
// TTL expiration
// ---------------------------------------------------------------------------

func TestGet_ExpiredItem(t *testing.T) {
	t.Parallel()
	c := New()
	c.Set("temp", "data", 10*time.Millisecond)

	// Before expiry: should be present.
	got, ok := c.Get("temp")
	if !ok {
		t.Fatalf("Get(temp) before expiry: ok = false, want true")
	}
	if got != "data" {
		t.Errorf("Get(temp) before expiry = %v, want data", got)
	}

	// Wait for expiry.
	time.Sleep(20 * time.Millisecond)

	got, ok = c.Get("temp")
	if ok {
		t.Errorf("Get(temp) after expiry: ok = true, want false")
	}
	if got != nil {
		t.Errorf("Get(temp) after expiry: value = %v, want nil", got)
	}
}

func TestSet_ZeroTTLNeverExpires(t *testing.T) {
	t.Parallel()
	c := New()
	c.Set("permanent", "stays", 0)

	// Even after a short sleep, zero-TTL items remain accessible.
	time.Sleep(5 * time.Millisecond)

	got, ok := c.Get("permanent")
	if !ok {
		t.Fatalf("Get(permanent) ok = false, want true for zero-TTL item")
	}
	if got != "stays" {
		t.Errorf("Get(permanent) = %v, want stays", got)
	}
}

// ---------------------------------------------------------------------------
// Set: overwrite existing key
// ---------------------------------------------------------------------------

func TestSet_OverwriteExistingKey(t *testing.T) {
	t.Parallel()
	c := New()

	c.Set("key", "original", 0)
	c.Set("key", "updated", 0)

	got, ok := c.Get("key")
	if !ok {
		t.Fatalf("Get(key) ok = false after overwrite")
	}
	if got != "updated" {
		t.Errorf("Get(key) = %v, want updated", got)
	}
	if c.Len() != 1 {
		t.Errorf("Len() = %d, want 1 after overwrite (not 2)", c.Len())
	}
}

func TestSet_OverwriteRefreshesTTL(t *testing.T) {
	t.Parallel()
	c := New()

	// Set with short TTL.
	c.Set("key", "v1", 10*time.Millisecond)

	// Overwrite with much longer TTL before the first one expires.
	c.Set("key", "v2", 5*time.Second)

	// Wait past the original TTL.
	time.Sleep(20 * time.Millisecond)

	got, ok := c.Get("key")
	if !ok {
		t.Fatalf("Get(key) ok = false; overwrite should have refreshed TTL")
	}
	if got != "v2" {
		t.Errorf("Get(key) = %v, want v2", got)
	}
}

// ---------------------------------------------------------------------------
// Delete
// ---------------------------------------------------------------------------

func TestDelete_ExistingKey(t *testing.T) {
	t.Parallel()
	c := New()
	c.Set("a", 1, 0)
	c.Set("b", 2, 0)

	c.Delete("a")

	_, ok := c.Get("a")
	if ok {
		t.Errorf("Get(a) ok = true after Delete, want false")
	}
	// Verify other keys are unaffected.
	got, ok := c.Get("b")
	if !ok || got != 2 {
		t.Errorf("Get(b) = (%v, %v), want (2, true) after deleting a", got, ok)
	}
	if c.Len() != 1 {
		t.Errorf("Len() = %d after Delete, want 1", c.Len())
	}
}

func TestDelete_NonexistentKey(t *testing.T) {
	t.Parallel()
	c := New()
	c.Set("a", 1, 0)

	// Deleting a key that doesn't exist should not panic or affect other keys.
	c.Delete("nonexistent")

	got, ok := c.Get("a")
	if !ok || got != 1 {
		t.Errorf("Get(a) = (%v, %v), want (1, true) after deleting nonexistent key", got, ok)
	}
	if c.Len() != 1 {
		t.Errorf("Len() = %d, want 1", c.Len())
	}
}

func TestDelete_AlreadyExpiredKey(t *testing.T) {
	t.Parallel()
	c := New()
	c.Set("temp", "data", 10*time.Millisecond)
	time.Sleep(20 * time.Millisecond)

	// The item is expired but still in the map (Len counts it).
	lenBefore := c.Len()
	c.Delete("temp")
	lenAfter := c.Len()

	if lenAfter >= lenBefore {
		t.Errorf("Len after Delete = %d, want less than %d (expired item should be removed)", lenAfter, lenBefore)
	}
	_, ok := c.Get("temp")
	if ok {
		t.Errorf("Get(temp) ok = true after Delete, want false")
	}
}

// ---------------------------------------------------------------------------
// Len
// ---------------------------------------------------------------------------

func TestLen_EmptyCache(t *testing.T) {
	t.Parallel()
	c := New()

	if c.Len() != 0 {
		t.Errorf("Len() of new cache = %d, want 0", c.Len())
	}
}

func TestLen_CountsExpiredItems(t *testing.T) {
	t.Parallel()
	c := New()
	c.Set("permanent", "stays", 0)
	c.Set("temp", "goes", 10*time.Millisecond)

	if c.Len() != 2 {
		t.Errorf("Len() before expiry = %d, want 2", c.Len())
	}

	time.Sleep(20 * time.Millisecond)

	// Len counts expired items (documented behavior).
	if c.Len() != 2 {
		t.Errorf("Len() after expiry = %d, want 2 (Len includes expired items)", c.Len())
	}

	// But Get returns false for the expired one.
	_, ok := c.Get("temp")
	if ok {
		t.Errorf("Get(temp) ok = true after expiry, want false")
	}
}

func TestLen_AfterOperations(t *testing.T) {
	t.Parallel()
	c := New()

	c.Set("a", 1, 0)
	c.Set("b", 2, 0)
	c.Set("c", 3, 0)
	if c.Len() != 3 {
		t.Errorf("Len() after 3 sets = %d, want 3", c.Len())
	}

	c.Delete("b")
	if c.Len() != 2 {
		t.Errorf("Len() after delete = %d, want 2", c.Len())
	}

	// Overwrite should not increase Len.
	c.Set("a", 10, 0)
	if c.Len() != 2 {
		t.Errorf("Len() after overwrite = %d, want 2", c.Len())
	}
}

// ---------------------------------------------------------------------------
// Clear
// ---------------------------------------------------------------------------

func TestClear_RemovesAllItems(t *testing.T) {
	t.Parallel()
	c := New()
	c.Set("a", 1, 0)
	c.Set("b", 2, 0)
	c.Set("c", 3, time.Minute)

	c.Clear()

	if c.Len() != 0 {
		t.Errorf("Len() after Clear = %d, want 0", c.Len())
	}
	_, okA := c.Get("a")
	_, okB := c.Get("b")
	_, okC := c.Get("c")
	if okA || okB || okC {
		t.Errorf("Get returned ok=true after Clear: a=%v, b=%v, c=%v", okA, okB, okC)
	}
}

func TestClear_CacheUsableAfterClear(t *testing.T) {
	t.Parallel()
	c := New()
	c.Set("a", 1, 0)
	c.Clear()

	c.Set("b", 2, 0)

	got, ok := c.Get("b")
	if !ok || got != 2 {
		t.Errorf("Get(b) = (%v, %v) after Clear+Set, want (2, true)", got, ok)
	}
	if c.Len() != 1 {
		t.Errorf("Len() after Clear+Set = %d, want 1", c.Len())
	}
	// Old key should still be absent.
	_, okA := c.Get("a")
	if okA {
		t.Errorf("Get(a) ok = true after Clear, want false")
	}
}

func TestClear_OnEmptyCache(t *testing.T) {
	t.Parallel()
	c := New()

	// Should not panic.
	c.Clear()

	if c.Len() != 0 {
		t.Errorf("Len() after Clear on empty cache = %d, want 0", c.Len())
	}
}

// ---------------------------------------------------------------------------
// Edge cases: key variations
// ---------------------------------------------------------------------------

func TestSet_EmptyStringKey(t *testing.T) {
	t.Parallel()
	c := New()

	c.Set("", "empty-key-value", 0)

	got, ok := c.Get("")
	if !ok {
		t.Fatalf("Get('') ok = false, want true")
	}
	if got != "empty-key-value" {
		t.Errorf("Get('') = %v, want empty-key-value", got)
	}
	if c.Len() != 1 {
		t.Errorf("Len() = %d, want 1", c.Len())
	}
}

func TestSet_SpecialCharacterKeys(t *testing.T) {
	t.Parallel()

	keys := []string{
		"key with spaces",
		"key/with/slashes",
		"key.with.dots",
		"emoji-🔑",
		"unicode-日本語",
		"newline\nkey",
		"",
	}

	c := New()
	for i, key := range keys {
		c.Set(key, i, 0)
	}

	for i, key := range keys {
		got, ok := c.Get(key)
		if !ok {
			t.Errorf("Get(%q) ok = false, want true", key)
			continue
		}
		if got != i {
			t.Errorf("Get(%q) = %v, want %d", key, got, i)
		}
	}

	if c.Len() != len(keys) {
		t.Errorf("Len() = %d, want %d", c.Len(), len(keys))
	}
}

// ---------------------------------------------------------------------------
// Concurrency / Thread-Safety (run with -race)
// ---------------------------------------------------------------------------

func TestConcurrentSetAndGet(t *testing.T) {
	t.Parallel()
	c := New()
	const goroutines = 50
	const opsPerGoroutine = 100

	var wg sync.WaitGroup
	wg.Add(goroutines)

	for g := 0; g < goroutines; g++ {
		go func(id int) {
			defer wg.Done()
			key := fmt.Sprintf("key-%d", id)
			for i := 0; i < opsPerGoroutine; i++ {
				c.Set(key, i, time.Minute)
				c.Get(key)
			}
		}(g)
	}

	wg.Wait()

	// After all goroutines finish, every key should be retrievable.
	for g := 0; g < goroutines; g++ {
		key := fmt.Sprintf("key-%d", g)
		_, ok := c.Get(key)
		if !ok {
			t.Errorf("Get(%q) ok = false after concurrent writes, want true", key)
		}
	}
	if c.Len() != goroutines {
		t.Errorf("Len() = %d, want %d", c.Len(), goroutines)
	}
}

func TestConcurrentMixedOperations(t *testing.T) {
	t.Parallel()
	c := New()
	const goroutines = 20

	var wg sync.WaitGroup
	wg.Add(goroutines * 4) // 4 operation types

	// Concurrent Set.
	for g := 0; g < goroutines; g++ {
		go func(id int) {
			defer wg.Done()
			c.Set(fmt.Sprintf("key-%d", id), id, time.Minute)
		}(g)
	}

	// Concurrent Get.
	for g := 0; g < goroutines; g++ {
		go func(id int) {
			defer wg.Done()
			c.Get(fmt.Sprintf("key-%d", id))
		}(g)
	}

	// Concurrent Delete.
	for g := 0; g < goroutines; g++ {
		go func(id int) {
			defer wg.Done()
			c.Delete(fmt.Sprintf("key-%d", id))
		}(g)
	}

	// Concurrent Len + Clear interleaved.
	for g := 0; g < goroutines; g++ {
		go func(id int) {
			defer wg.Done()
			c.Len()
			if id%5 == 0 {
				c.Clear()
			}
		}(g)
	}

	wg.Wait()

	// After the storm of mixed operations, the cache should be in a consistent state.
	// We can't predict the exact contents but it should not panic or deadlock
	// and Len should be non-negative.
	length := c.Len()
	if length < 0 {
		t.Errorf("Len() = %d after concurrent ops, want >= 0", length)
	}
}

func TestConcurrentSetSameKey(t *testing.T) {
	t.Parallel()
	c := New()
	const goroutines = 100

	var wg sync.WaitGroup
	wg.Add(goroutines)

	for g := 0; g < goroutines; g++ {
		go func(id int) {
			defer wg.Done()
			c.Set("shared", id, time.Minute)
		}(g)
	}

	wg.Wait()

	// Exactly one write should win.
	got, ok := c.Get("shared")
	if !ok {
		t.Fatalf("Get(shared) ok = false, want true")
	}
	val, isInt := got.(int)
	if !isInt {
		t.Fatalf("Get(shared) type = %T, want int", got)
	}
	if val < 0 || val >= goroutines {
		t.Errorf("Get(shared) = %d, want value in [0, %d)", val, goroutines)
	}
	if c.Len() != 1 {
		t.Errorf("Len() = %d after concurrent writes to same key, want 1", c.Len())
	}
}

// ---------------------------------------------------------------------------
// Multiple items and isolation
// ---------------------------------------------------------------------------

func TestMultipleItemsAreIsolated(t *testing.T) {
	t.Parallel()
	c := New()

	c.Set("short", "fast", 10*time.Millisecond)
	c.Set("long", "slow", time.Minute)
	c.Set("forever", "eternal", 0)

	time.Sleep(20 * time.Millisecond)

	// Short-lived item should be expired.
	_, okShort := c.Get("short")
	if okShort {
		t.Errorf("Get(short) ok = true after expiry, want false")
	}

	// Long-lived item should still be present.
	gotLong, okLong := c.Get("long")
	if !okLong || gotLong != "slow" {
		t.Errorf("Get(long) = (%v, %v), want (slow, true)", gotLong, okLong)
	}

	// Permanent item should still be present.
	gotForever, okForever := c.Get("forever")
	if !okForever || gotForever != "eternal" {
		t.Errorf("Get(forever) = (%v, %v), want (eternal, true)", gotForever, okForever)
	}

	// Len counts all items including expired.
	if c.Len() != 3 {
		t.Errorf("Len() = %d, want 3 (includes expired)", c.Len())
	}
}

// ---------------------------------------------------------------------------
// New() constructor
// ---------------------------------------------------------------------------

func TestNew_ReturnsIndependentCaches(t *testing.T) {
	t.Parallel()
	c1 := New()
	c2 := New()

	c1.Set("key", "from-c1", 0)

	_, ok := c2.Get("key")
	if ok {
		t.Errorf("Get(key) on c2 returned ok=true; caches should be independent")
	}
	if c2.Len() != 0 {
		t.Errorf("c2.Len() = %d, want 0", c2.Len())
	}
	if c1.Len() != 1 {
		t.Errorf("c1.Len() = %d, want 1", c1.Len())
	}
}

// ---------------------------------------------------------------------------
// Boundary: large number of items
// ---------------------------------------------------------------------------

func TestLargeNumberOfItems(t *testing.T) {
	t.Parallel()
	c := New()
	const n = 10_000

	for i := 0; i < n; i++ {
		c.Set(fmt.Sprintf("key-%d", i), i, 0)
	}

	if c.Len() != n {
		t.Errorf("Len() = %d, want %d", c.Len(), n)
	}

	// Spot-check a few values.
	for _, i := range []int{0, 1, n / 2, n - 1} {
		got, ok := c.Get(fmt.Sprintf("key-%d", i))
		if !ok {
			t.Errorf("Get(key-%d) ok = false, want true", i)
			continue
		}
		if got != i {
			t.Errorf("Get(key-%d) = %v, want %d", i, got, i)
		}
	}

	c.Clear()
	if c.Len() != 0 {
		t.Errorf("Len() after Clear = %d, want 0", c.Len())
	}
}

// ---------------------------------------------------------------------------
// Delete then re-add same key
// ---------------------------------------------------------------------------

func TestDeleteThenReAdd(t *testing.T) {
	t.Parallel()
	c := New()

	c.Set("key", "v1", 0)
	c.Delete("key")

	_, ok := c.Get("key")
	if ok {
		t.Errorf("Get(key) ok = true after Delete, want false")
	}

	c.Set("key", "v2", 0)

	got, ok := c.Get("key")
	if !ok {
		t.Fatalf("Get(key) ok = false after re-add, want true")
	}
	if got != "v2" {
		t.Errorf("Get(key) = %v after re-add, want v2", got)
	}
	if c.Len() != 1 {
		t.Errorf("Len() = %d after Delete+re-add, want 1", c.Len())
	}
}
