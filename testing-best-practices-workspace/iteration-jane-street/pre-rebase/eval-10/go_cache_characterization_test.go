// Package cache characterization tests.
//
// These tests record the CURRENT behavior of the cache implementation in
// go_cache.go. They are not assertions of correctness — they exist to detect
// behavior changes during refactoring. If a test fails after a refactor,
// decide whether the old behavior was a bug (update the test) or a feature
// (fix the refactoring).
//
// Note: the cache calls time.Now() directly with no injectable clock seam, so
// expiry tests use short real-time TTLs with time.Sleep. This is itself a
// characterization observation: any refactor that introduces a clock seam
// will require updating these tests.
package cache

import (
	"sync"
	"testing"
	"time"
)

// --- New / empty cache ---------------------------------------------------

func TestCharacterize_New_ReturnsNonNilEmptyCache(t *testing.T) {
	c := New()
	if c == nil {
		t.Fatalf("New() returned nil")
	}
	if c.Len() != 0 {
		t.Errorf("New().Len() = %d, want 0", c.Len())
	}
	if v, ok := c.Get("anything"); ok || v != nil {
		t.Errorf("New().Get(\"anything\") = (%v, %v), want (nil, false)", v, ok)
	}
}

func TestCharacterize_New_DistinctInstancesDoNotShareState(t *testing.T) {
	a := New()
	b := New()
	a.Set("k", "v-a", 0)
	if v, ok := b.Get("k"); ok || v != nil {
		t.Errorf("b.Get(\"k\") after a.Set = (%v, %v), want (nil, false)", v, ok)
	}
	if a.Len() != 1 {
		t.Errorf("a.Len() = %d, want 1", a.Len())
	}
	if b.Len() != 0 {
		t.Errorf("b.Len() = %d, want 0", b.Len())
	}
}

// --- Set / Get basic round-trips -----------------------------------------

func TestCharacterize_SetGet_StringValue_TTLZero_NoExpiry(t *testing.T) {
	c := New()
	c.Set("k", "hello", 0)
	v, ok := c.Get("k")
	if !ok {
		t.Fatalf("Get after Set returned ok=false, want true")
	}
	if v != "hello" {
		t.Errorf("Get returned %v, want %q", v, "hello")
	}
}

func TestCharacterize_SetGet_VariousValueTypes(t *testing.T) {
	c := New()

	tests := []struct {
		name  string
		key   string
		value interface{}
	}{
		{"string", "s", "hello"},
		{"int", "i", 42},
		{"int64", "i64", int64(9_999_999_999)},
		{"float64", "f", 3.14},
		{"bool true", "bt", true},
		{"bool false", "bf", false},
		{"nil value", "n", nil},
		{"empty string", "es", ""},
		{"zero int", "z", 0},
		{"slice", "sl", []int{1, 2, 3}},
		{"map", "m", map[string]int{"a": 1}},
		{"struct", "st", struct{ X int }{X: 7}},
	}

	for _, tt := range tests {
		c.Set(tt.key, tt.value, 0)
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			v, ok := c.Get(tt.key)
			if !ok {
				t.Fatalf("Get(%q) ok=false, want true (value type %T)", tt.key, tt.value)
			}
			// Compare via fmt-printable equality for slice/map/struct.
			// Direct == works for comparable types; for the rest we accept the
			// recorded behavior: the same value comes back.
			switch want := tt.value.(type) {
			case []int:
				got, ok := v.([]int)
				if !ok || len(got) != len(want) {
					t.Errorf("Get(%q) = %v, want %v", tt.key, v, want)
					return
				}
				for i := range want {
					if got[i] != want[i] {
						t.Errorf("Get(%q)[%d] = %v, want %v", tt.key, i, got[i], want[i])
					}
				}
			case map[string]int:
				got, ok := v.(map[string]int)
				if !ok || len(got) != len(want) {
					t.Errorf("Get(%q) = %v, want %v", tt.key, v, want)
					return
				}
				for k, w := range want {
					if got[k] != w {
						t.Errorf("Get(%q)[%q] = %v, want %v", tt.key, k, got[k], w)
					}
				}
			default:
				if v != tt.value {
					t.Errorf("Get(%q) = %v (%T), want %v (%T)", tt.key, v, v, tt.value, tt.value)
				}
			}
		})
	}
}

func TestCharacterize_Get_MissingKey_ReturnsNilFalse(t *testing.T) {
	c := New()
	c.Set("present", "v", 0)
	v, ok := c.Get("missing")
	if ok {
		t.Errorf("Get(\"missing\") ok = true, want false")
	}
	if v != nil {
		t.Errorf("Get(\"missing\") value = %v, want nil", v)
	}
}

func TestCharacterize_Get_NilValueStored_ReturnsNilTrue(t *testing.T) {
	// Recorded behavior: storing a nil value returns (nil, true) on Get.
	// Callers cannot distinguish "stored nil" from "missing key" by value
	// alone — they must check the boolean.
	c := New()
	c.Set("k", nil, 0)
	v, ok := c.Get("k")
	if !ok {
		t.Errorf("Get of stored nil returned ok=false, want true")
	}
	if v != nil {
		t.Errorf("Get of stored nil returned value = %v, want nil", v)
	}
}

func TestCharacterize_Set_OverwritesExistingValue(t *testing.T) {
	c := New()
	c.Set("k", "first", 0)
	c.Set("k", "second", 0)
	v, ok := c.Get("k")
	if !ok {
		t.Fatalf("Get after overwrite ok=false, want true")
	}
	if v != "second" {
		t.Errorf("Get after overwrite = %v, want %q", v, "second")
	}
	if c.Len() != 1 {
		t.Errorf("Len after overwrite = %d, want 1", c.Len())
	}
}

func TestCharacterize_Set_OverwriteReplacesTTL(t *testing.T) {
	// Recorded behavior: overwriting with ttl=0 removes the prior expiry.
	c := New()
	c.Set("k", "v1", 10*time.Millisecond)
	c.Set("k", "v2", 0) // overwrite with no expiry
	time.Sleep(30 * time.Millisecond)
	v, ok := c.Get("k")
	if !ok {
		t.Errorf("Get after TTL replaced with 0 ok=false, want true (overwrite should clear expiry)")
	}
	if v != "v2" {
		t.Errorf("Get after overwrite = %v, want %q", v, "v2")
	}
}

// --- Set: TTL semantics ---------------------------------------------------

func TestCharacterize_Set_NegativeTTL_TreatedAsNoExpiry(t *testing.T) {
	// Recorded behavior: the implementation only sets expiresAt when ttl > 0.
	// A negative TTL leaves expiresAt as the zero Time, so the item never
	// expires. This may be surprising — record it explicitly.
	c := New()
	c.Set("k", "v", -1*time.Hour)
	v, ok := c.Get("k")
	if !ok {
		t.Errorf("Get after Set with negative TTL ok=false, want true (negative TTL is treated as no expiry)")
	}
	if v != "v" {
		t.Errorf("Get after Set with negative TTL = %v, want %q", v, "v")
	}
}

func TestCharacterize_Set_ZeroTTL_NeverExpires(t *testing.T) {
	c := New()
	c.Set("k", "v", 0)
	time.Sleep(20 * time.Millisecond)
	v, ok := c.Get("k")
	if !ok {
		t.Errorf("Get with ttl=0 after sleep ok=false, want true (ttl=0 means no expiry)")
	}
	if v != "v" {
		t.Errorf("Get with ttl=0 after sleep = %v, want %q", v, "v")
	}
}

func TestCharacterize_Set_PositiveTTL_ExpiresAfterDuration(t *testing.T) {
	c := New()
	c.Set("k", "v", 20*time.Millisecond)

	// Before expiry: present.
	if v, ok := c.Get("k"); !ok || v != "v" {
		t.Errorf("Get before expiry = (%v, %v), want (%q, true)", v, ok, "v")
	}

	// Wait past expiry.
	time.Sleep(60 * time.Millisecond)

	v, ok := c.Get("k")
	if ok {
		t.Errorf("Get after expiry ok=true, want false")
	}
	if v != nil {
		t.Errorf("Get after expiry value = %v, want nil", v)
	}
}

func TestCharacterize_Set_ExpiredItem_StillCountsInLen(t *testing.T) {
	// Recorded behavior: Len includes expired items. There is no automatic
	// cleanup — only Get filters expired entries, and only Delete/Clear
	// remove them from the map.
	c := New()
	c.Set("k", "v", 10*time.Millisecond)
	time.Sleep(40 * time.Millisecond)

	// Get reports it gone...
	if _, ok := c.Get("k"); ok {
		t.Errorf("Get after expiry ok=true, want false")
	}
	// ...but Len still counts it.
	if got := c.Len(); got != 1 {
		t.Errorf("Len after expiry = %d, want 1 (expired items remain in the map)", got)
	}
}

// --- Delete ---------------------------------------------------------------

func TestCharacterize_Delete_RemovesExistingKey(t *testing.T) {
	c := New()
	c.Set("k", "v", 0)
	c.Delete("k")

	v, ok := c.Get("k")
	if ok {
		t.Errorf("Get after Delete ok=true, want false")
	}
	if v != nil {
		t.Errorf("Get after Delete value = %v, want nil", v)
	}
	if c.Len() != 0 {
		t.Errorf("Len after Delete = %d, want 0", c.Len())
	}
}

func TestCharacterize_Delete_MissingKey_NoEffectNoError(t *testing.T) {
	// Recorded behavior: deleting a missing key is a silent no-op.
	c := New()
	c.Set("present", "v", 0)
	c.Delete("missing")

	if c.Len() != 1 {
		t.Errorf("Len after Delete(missing) = %d, want 1", c.Len())
	}
	if v, ok := c.Get("present"); !ok || v != "v" {
		t.Errorf("unrelated key disturbed by Delete(missing): Get(\"present\") = (%v, %v)", v, ok)
	}
}

func TestCharacterize_Delete_OnlyAffectsTargetKey(t *testing.T) {
	c := New()
	c.Set("a", 1, 0)
	c.Set("b", 2, 0)
	c.Set("c", 3, 0)

	c.Delete("b")

	if v, ok := c.Get("a"); !ok || v != 1 {
		t.Errorf("Get(\"a\") = (%v, %v), want (1, true)", v, ok)
	}
	if v, ok := c.Get("b"); ok || v != nil {
		t.Errorf("Get(\"b\") = (%v, %v), want (nil, false)", v, ok)
	}
	if v, ok := c.Get("c"); !ok || v != 3 {
		t.Errorf("Get(\"c\") = (%v, %v), want (3, true)", v, ok)
	}
	if c.Len() != 2 {
		t.Errorf("Len = %d, want 2", c.Len())
	}
}

// --- Len -----------------------------------------------------------------

func TestCharacterize_Len_EmptyCache(t *testing.T) {
	c := New()
	if got := c.Len(); got != 0 {
		t.Errorf("Len of new cache = %d, want 0", got)
	}
}

func TestCharacterize_Len_CountsAllEntries(t *testing.T) {
	c := New()
	c.Set("a", 1, 0)
	c.Set("b", 2, 0)
	c.Set("c", 3, 0)
	if got := c.Len(); got != 3 {
		t.Errorf("Len after 3 unique Sets = %d, want 3", got)
	}
}

func TestCharacterize_Len_DuplicateKeyDoesNotIncreaseCount(t *testing.T) {
	c := New()
	c.Set("a", 1, 0)
	c.Set("a", 2, 0)
	c.Set("a", 3, 0)
	if got := c.Len(); got != 1 {
		t.Errorf("Len after 3 Sets to same key = %d, want 1", got)
	}
}

// --- Clear ---------------------------------------------------------------

func TestCharacterize_Clear_RemovesAllEntries(t *testing.T) {
	c := New()
	c.Set("a", 1, 0)
	c.Set("b", 2, 0)
	c.Set("c", 3, 0)

	c.Clear()

	if got := c.Len(); got != 0 {
		t.Errorf("Len after Clear = %d, want 0", got)
	}
	for _, k := range []string{"a", "b", "c"} {
		if v, ok := c.Get(k); ok || v != nil {
			t.Errorf("Get(%q) after Clear = (%v, %v), want (nil, false)", k, v, ok)
		}
	}
}

func TestCharacterize_Clear_OnEmptyCache_NoEffectNoError(t *testing.T) {
	c := New()
	c.Clear() // should not panic
	if got := c.Len(); got != 0 {
		t.Errorf("Len after Clear on empty cache = %d, want 0", got)
	}
}

func TestCharacterize_Clear_CacheReusableAfterClear(t *testing.T) {
	// Recorded behavior: Clear replaces the internal map with a fresh one;
	// the cache remains usable for subsequent operations.
	c := New()
	c.Set("a", 1, 0)
	c.Clear()
	c.Set("b", 2, 0)

	if got := c.Len(); got != 1 {
		t.Errorf("Len after Clear+Set = %d, want 1", got)
	}
	if v, ok := c.Get("b"); !ok || v != 2 {
		t.Errorf("Get(\"b\") after Clear+Set = (%v, %v), want (2, true)", v, ok)
	}
	if v, ok := c.Get("a"); ok || v != nil {
		t.Errorf("Get(\"a\") after Clear = (%v, %v), want (nil, false)", v, ok)
	}
}

// --- Key semantics --------------------------------------------------------

func TestCharacterize_Keys_AreCaseSensitive(t *testing.T) {
	c := New()
	c.Set("Key", "upper", 0)
	c.Set("key", "lower", 0)

	if v, ok := c.Get("Key"); !ok || v != "upper" {
		t.Errorf("Get(\"Key\") = (%v, %v), want (\"upper\", true)", v, ok)
	}
	if v, ok := c.Get("key"); !ok || v != "lower" {
		t.Errorf("Get(\"key\") = (%v, %v), want (\"lower\", true)", v, ok)
	}
	if c.Len() != 2 {
		t.Errorf("Len = %d, want 2 (keys differ only by case)", c.Len())
	}
}

func TestCharacterize_Keys_EmptyStringIsValidKey(t *testing.T) {
	// Recorded behavior: "" is a valid, distinct key.
	c := New()
	c.Set("", "empty-key-value", 0)

	v, ok := c.Get("")
	if !ok {
		t.Fatalf("Get(\"\") ok=false, want true")
	}
	if v != "empty-key-value" {
		t.Errorf("Get(\"\") = %v, want %q", v, "empty-key-value")
	}
	if c.Len() != 1 {
		t.Errorf("Len = %d, want 1", c.Len())
	}
}

// --- Concurrency ----------------------------------------------------------

func TestCharacterize_Concurrent_SetAndGet_DoNotPanic(t *testing.T) {
	// Recorded behavior: the cache is safe for concurrent Set/Get under
	// sync.RWMutex. This test exists to guard against a refactor that
	// removes or reorders the locking. Run with: go test -race
	c := New()
	const goroutines = 16
	const ops = 200

	var wg sync.WaitGroup
	wg.Add(goroutines * 2)

	for g := 0; g < goroutines; g++ {
		g := g
		go func() {
			defer wg.Done()
			for i := 0; i < ops; i++ {
				c.Set("k", g*1000+i, 0)
			}
		}()
		go func() {
			defer wg.Done()
			for i := 0; i < ops; i++ {
				_, _ = c.Get("k")
			}
		}()
	}

	wg.Wait()

	// After concurrent writes, the key must be present with *some* value.
	v, ok := c.Get("k")
	if !ok {
		t.Errorf("Get(\"k\") after concurrent Sets ok=false, want true")
	}
	if _, isInt := v.(int); !isInt {
		t.Errorf("Get(\"k\") = %v (%T), want some int value", v, v)
	}
}

func TestCharacterize_Concurrent_DeleteAndClear_DoNotPanic(t *testing.T) {
	c := New()
	for i := 0; i < 50; i++ {
		c.Set(string(rune('a'+i%26)), i, 0)
	}

	var wg sync.WaitGroup
	wg.Add(4)

	go func() {
		defer wg.Done()
		for i := 0; i < 100; i++ {
			c.Set("x", i, 0)
		}
	}()
	go func() {
		defer wg.Done()
		for i := 0; i < 100; i++ {
			c.Delete("x")
		}
	}()
	go func() {
		defer wg.Done()
		for i := 0; i < 50; i++ {
			c.Clear()
		}
	}()
	go func() {
		defer wg.Done()
		for i := 0; i < 100; i++ {
			_, _ = c.Get("x")
			_ = c.Len()
		}
	}()

	wg.Wait()
	// No assertion on final state — these operations race by design.
	// The point is: no panic, no data race (verified by -race).
}
