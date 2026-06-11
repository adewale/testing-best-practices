package store

import (
	"fmt"
	"math/rand"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"testing"
)

// --- Canonical dump helpers --------------------------------------------------

// canonicalEntry renders a single Entry into a stable string that covers every
// field the format claims to persist: key, value type, value contents, TTL.
// Sets (map[string]bool) have their keys sorted so map iteration order never
// causes false failures.
func canonicalEntry(key string, e Entry) string {
	var valStr string
	switch v := e.Value.(type) {
	case string:
		valStr = fmt.Sprintf("string(%q)", v)
	case []string:
		// Preserve slice order — order is part of the value contract.
		quoted := make([]string, len(v))
		for i, s := range v {
			quoted[i] = fmt.Sprintf("%q", s)
		}
		valStr = fmt.Sprintf("[]string{%s}", strings.Join(quoted, ","))
	case map[string]bool:
		keys := make([]string, 0, len(v))
		for k := range v {
			keys = append(keys, k)
		}
		sort.Strings(keys)
		parts := make([]string, len(keys))
		for i, k := range keys {
			parts[i] = fmt.Sprintf("%q:%v", k, v[k])
		}
		valStr = fmt.Sprintf("map[string]bool{%s}", strings.Join(parts, ","))
	default:
		valStr = fmt.Sprintf("%v", v)
	}
	return fmt.Sprintf("key=%q value=%s ttl=%d", key, valStr, e.TTLSeconds)
}

// canonicalDump serialises the entire store snapshot to a deterministic string.
// Keys are sorted so map iteration order never causes false failures.
// Every field (value, value type, TTL) is included so no persistence bug can
// hide behind a partial dump.
func canonicalDump(s *Store) string {
	snap := s.Snapshot()
	keys := make([]string, 0, len(snap))
	for k := range snap {
		keys = append(keys, k)
	}
	sort.Strings(keys)

	lines := make([]string, len(keys))
	for i, k := range keys {
		lines[i] = canonicalEntry(k, snap[k])
	}
	return strings.Join(lines, "\n")
}

// --- Seeded store builder ----------------------------------------------------

// buildSeededStore populates a Store with a rich, deterministic set of entries
// that exercises every supported value type plus the awkward edge cases.
// Using a seeded RNG means the dataset is reproducible across runs.
func buildSeededStore(rng *rand.Rand, numKeys int) *Store {
	s := NewStore()

	unicodeSuffixes := []string{"α", "β", "™", "日本語", "émoji🎉", ""}

	for i := 0; i < numKeys; i++ {
		key := fmt.Sprintf("key-%04d-%s", i, unicodeSuffixes[i%len(unicodeSuffixes)])

		// Rotate through all value types plus edge cases.
		switch i % 7 {
		case 0:
			// Plain string
			s.Set(key, fmt.Sprintf("value-%d", i), 0)
		case 1:
			// String with TTL
			ttl := rng.Intn(3600) + 1
			s.Set(key, fmt.Sprintf("timed-%d", i), ttl)
		case 2:
			// []string — non-empty
			length := rng.Intn(8) + 1
			slice := make([]string, length)
			for j := range slice {
				slice[j] = fmt.Sprintf("item-%d-%d", i, j)
			}
			s.Set(key, slice, 0)
		case 3:
			// []string — empty slice (edge case)
			s.Set(key, []string{}, 0)
		case 4:
			// map[string]bool — non-empty set
			size := rng.Intn(6) + 1
			m := make(map[string]bool, size)
			for j := 0; j < size; j++ {
				m[fmt.Sprintf("member-%d-%d", i, j)] = true
			}
			s.Set(key, m, 0)
		case 5:
			// map[string]bool — empty set (edge case)
			s.Set(key, map[string]bool{}, 0)
		case 6:
			// []string with TTL
			ttl := rng.Intn(7200) + 1
			s.Set(key, []string{"a", "b", fmt.Sprintf("c-%d", i)}, ttl)
		}
	}

	// Always include one entry for each explicit awkward case so they appear
	// regardless of numKeys.
	s.Set("empty-string", "", 0)
	s.Set("unicode-value", "日本語テスト™", 0)
	s.Set("unicode-key-日本語", "v", 0)
	s.Set("set-with-false", map[string]bool{"present": true, "absent": false}, 0)
	s.Set("max-ttl", "x", 86400)

	return s
}

// --- Format table for parameterized tests ------------------------------------

type persistenceCase struct {
	name   string
	format Format
}

var persistenceCases = []persistenceCase{
	{"JSON", FormatJSON},
	{"Gob", FormatGob},
}

// --- Roundtrip identity tests ------------------------------------------------

// TestSaveLoadRoundtripIdentity is the primary characterization test.
// It generates a rich store with all value types, saves it, reloads it, and
// asserts that the full canonical dump is identical — covering every field
// that each format claims to persist.
func TestSaveLoadRoundtripIdentity(t *testing.T) {
	for _, tc := range persistenceCases {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			rng := rand.New(rand.NewSource(1234))
			original := buildSeededStore(rng, 60)
			before := canonicalDump(original)

			dir := t.TempDir()
			path := filepath.Join(dir, "store.db")

			if err := Save(original, path, tc.format); err != nil {
				t.Fatalf("Save(%s): %v", tc.name, err)
			}

			reloaded, err := Load(path, tc.format)
			if err != nil {
				t.Fatalf("Load(%s): %v", tc.name, err)
			}

			after := canonicalDump(reloaded)
			if after != before {
				t.Errorf("save→load identity failed for format %s\n--- before ---\n%s\n--- after ---\n%s",
					tc.name, before, after)
			}
		})
	}
}

// TestSaveLoadRoundtripSmallStore checks identity with a minimal store so that
// failures are easy to diagnose without scrolling through 60 entries.
func TestSaveLoadRoundtripSmallStore(t *testing.T) {
	for _, tc := range persistenceCases {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			s := NewStore()
			s.Set("str", "hello", 0)
			s.Set("str-ttl", "world", 30)
			s.Set("slice", []string{"x", "y", "z"}, 0)
			s.Set("set", map[string]bool{"a": true, "b": true}, 0)

			before := canonicalDump(s)
			dir := t.TempDir()
			path := filepath.Join(dir, "small.db")

			if err := Save(s, path, tc.format); err != nil {
				t.Fatalf("Save: %v", err)
			}
			reloaded, err := Load(path, tc.format)
			if err != nil {
				t.Fatalf("Load: %v", err)
			}

			after := canonicalDump(reloaded)
			if after != before {
				t.Errorf("roundtrip mismatch for %s\n--- want ---\n%s\n--- got ---\n%s",
					tc.name, before, after)
			}
		})
	}
}

// TestSaveLoadTTLPersisted specifically verifies that TTL values survive the
// roundtrip.  Omitting this field from canonicalDump would give false
// confidence; this test makes the contract explicit.
func TestSaveLoadTTLPersisted(t *testing.T) {
	for _, tc := range persistenceCases {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			s := NewStore()
			s.Set("no-ttl", "a", 0)
			s.Set("ttl-60", "b", 60)
			s.Set("ttl-3600", "c", 3600)

			dir := t.TempDir()
			path := filepath.Join(dir, "ttl.db")

			if err := Save(s, path, tc.format); err != nil {
				t.Fatalf("Save: %v", err)
			}
			reloaded, err := Load(path, tc.format)
			if err != nil {
				t.Fatalf("Load: %v", err)
			}

			snap := reloaded.Snapshot()

			if snap["no-ttl"].TTLSeconds != 0 {
				t.Errorf("no-ttl: want TTLSeconds=0, got %d", snap["no-ttl"].TTLSeconds)
			}
			if snap["ttl-60"].TTLSeconds != 60 {
				t.Errorf("ttl-60: want TTLSeconds=60, got %d", snap["ttl-60"].TTLSeconds)
			}
			if snap["ttl-3600"].TTLSeconds != 3600 {
				t.Errorf("ttl-3600: want TTLSeconds=3600, got %d", snap["ttl-3600"].TTLSeconds)
			}
		})
	}
}

// TestSaveLoadEmptyStore verifies that an empty store saves and loads without
// error and that the reloaded store is also empty.
func TestSaveLoadEmptyStore(t *testing.T) {
	for _, tc := range persistenceCases {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			s := NewStore()
			dir := t.TempDir()
			path := filepath.Join(dir, "empty.db")

			if err := Save(s, path, tc.format); err != nil {
				t.Fatalf("Save empty store (%s): %v", tc.name, err)
			}

			reloaded, err := Load(path, tc.format)
			if err != nil {
				t.Fatalf("Load empty store (%s): %v", tc.name, err)
			}

			snap := reloaded.Snapshot()
			if len(snap) != 0 {
				t.Errorf("expected empty store after load, got %d entries", len(snap))
			}
		})
	}
}

// TestSaveCreatesFile checks that Save actually writes a file to disk.
func TestSaveCreatesFile(t *testing.T) {
	for _, tc := range persistenceCases {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			s := NewStore()
			s.Set("k", "v", 0)

			dir := t.TempDir()
			path := filepath.Join(dir, "created.db")

			if err := Save(s, path, tc.format); err != nil {
				t.Fatalf("Save: %v", err)
			}

			info, err := os.Stat(path)
			if err != nil {
				t.Fatalf("expected file at %s, got error: %v", path, err)
			}
			if info.Size() == 0 {
				t.Errorf("expected non-empty file, got size 0")
			}
		})
	}
}

// TestLoadNonexistentFileReturnsError verifies that Load returns a non-nil
// error when the file does not exist, not a panic or a silently empty store.
func TestLoadNonexistentFileReturnsError(t *testing.T) {
	for _, tc := range persistenceCases {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			dir := t.TempDir()
			path := filepath.Join(dir, "does-not-exist.db")

			_, err := Load(path, tc.format)
			if err == nil {
				t.Errorf("Load of nonexistent file: expected error, got nil")
			}
		})
	}
}

// TestSaveLoadValueTypes verifies that every value type round-trips correctly
// with explicit per-type assertions to make the contract legible to reviewers.
func TestSaveLoadValueTypes(t *testing.T) {
	for _, tc := range persistenceCases {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			s := NewStore()
			s.Set("string", "hello world", 0)
			s.Set("slice-single", []string{"only"}, 0)
			s.Set("slice-multi", []string{"first", "second", "third"}, 0)
			s.Set("slice-empty", []string{}, 0)
			s.Set("set-single", map[string]bool{"member": true}, 0)
			s.Set("set-multi", map[string]bool{"a": true, "b": true, "c": true}, 0)
			s.Set("set-empty", map[string]bool{}, 0)

			dir := t.TempDir()
			path := filepath.Join(dir, "types.db")

			if err := Save(s, path, tc.format); err != nil {
				t.Fatalf("Save: %v", err)
			}
			reloaded, err := Load(path, tc.format)
			if err != nil {
				t.Fatalf("Load: %v", err)
			}

			snap := reloaded.Snapshot()

			// string
			if v, ok := snap["string"].Value.(string); !ok || v != "hello world" {
				t.Errorf("string: got %T(%v)", snap["string"].Value, snap["string"].Value)
			}

			// slice — non-empty, order matters
			if sl, ok := snap["slice-multi"].Value.([]string); !ok {
				t.Errorf("slice-multi: expected []string, got %T", snap["slice-multi"].Value)
			} else if got, want := strings.Join(sl, ","), "first,second,third"; got != want {
				t.Errorf("slice-multi: got %q, want %q", got, want)
			}

			// slice — empty
			if sl, ok := snap["slice-empty"].Value.([]string); !ok {
				t.Errorf("slice-empty: expected []string, got %T", snap["slice-empty"].Value)
			} else if len(sl) != 0 {
				t.Errorf("slice-empty: expected len 0, got %d", len(sl))
			}

			// set — members present
			if m, ok := snap["set-multi"].Value.(map[string]bool); !ok {
				t.Errorf("set-multi: expected map[string]bool, got %T", snap["set-multi"].Value)
			} else {
				for _, member := range []string{"a", "b", "c"} {
					if !m[member] {
						t.Errorf("set-multi: member %q missing", member)
					}
				}
				if len(m) != 3 {
					t.Errorf("set-multi: expected 3 members, got %d", len(m))
				}
			}

			// set — empty
			if m, ok := snap["set-empty"].Value.(map[string]bool); !ok {
				t.Errorf("set-empty: expected map[string]bool, got %T", snap["set-empty"].Value)
			} else if len(m) != 0 {
				t.Errorf("set-empty: expected 0 members, got %d", len(m))
			}
		})
	}
}

// TestSaveLoadKeyCount verifies that the number of keys is preserved exactly —
// neither keys are lost nor phantom keys introduced.
func TestSaveLoadKeyCount(t *testing.T) {
	for _, tc := range persistenceCases {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			rng := rand.New(rand.NewSource(9999))
			s := buildSeededStore(rng, 40)
			want := len(s.Snapshot())

			dir := t.TempDir()
			path := filepath.Join(dir, "count.db")

			if err := Save(s, path, tc.format); err != nil {
				t.Fatalf("Save: %v", err)
			}
			reloaded, err := Load(path, tc.format)
			if err != nil {
				t.Fatalf("Load: %v", err)
			}

			got := len(reloaded.Snapshot())
			if got != want {
				t.Errorf("key count: want %d, got %d", want, got)
			}
		})
	}
}

// TestSaveLoadUnicodeKeys verifies that keys containing multi-byte Unicode
// characters survive the roundtrip without corruption or key collisions.
func TestSaveLoadUnicodeKeys(t *testing.T) {
	for _, tc := range persistenceCases {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			s := NewStore()
			unicodeKeys := map[string]string{
				"日本語":         "japanese",
				"中文":          "chinese",
				"한국어":         "korean",
				"émoji🎉":      "emoji",
				"café":        "accented",
				"naïve":       "combining",
				"key\x00null": "with-null-byte",
			}
			for k, v := range unicodeKeys {
				s.Set(k, v, 0)
			}

			dir := t.TempDir()
			path := filepath.Join(dir, "unicode.db")

			if err := Save(s, path, tc.format); err != nil {
				t.Fatalf("Save: %v", err)
			}
			reloaded, err := Load(path, tc.format)
			if err != nil {
				t.Fatalf("Load: %v", err)
			}

			snap := reloaded.Snapshot()
			for k, wantV := range unicodeKeys {
				entry, ok := snap[k]
				if !ok {
					t.Errorf("key %q missing after reload", k)
					continue
				}
				if gotV, ok := entry.Value.(string); !ok || gotV != wantV {
					t.Errorf("key %q: want %q, got %v", k, wantV, entry.Value)
				}
			}
		})
	}
}

// TestFormatsDifferentFiles verifies that JSON and Gob files are not
// interchangeable — loading a JSON file as Gob (or vice-versa) must return
// an error, not silently return a wrong store.
func TestFormatsDifferentFiles(t *testing.T) {
	s := NewStore()
	s.Set("k", "v", 0)

	dir := t.TempDir()
	jsonPath := filepath.Join(dir, "store.json")
	gobPath := filepath.Join(dir, "store.gob")

	if err := Save(s, jsonPath, FormatJSON); err != nil {
		t.Fatalf("Save JSON: %v", err)
	}
	if err := Save(s, gobPath, FormatGob); err != nil {
		t.Fatalf("Save Gob: %v", err)
	}

	if _, err := Load(gobPath, FormatJSON); err == nil {
		t.Error("Load Gob file as JSON: expected error, got nil")
	}
	if _, err := Load(jsonPath, FormatGob); err == nil {
		t.Error("Load JSON file as Gob: expected error, got nil")
	}
}

// TestSaveLoadDeterministic verifies that saving the same store twice and
// reloading both files produces identical canonical dumps — ensuring no
// nondeterminism (e.g. random padding, timestamp injection) in the format.
func TestSaveLoadDeterministic(t *testing.T) {
	for _, tc := range persistenceCases {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			rng := rand.New(rand.NewSource(42))
			s := buildSeededStore(rng, 20)

			dir := t.TempDir()
			path1 := filepath.Join(dir, "a.db")
			path2 := filepath.Join(dir, "b.db")

			if err := Save(s, path1, tc.format); err != nil {
				t.Fatalf("Save 1: %v", err)
			}
			if err := Save(s, path2, tc.format); err != nil {
				t.Fatalf("Save 2: %v", err)
			}

			r1, err := Load(path1, tc.format)
			if err != nil {
				t.Fatalf("Load 1: %v", err)
			}
			r2, err := Load(path2, tc.format)
			if err != nil {
				t.Fatalf("Load 2: %v", err)
			}

			d1 := canonicalDump(r1)
			d2 := canonicalDump(r2)
			if d1 != d2 {
				t.Errorf("two saves of the same store produced different dumps for %s\n--- dump1 ---\n%s\n--- dump2 ---\n%s",
					tc.name, d1, d2)
			}
		})
	}
}

// TestSaveOverwritesExistingFile verifies that Save replaces an existing file
// rather than appending to it, so a second save of a smaller store does not
// leave stale entries from the first.
func TestSaveOverwritesExistingFile(t *testing.T) {
	for _, tc := range persistenceCases {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			large := NewStore()
			for i := 0; i < 20; i++ {
				large.Set(fmt.Sprintf("big-key-%d", i), fmt.Sprintf("val-%d", i), 0)
			}

			small := NewStore()
			small.Set("only-key", "only-val", 0)

			dir := t.TempDir()
			path := filepath.Join(dir, "overwrite.db")

			// Save the large store first.
			if err := Save(large, path, tc.format); err != nil {
				t.Fatalf("Save large: %v", err)
			}
			// Overwrite with the small store.
			if err := Save(small, path, tc.format); err != nil {
				t.Fatalf("Save small: %v", err)
			}

			reloaded, err := Load(path, tc.format)
			if err != nil {
				t.Fatalf("Load after overwrite: %v", err)
			}

			want := canonicalDump(small)
			got := canonicalDump(reloaded)
			if got != want {
				t.Errorf("after overwrite, expected small store\n--- want ---\n%s\n--- got ---\n%s", want, got)
			}
		})
	}
}

// TestSaveLoadSliceOrder verifies that []string values preserve insertion order
// across a roundtrip; order is part of the value contract.
func TestSaveLoadSliceOrder(t *testing.T) {
	for _, tc := range persistenceCases {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			s := NewStore()
			ordered := []string{"first", "second", "third", "fourth", "fifth"}
			s.Set("ordered", ordered, 0)

			dir := t.TempDir()
			path := filepath.Join(dir, "order.db")

			if err := Save(s, path, tc.format); err != nil {
				t.Fatalf("Save: %v", err)
			}
			reloaded, err := Load(path, tc.format)
			if err != nil {
				t.Fatalf("Load: %v", err)
			}

			snap := reloaded.Snapshot()
			got, ok := snap["ordered"].Value.([]string)
			if !ok {
				t.Fatalf("expected []string, got %T", snap["ordered"].Value)
			}
			if len(got) != len(ordered) {
				t.Fatalf("slice length: want %d, got %d", len(ordered), len(got))
			}
			for i := range ordered {
				if got[i] != ordered[i] {
					t.Errorf("index %d: want %q, got %q", i, ordered[i], got[i])
				}
			}
		})
	}
}
