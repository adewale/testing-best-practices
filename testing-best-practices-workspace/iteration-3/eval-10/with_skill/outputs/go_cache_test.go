// Characterization tests for the cache package.
//
// These tests capture the CURRENT behavior of the cache implementation
// before refactoring. They are change-detection tests, not correctness tests.
// If a refactoring causes any of these to fail, investigate whether the old
// behavior was a bug (update the test) or a feature (fix the refactoring).
package cache

import (
	"sync"
	"testing"
	"time"
)

// ---------------------------------------------------------------------------
// New
// ---------------------------------------------------------------------------

func TestNew_ReturnsNonNilCache(t *testing.T) {
	c := New()
	if c == nil {
		t.Fatal("New() returned nil")
	}
	if c.items == nil {
		t.Error("New() cache has nil items map")
	}
	if len(c.items) != 0 {
		t.Errorf("New() cache has %d items, want 0", len(c.items))
	}
}

// ---------------------------------------------------------------------------
// Set + Get — basic storage
// ---------------------------------------------------------------------------

func TestSetGet_StringValue(t *testing.T) {
	c := New()
	c.Set("greeting", "hello", 0)

	val, ok := c.Get("greeting")
	if !ok {
		t.Fatal("Get returned ok=false for existing key")
	}
	if val != "hello" {
		t.Errorf("Get value = %v, want %q", val, "hello")
	}
}

func TestSetGet_IntValue(t *testing.T) {
	c := New()
	c.Set("count", 42, 0)

	val, ok := c.Get("count")
	if !ok {
		t.Fatal("Get returned ok=false for existing key")
	}
	if val != 42 {
		t.Errorf("Get value = %v, want %d", val, 42)
	}
}

func TestSetGet_NilValue(t *testing.T) {
	c := New()
	c.Set("nothing", nil, 0)

	val, ok := c.Get("nothing")
	if !ok {
		t.Fatal("Get returned ok=false for key set to nil")
	}
	if val != nil {
		t.Errorf("Get value = %v, want nil", val)
	}
}

func TestSetGet_StructValue(t *testing.T) {
	type person struct {
		Name string
		Age  int
	}
	p := person{Name: "Alice", Age: 30}
	c := New()
	c.Set("user", p, 0)

	val, ok := c.Get("user")
	if !ok {
		t.Fatal("Get returned ok=false for struct value")
	}
	got, isType := val.(person)
	if !isType {
		t.Fatalf("Get value type = %T, want person", val)
	}
	if got.Name != "Alice" || got.Age != 30 {
		t.Errorf("Get value = %+v, want %+v", got, p)
	}
}

func TestSetGet_EmptyStringKey(t *testing.T) {
	c := New()
	c.Set("", "empty-key-value", 0)

	val, ok := c.Get("")
	if !ok {
		t.Fatal("Get returned ok=false for empty string key")
	}
	if val != "empty-key-value" {
		t.Errorf("Get value = %v, want %q", val, "empty-key-value")
	}
}

// ---------------------------------------------------------------------------
// Set overwrites existing key
// ---------------------------------------------------------------------------

func TestSet_OverwritesExistingKey(t *testing.T) {
	c := New()
	c.Set("key", "first", 0)
	c.Set("key", "second", 0)

	val, ok := c.Get("key")
	if !ok {
		t.Fatal("Get returned ok=false after overwrite")
	}
	if val != "second" {
		t.Errorf("Get value = %v, want %q (overwritten value)", val, "second")
	}
	if c.Len() != 1 {
		t.Errorf("Len() = %d after overwrite, want 1", c.Len())
	}
}

func TestSet_OverwriteChangesTypeAndTTL(t *testing.T) {
	c := New()
	c.Set("key", "string-val", 0)
	c.Set("key", 999, time.Hour)

	val, ok := c.Get("key")
	if !ok {
		t.Fatal("Get returned ok=false after type-changing overwrite")
	}
	if val != 999 {
		t.Errorf("Get value = %v, want 999", val)
	}
}

// ---------------------------------------------------------------------------
// Get — missing keys
// ---------------------------------------------------------------------------

func TestGet_MissingKey(t *testing.T) {
	c := New()

	val, ok := c.Get("nonexistent")
	if ok {
		t.Error("Get returned ok=true for nonexistent key")
	}
	if val != nil {
		t.Errorf("Get value = %v for nonexistent key, want nil", val)
	}
}

func TestGet_EmptyCache(t *testing.T) {
	c := New()

	val, ok := c.Get("anything")
	if ok {
		t.Error("Get returned ok=true on empty cache")
	}
	if val != nil {
		t.Errorf("Get value = %v, want nil", val)
	}
}

// ---------------------------------------------------------------------------
// TTL behavior
// ---------------------------------------------------------------------------

func TestSet_ZeroTTLNeverExpires(t *testing.T) {
	c := New()
	c.Set("permanent", "value", 0)

	// Even after a small sleep, item should still be there.
	time.Sleep(5 * time.Millisecond)

	val, ok := c.Get("permanent")
	if !ok {
		t.Fatal("Get returned ok=false for zero-TTL item (should never expire)")
	}
	if val != "value" {
		t.Errorf("Get value = %v, want %q", val, "value")
	}
}

func TestSet_NegativeTTLBehavesLikeZero(t *testing.T) {
	// Characterization: negative TTL does NOT cause immediate expiry.
	// The condition `ttl > 0` means negative TTL leaves expiresAt as zero-value,
	// which is treated as "never expires" by Get.
	c := New()
	c.Set("neg", "val", -time.Second)

	val, ok := c.Get("neg")
	if !ok {
		t.Fatal("Get returned ok=false for negative-TTL item (behaves as never-expire)")
	}
	if val != "val" {
		t.Errorf("Get value = %v, want %q", val, "val")
	}
}

func TestGet_ExpiredItemReturnsNilFalse(t *testing.T) {
	c := New()
	c.Set("temp", "data", 10*time.Millisecond)

	// Verify it exists before expiry.
	val, ok := c.Get("temp")
	if !ok {
		t.Fatal("Get returned ok=false before expiry")
	}
	if val != "data" {
		t.Errorf("Get value = %v before expiry, want %q", val, "data")
	}

	// Wait for expiry.
	time.Sleep(20 * time.Millisecond)

	val, ok = c.Get("temp")
	if ok {
		t.Error("Get returned ok=true for expired item")
	}
	if val != nil {
		t.Errorf("Get value = %v for expired item, want nil", val)
	}
}

// ---------------------------------------------------------------------------
// Len — counts expired items
// ---------------------------------------------------------------------------

func TestLen_EmptyCache(t *testing.T) {
	c := New()
	if got := c.Len(); got != 0 {
		t.Errorf("Len() = %d on empty cache, want 0", got)
	}
}

func TestLen_CountsMultipleItems(t *testing.T) {
	c := New()
	c.Set("a", 1, 0)
	c.Set("b", 2, 0)
	c.Set("c", 3, 0)

	if got := c.Len(); got != 3 {
		t.Errorf("Len() = %d, want 3", got)
	}
}

func TestLen_IncludesExpiredItems(t *testing.T) {
	// Characterization: Len counts ALL items in the map, including expired ones.
	// Expired items are not lazily removed by Get, and there is no cleanup goroutine.
	c := New()
	c.Set("short", "val", 10*time.Millisecond)
	c.Set("long", "val", time.Hour)

	time.Sleep(20 * time.Millisecond)

	// "short" has expired, but Len still counts it.
	if got := c.Len(); got != 2 {
		t.Errorf("Len() = %d after expiry, want 2 (expired items still counted)", got)
	}

	// Confirm Get indeed treats it as expired.
	_, ok := c.Get("short")
	if ok {
		t.Error("Get returned ok=true for expired item")
	}
}

// ---------------------------------------------------------------------------
// Delete
// ---------------------------------------------------------------------------

func TestDelete_RemovesExistingKey(t *testing.T) {
	c := New()
	c.Set("key", "val", 0)
	c.Delete("key")

	val, ok := c.Get("key")
	if ok {
		t.Error("Get returned ok=true after Delete")
	}
	if val != nil {
		t.Errorf("Get value = %v after Delete, want nil", val)
	}
	if c.Len() != 0 {
		t.Errorf("Len() = %d after Delete, want 0", c.Len())
	}
}

func TestDelete_NonexistentKeyIsNoOp(t *testing.T) {
	c := New()
	c.Set("keep", "val", 0)

	// Deleting a key that doesn't exist should not panic or affect other keys.
	c.Delete("nonexistent")

	if c.Len() != 1 {
		t.Errorf("Len() = %d after deleting nonexistent key, want 1", c.Len())
	}
	val, ok := c.Get("keep")
	if !ok || val != "val" {
		t.Errorf("Existing key affected by Delete of nonexistent key: ok=%v, val=%v", ok, val)
	}
}

func TestDelete_OnEmptyCache(t *testing.T) {
	c := New()
	// Should not panic.
	c.Delete("anything")
	if c.Len() != 0 {
		t.Errorf("Len() = %d after Delete on empty cache, want 0", c.Len())
	}
}

// ---------------------------------------------------------------------------
// Clear
// ---------------------------------------------------------------------------

func TestClear_RemovesAllItems(t *testing.T) {
	c := New()
	c.Set("a", 1, 0)
	c.Set("b", 2, 0)
	c.Set("c", 3, 0)

	c.Clear()

	if c.Len() != 0 {
		t.Errorf("Len() = %d after Clear, want 0", c.Len())
	}
	for _, key := range []string{"a", "b", "c"} {
		val, ok := c.Get(key)
		if ok {
			t.Errorf("Get(%q) returned ok=true after Clear", key)
		}
		if val != nil {
			t.Errorf("Get(%q) value = %v after Clear, want nil", key, val)
		}
	}
}

func TestClear_OnEmptyCacheIsNoOp(t *testing.T) {
	c := New()
	c.Clear()
	if c.Len() != 0 {
		t.Errorf("Len() = %d after Clear on empty cache, want 0", c.Len())
	}
}

func TestClear_CacheIsReusableAfterClear(t *testing.T) {
	c := New()
	c.Set("old", "val", 0)
	c.Clear()

	c.Set("new", "val2", 0)
	val, ok := c.Get("new")
	if !ok {
		t.Fatal("Get returned ok=false after Clear + Set")
	}
	if val != "val2" {
		t.Errorf("Get value = %v after Clear + Set, want %q", val, "val2")
	}
	if c.Len() != 1 {
		t.Errorf("Len() = %d after Clear + Set, want 1", c.Len())
	}
}

// ---------------------------------------------------------------------------
// Expired items are NOT lazily removed
// ---------------------------------------------------------------------------

func TestGet_DoesNotRemoveExpiredItem(t *testing.T) {
	// Characterization: calling Get on an expired key returns nil/false but does
	// NOT delete the item from the underlying map. Len still counts it.
	c := New()
	c.Set("temp", "data", 10*time.Millisecond)
	time.Sleep(20 * time.Millisecond)

	// Get should report it as missing.
	_, ok := c.Get("temp")
	if ok {
		t.Error("Get returned ok=true for expired item")
	}

	// But it's still in the map (Len counts it).
	if c.Len() != 1 {
		t.Errorf("Len() = %d after Get on expired item, want 1 (not lazily removed)", c.Len())
	}
}

// ---------------------------------------------------------------------------
// Multiple distinct keys
// ---------------------------------------------------------------------------

func TestMultipleKeys_IndependentStorage(t *testing.T) {
	c := New()
	c.Set("x", 10, 0)
	c.Set("y", 20, 0)
	c.Set("z", 30, 0)

	tests := []struct {
		key  string
		want int
	}{
		{"x", 10},
		{"y", 20},
		{"z", 30},
	}
	for _, tt := range tests {
		val, ok := c.Get(tt.key)
		if !ok {
			t.Errorf("Get(%q) ok=false, want true", tt.key)
			continue
		}
		if val != tt.want {
			t.Errorf("Get(%q) = %v, want %d", tt.key, val, tt.want)
		}
	}
}

// ---------------------------------------------------------------------------
// Concurrency safety
// ---------------------------------------------------------------------------

func TestConcurrentAccess_NoRaceOrPanic(t *testing.T) {
	// Characterization: the cache uses sync.RWMutex and should be safe for
	// concurrent reads and writes. This test verifies no panics occur.
	c := New()
	var wg sync.WaitGroup

	// Writers.
	for i := 0; i < 50; i++ {
		wg.Add(1)
		go func(n int) {
			defer wg.Done()
			key := "key"
			c.Set(key, n, time.Millisecond*100)
		}(i)
	}

	// Readers.
	for i := 0; i < 50; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			c.Get("key")
		}()
	}

	// Deleters.
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			c.Delete("key")
		}()
	}

	// Len callers.
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			c.Len()
		}()
	}

	// Clear callers.
	for i := 0; i < 5; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			c.Clear()
		}()
	}

	wg.Wait()
	// If we reach here without a panic or data race, the test passes.
	// The final state is non-deterministic, so we only assert no crash.
}

// ---------------------------------------------------------------------------
// Table-driven: Set + Get with various TTLs
// ---------------------------------------------------------------------------

func TestSetGet_TableDrivenTTLBehavior(t *testing.T) {
	tests := []struct {
		name       string
		ttl        time.Duration
		sleepAfter time.Duration
		wantOK     bool
	}{
		{"zero TTL, no sleep", 0, 0, true},
		{"positive TTL, read before expiry", 50 * time.Millisecond, 0, true},
		{"positive TTL, read after expiry", 10 * time.Millisecond, 20 * time.Millisecond, false},
		{"negative TTL, no sleep (behaves as never-expire)", -time.Second, 0, true},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := New()
			c.Set("k", "v", tt.ttl)

			if tt.sleepAfter > 0 {
				time.Sleep(tt.sleepAfter)
			}

			val, ok := c.Get("k")
			if ok != tt.wantOK {
				t.Errorf("Get ok = %v, want %v", ok, tt.wantOK)
			}
			if tt.wantOK && val != "v" {
				t.Errorf("Get value = %v, want %q", val, "v")
			}
			if !tt.wantOK && val != nil {
				t.Errorf("Get value = %v, want nil", val)
			}
		})
	}
}

// ---------------------------------------------------------------------------
// Interaction: Delete then Set same key
// ---------------------------------------------------------------------------

func TestDelete_ThenSetSameKey(t *testing.T) {
	c := New()
	c.Set("k", "first", 0)
	c.Delete("k")
	c.Set("k", "second", 0)

	val, ok := c.Get("k")
	if !ok {
		t.Fatal("Get returned ok=false after Delete + re-Set")
	}
	if val != "second" {
		t.Errorf("Get value = %v, want %q", val, "second")
	}
	if c.Len() != 1 {
		t.Errorf("Len() = %d, want 1", c.Len())
	}
}

// ---------------------------------------------------------------------------
// Interaction: Clear then Set
// ---------------------------------------------------------------------------

func TestClear_ThenSetNewItems(t *testing.T) {
	c := New()
	c.Set("a", 1, 0)
	c.Set("b", 2, 0)
	c.Clear()
	c.Set("c", 3, 0)

	if c.Len() != 1 {
		t.Errorf("Len() = %d after Clear + Set, want 1", c.Len())
	}
	_, okA := c.Get("a")
	_, okB := c.Get("b")
	valC, okC := c.Get("c")
	if okA || okB {
		t.Error("Cleared keys still accessible")
	}
	if !okC || valC != 3 {
		t.Errorf("New key after Clear: ok=%v, val=%v, want true/3", okC, valC)
	}
}

// ---------------------------------------------------------------------------
// Overwrite expired item with fresh item
// ---------------------------------------------------------------------------

func TestSet_OverwriteExpiredItemRefreshes(t *testing.T) {
	c := New()
	c.Set("k", "old", 10*time.Millisecond)
	time.Sleep(20 * time.Millisecond)

	// Item is now expired.
	_, ok := c.Get("k")
	if ok {
		t.Fatal("Get returned ok=true for expired item (setup error)")
	}

	// Overwrite with a fresh, non-expiring value.
	c.Set("k", "new", 0)
	val, ok := c.Get("k")
	if !ok {
		t.Fatal("Get returned ok=false after overwriting expired item")
	}
	if val != "new" {
		t.Errorf("Get value = %v, want %q", val, "new")
	}
}
