package store

import (
	"encoding/json"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"testing"
)

// snapshotStore renders a Store's snapshot as a stable, sorted string suitable
// for snapshot-style assertions. Sorting keys ensures determinism regardless
// of map iteration order.
func snapshotStore(t *testing.T, s *Store) string {
	t.Helper()
	snap := s.Snapshot()
	keys := make([]string, 0, len(snap))
	for k := range snap {
		keys = append(keys, k)
	}
	sort.Strings(keys)

	var sb strings.Builder
	for _, k := range keys {
		entry := snap[k]
		sb.WriteString(k)
		sb.WriteString(": ")
		switch v := entry.Value.(type) {
		case string:
			sb.WriteString("string(")
			sb.WriteString(v)
			sb.WriteString(")")
		case []string:
			sorted := make([]string, len(v))
			copy(sorted, v)
			sort.Strings(sorted)
			sb.WriteString("[]string(")
			sb.WriteString(strings.Join(sorted, ","))
			sb.WriteString(")")
		case map[string]bool:
			setKeys := make([]string, 0, len(v))
			for sk := range v {
				setKeys = append(setKeys, sk)
			}
			sort.Strings(setKeys)
			sb.WriteString("set(")
			sb.WriteString(strings.Join(setKeys, ","))
			sb.WriteString(")")
		default:
			sb.WriteString("unknown")
		}
		if entry.TTLSeconds > 0 {
			sb.WriteString(" ttl>0")
		}
		sb.WriteString("\n")
	}
	return sb.String()
}

// goldenPath returns the path to the golden file for a given test name.
func goldenPath(t *testing.T, name string) string {
	t.Helper()
	dir := filepath.Join("testdata", "golden")
	return filepath.Join(dir, name+".golden")
}

// assertGolden compares actual against the stored golden file for the given
// test name. When the UPDATE_SNAPSHOTS environment variable is set, it writes
// the actual output as the new baseline (the promote workflow).
func assertGolden(t *testing.T, name, actual string) {
	t.Helper()
	path := goldenPath(t, name)

	if os.Getenv("UPDATE_SNAPSHOTS") == "true" {
		if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
			t.Fatalf("create golden dir: %v", err)
		}
		if err := os.WriteFile(path, []byte(actual), 0o644); err != nil {
			t.Fatalf("write golden file: %v", err)
		}
		t.Logf("updated golden file: %s", path)
		return
	}

	expected, err := os.ReadFile(path)
	if os.IsNotExist(err) {
		// Auto-baseline: write on first run, then let the developer review.
		if err2 := os.MkdirAll(filepath.Dir(path), 0o755); err2 != nil {
			t.Fatalf("create golden dir: %v", err2)
		}
		if err2 := os.WriteFile(path, []byte(actual), 0o644); err2 != nil {
			t.Fatalf("write initial golden file: %v", err2)
		}
		t.Logf("created initial golden baseline: %s — review and commit", path)
		return
	}
	if err != nil {
		t.Fatalf("read golden file: %v", err)
	}

	if string(expected) != actual {
		t.Errorf("golden mismatch for %q\n--- want ---\n%s\n--- got ---\n%s", name, expected, actual)
	}
}

// tmpFile returns a temporary file path with the given suffix and registers
// cleanup so it is removed after the test.
func tmpFile(t *testing.T, suffix string) string {
	t.Helper()
	f, err := os.CreateTemp(t.TempDir(), "store-*"+suffix)
	if err != nil {
		t.Fatalf("create temp file: %v", err)
	}
	f.Close()
	return f.Name()
}

// --------------------------------------------------------------------------
// Round-trip: JSON
// --------------------------------------------------------------------------

func TestSaveLoad_JSON_StringValue_RoundTrip(t *testing.T) {
	s := NewStore()
	s.Set("greeting", "hello", 0)

	path := tmpFile(t, ".json")
	if err := Save(s, path, FormatJSON); err != nil {
		t.Fatalf("Save: %v", err)
	}

	loaded, err := Load(path, FormatJSON)
	if err != nil {
		t.Fatalf("Load: %v", err)
	}

	val, ok := loaded.Get("greeting")
	if !ok {
		t.Fatal("expected key 'greeting' to exist after round-trip")
	}
	got, ok := val.(string)
	if !ok {
		t.Fatalf("expected string value, got %T", val)
	}
	if got != "hello" {
		t.Errorf("string value after round-trip: got %q, want %q", got, "hello")
	}
}

func TestSaveLoad_JSON_SliceValue_RoundTrip(t *testing.T) {
	s := NewStore()
	s.Set("tags", []string{"go", "testing", "persistence"}, 0)

	path := tmpFile(t, ".json")
	if err := Save(s, path, FormatJSON); err != nil {
		t.Fatalf("Save: %v", err)
	}

	loaded, err := Load(path, FormatJSON)
	if err != nil {
		t.Fatalf("Load: %v", err)
	}

	val, ok := loaded.Get("tags")
	if !ok {
		t.Fatal("expected key 'tags' to exist after round-trip")
	}
	got, ok := val.([]string)
	if !ok {
		t.Fatalf("expected []string, got %T", val)
	}
	sort.Strings(got)
	want := []string{"go", "persistence", "testing"}
	if strings.Join(got, ",") != strings.Join(want, ",") {
		t.Errorf("[]string round-trip: got %v, want %v", got, want)
	}
}

func TestSaveLoad_JSON_SetValue_RoundTrip(t *testing.T) {
	s := NewStore()
	s.Set("flags", map[string]bool{"alpha": true, "beta": false, "gamma": true}, 0)

	path := tmpFile(t, ".json")
	if err := Save(s, path, FormatJSON); err != nil {
		t.Fatalf("Save: %v", err)
	}

	loaded, err := Load(path, FormatJSON)
	if err != nil {
		t.Fatalf("Load: %v", err)
	}

	val, ok := loaded.Get("flags")
	if !ok {
		t.Fatal("expected key 'flags' to exist after round-trip")
	}
	got, ok := val.(map[string]bool)
	if !ok {
		t.Fatalf("expected map[string]bool, got %T", val)
	}
	if got["alpha"] != true {
		t.Errorf("flags[alpha]: got %v, want true", got["alpha"])
	}
	if got["beta"] != false {
		t.Errorf("flags[beta]: got %v, want false", got["beta"])
	}
	if got["gamma"] != true {
		t.Errorf("flags[gamma]: got %v, want true", got["gamma"])
	}
}

// --------------------------------------------------------------------------
// Round-trip: Gob
// --------------------------------------------------------------------------

func TestSaveLoad_Gob_StringValue_RoundTrip(t *testing.T) {
	s := NewStore()
	s.Set("city", "Lagos", 0)

	path := tmpFile(t, ".gob")
	if err := Save(s, path, FormatGob); err != nil {
		t.Fatalf("Save: %v", err)
	}

	loaded, err := Load(path, FormatGob)
	if err != nil {
		t.Fatalf("Load: %v", err)
	}

	val, ok := loaded.Get("city")
	if !ok {
		t.Fatal("expected key 'city' after gob round-trip")
	}
	got, ok := val.(string)
	if !ok {
		t.Fatalf("expected string, got %T", val)
	}
	if got != "Lagos" {
		t.Errorf("gob string round-trip: got %q, want %q", got, "Lagos")
	}
}

func TestSaveLoad_Gob_SliceValue_RoundTrip(t *testing.T) {
	s := NewStore()
	s.Set("colors", []string{"red", "green", "blue"}, 0)

	path := tmpFile(t, ".gob")
	if err := Save(s, path, FormatGob); err != nil {
		t.Fatalf("Save: %v", err)
	}

	loaded, err := Load(path, FormatGob)
	if err != nil {
		t.Fatalf("Load: %v", err)
	}

	val, ok := loaded.Get("colors")
	if !ok {
		t.Fatal("expected key 'colors' after gob round-trip")
	}
	got, ok := val.([]string)
	if !ok {
		t.Fatalf("expected []string, got %T", val)
	}
	sort.Strings(got)
	want := []string{"blue", "green", "red"}
	if strings.Join(got, ",") != strings.Join(want, ",") {
		t.Errorf("gob []string round-trip: got %v, want %v", got, want)
	}
}

func TestSaveLoad_Gob_SetValue_RoundTrip(t *testing.T) {
	s := NewStore()
	s.Set("perms", map[string]bool{"read": true, "write": true, "exec": false}, 0)

	path := tmpFile(t, ".gob")
	if err := Save(s, path, FormatGob); err != nil {
		t.Fatalf("Save: %v", err)
	}

	loaded, err := Load(path, FormatGob)
	if err != nil {
		t.Fatalf("Load: %v", err)
	}

	val, ok := loaded.Get("perms")
	if !ok {
		t.Fatal("expected key 'perms' after gob round-trip")
	}
	got, ok := val.(map[string]bool)
	if !ok {
		t.Fatalf("expected map[string]bool, got %T", val)
	}
	if !got["read"] {
		t.Errorf("perms[read] should be true")
	}
	if !got["write"] {
		t.Errorf("perms[write] should be true")
	}
	if got["exec"] {
		t.Errorf("perms[exec] should be false")
	}
}

// --------------------------------------------------------------------------
// TTL persistence
// --------------------------------------------------------------------------

func TestSaveLoad_JSON_TTLIsPreserved(t *testing.T) {
	s := NewStore()
	s.Set("session", "tok123", 3600)
	s.Set("permanent", "value", 0)

	path := tmpFile(t, ".json")
	if err := Save(s, path, FormatJSON); err != nil {
		t.Fatalf("Save: %v", err)
	}

	loaded, err := Load(path, FormatJSON)
	if err != nil {
		t.Fatalf("Load: %v", err)
	}

	snap := loaded.Snapshot()

	sessionEntry, ok := snap["session"]
	if !ok {
		t.Fatal("expected 'session' key after load")
	}
	if sessionEntry.TTLSeconds != 3600 {
		t.Errorf("TTL for 'session': got %d, want 3600", sessionEntry.TTLSeconds)
	}

	permanentEntry, ok := snap["permanent"]
	if !ok {
		t.Fatal("expected 'permanent' key after load")
	}
	if permanentEntry.TTLSeconds != 0 {
		t.Errorf("TTL for 'permanent': got %d, want 0", permanentEntry.TTLSeconds)
	}
}

func TestSaveLoad_Gob_TTLIsPreserved(t *testing.T) {
	s := NewStore()
	s.Set("cache", "data", 60)

	path := tmpFile(t, ".gob")
	if err := Save(s, path, FormatGob); err != nil {
		t.Fatalf("Save: %v", err)
	}

	loaded, err := Load(path, FormatGob)
	if err != nil {
		t.Fatalf("Load: %v", err)
	}

	snap := loaded.Snapshot()
	entry, ok := snap["cache"]
	if !ok {
		t.Fatal("expected 'cache' key after gob load")
	}
	if entry.TTLSeconds != 60 {
		t.Errorf("TTL for 'cache': got %d, want 60", entry.TTLSeconds)
	}
}

// --------------------------------------------------------------------------
// Multi-key store snapshot golden tests
// The full store state has many fields; snapshot testing is appropriate here.
// --------------------------------------------------------------------------

func TestSaveLoad_JSON_MultiKeyStore_MatchesGolden(t *testing.T) {
	s := NewStore()
	s.Set("name", "alice", 0)
	s.Set("roles", []string{"admin", "editor"}, 0)
	s.Set("features", map[string]bool{"darkMode": true, "betaUI": false}, 0)
	s.Set("token", "abc123", 900)

	path := tmpFile(t, ".json")
	if err := Save(s, path, FormatJSON); err != nil {
		t.Fatalf("Save: %v", err)
	}

	loaded, err := Load(path, FormatJSON)
	if err != nil {
		t.Fatalf("Load: %v", err)
	}

	assertGolden(t, "multikey-json-round-trip", snapshotStore(t, loaded))
}

func TestSaveLoad_Gob_MultiKeyStore_MatchesGolden(t *testing.T) {
	s := NewStore()
	s.Set("name", "bob", 0)
	s.Set("scores", []string{"100", "200", "150"}, 0)
	s.Set("flags", map[string]bool{"active": true, "banned": false}, 0)
	s.Set("key", "secret", 7200)

	path := tmpFile(t, ".gob")
	if err := Save(s, path, FormatGob); err != nil {
		t.Fatalf("Save: %v", err)
	}

	loaded, err := Load(path, FormatGob)
	if err != nil {
		t.Fatalf("Load: %v", err)
	}

	assertGolden(t, "multikey-gob-round-trip", snapshotStore(t, loaded))
}

// --------------------------------------------------------------------------
// Empty store
// --------------------------------------------------------------------------

func TestSaveLoad_JSON_EmptyStore_RoundTrip(t *testing.T) {
	s := NewStore()

	path := tmpFile(t, ".json")
	if err := Save(s, path, FormatJSON); err != nil {
		t.Fatalf("Save empty store: %v", err)
	}

	loaded, err := Load(path, FormatJSON)
	if err != nil {
		t.Fatalf("Load empty store: %v", err)
	}

	snap := loaded.Snapshot()
	if len(snap) != 0 {
		t.Errorf("expected empty snapshot after round-trip, got %d entries", len(snap))
	}
}

func TestSaveLoad_Gob_EmptyStore_RoundTrip(t *testing.T) {
	s := NewStore()

	path := tmpFile(t, ".gob")
	if err := Save(s, path, FormatGob); err != nil {
		t.Fatalf("Save empty store (gob): %v", err)
	}

	loaded, err := Load(path, FormatGob)
	if err != nil {
		t.Fatalf("Load empty store (gob): %v", err)
	}

	snap := loaded.Snapshot()
	if len(snap) != 0 {
		t.Errorf("expected empty snapshot after gob round-trip, got %d entries", len(snap))
	}
}

// --------------------------------------------------------------------------
// Key count preserved across round-trips
// --------------------------------------------------------------------------

func TestSaveLoad_JSON_AllKeysArePresent(t *testing.T) {
	keys := []string{"alpha", "beta", "gamma", "delta", "epsilon"}
	s := NewStore()
	for _, k := range keys {
		s.Set(k, "val-"+k, 0)
	}

	path := tmpFile(t, ".json")
	if err := Save(s, path, FormatJSON); err != nil {
		t.Fatalf("Save: %v", err)
	}

	loaded, err := Load(path, FormatJSON)
	if err != nil {
		t.Fatalf("Load: %v", err)
	}

	snap := loaded.Snapshot()
	if len(snap) != len(keys) {
		t.Errorf("key count after round-trip: got %d, want %d", len(snap), len(keys))
	}
	for _, k := range keys {
		if _, ok := snap[k]; !ok {
			t.Errorf("expected key %q to be present after round-trip", k)
		}
	}
}

func TestSaveLoad_Gob_AllKeysArePresent(t *testing.T) {
	keys := []string{"one", "two", "three"}
	s := NewStore()
	for _, k := range keys {
		s.Set(k, "val-"+k, 0)
	}

	path := tmpFile(t, ".gob")
	if err := Save(s, path, FormatGob); err != nil {
		t.Fatalf("Save: %v", err)
	}

	loaded, err := Load(path, FormatGob)
	if err != nil {
		t.Fatalf("Load: %v", err)
	}

	snap := loaded.Snapshot()
	if len(snap) != len(keys) {
		t.Errorf("key count after gob round-trip: got %d, want %d", len(snap), len(keys))
	}
}

// --------------------------------------------------------------------------
// Load from non-existent file returns an error
// --------------------------------------------------------------------------

func TestLoad_JSON_NonExistentFile_ReturnsError(t *testing.T) {
	_, err := Load("/nonexistent/path/store.json", FormatJSON)
	if err == nil {
		t.Error("expected error loading non-existent JSON file, got nil")
	}
}

func TestLoad_Gob_NonExistentFile_ReturnsError(t *testing.T) {
	_, err := Load("/nonexistent/path/store.gob", FormatGob)
	if err == nil {
		t.Error("expected error loading non-existent gob file, got nil")
	}
}

// --------------------------------------------------------------------------
// Load from a corrupt file returns an error (not a panic)
// --------------------------------------------------------------------------

func TestLoad_JSON_CorruptFile_ReturnsError(t *testing.T) {
	path := tmpFile(t, ".json")
	if err := os.WriteFile(path, []byte("{invalid json{{{{"), 0o644); err != nil {
		t.Fatalf("write corrupt file: %v", err)
	}

	_, err := Load(path, FormatJSON)
	if err == nil {
		t.Error("expected error loading corrupt JSON, got nil")
	}
}

func TestLoad_Gob_CorruptFile_ReturnsError(t *testing.T) {
	path := tmpFile(t, ".gob")
	if err := os.WriteFile(path, []byte("not gob data at all"), 0o644); err != nil {
		t.Fatalf("write corrupt file: %v", err)
	}

	_, err := Load(path, FormatGob)
	if err == nil {
		t.Error("expected error loading corrupt gob, got nil")
	}
}

// --------------------------------------------------------------------------
// Saving to an unwritable path returns an error (not a panic)
// --------------------------------------------------------------------------

func TestSave_JSON_UnwritablePath_ReturnsError(t *testing.T) {
	s := NewStore()
	s.Set("k", "v", 0)

	err := Save(s, "/nonexistent/directory/store.json", FormatJSON)
	if err == nil {
		t.Error("expected error saving to unwritable path, got nil")
	}
}

func TestSave_Gob_UnwritablePath_ReturnsError(t *testing.T) {
	s := NewStore()
	s.Set("k", "v", 0)

	err := Save(s, "/nonexistent/directory/store.gob", FormatGob)
	if err == nil {
		t.Error("expected error saving to unwritable path, got nil")
	}
}

// --------------------------------------------------------------------------
// JSON file is human-readable (explicit structural assertion, not snapshot)
// This is a security/contract property: the serialised form must be JSON.
// --------------------------------------------------------------------------

func TestSave_JSON_ProducesValidJSONOnDisk(t *testing.T) {
	s := NewStore()
	s.Set("hello", "world", 0)

	path := tmpFile(t, ".json")
	if err := Save(s, path, FormatJSON); err != nil {
		t.Fatalf("Save: %v", err)
	}

	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read saved file: %v", err)
	}

	var raw interface{}
	if err := json.Unmarshal(data, &raw); err != nil {
		t.Errorf("saved file is not valid JSON: %v\ncontents:\n%s", err, data)
	}
}

// --------------------------------------------------------------------------
// Overwrite: saving to an existing path replaces the old contents
// --------------------------------------------------------------------------

func TestSave_JSON_OverwriteExistingFile_ReplacesContents(t *testing.T) {
	s1 := NewStore()
	s1.Set("key", "first", 0)

	path := tmpFile(t, ".json")
	if err := Save(s1, path, FormatJSON); err != nil {
		t.Fatalf("first Save: %v", err)
	}

	s2 := NewStore()
	s2.Set("key", "second", 0)
	if err := Save(s2, path, FormatJSON); err != nil {
		t.Fatalf("second Save: %v", err)
	}

	loaded, err := Load(path, FormatJSON)
	if err != nil {
		t.Fatalf("Load after overwrite: %v", err)
	}

	val, ok := loaded.Get("key")
	if !ok {
		t.Fatal("expected 'key' after overwrite")
	}
	got, _ := val.(string)
	if got != "second" {
		t.Errorf("value after overwrite: got %q, want %q", got, "second")
	}
}

// --------------------------------------------------------------------------
// Cross-format isolation: a file saved as JSON cannot be loaded as Gob
// --------------------------------------------------------------------------

func TestLoad_JSON_FileAsGob_ReturnsError(t *testing.T) {
	s := NewStore()
	s.Set("x", "y", 0)

	path := tmpFile(t, ".json")
	if err := Save(s, path, FormatJSON); err != nil {
		t.Fatalf("Save as JSON: %v", err)
	}

	_, err := Load(path, FormatGob)
	if err == nil {
		t.Error("expected error loading a JSON file as gob, got nil")
	}
}

func TestLoad_Gob_FileAsJSON_ReturnsError(t *testing.T) {
	s := NewStore()
	s.Set("x", "y", 0)

	path := tmpFile(t, ".gob")
	if err := Save(s, path, FormatGob); err != nil {
		t.Fatalf("Save as gob: %v", err)
	}

	_, err := Load(path, FormatJSON)
	if err == nil {
		t.Error("expected error loading a gob file as JSON, got nil")
	}
}

// --------------------------------------------------------------------------
// Snapshot does not share mutable state with the loaded store
// Mutating the snapshot must not affect a subsequent Snapshot call.
// --------------------------------------------------------------------------

func TestSaveLoad_JSON_SnapshotIsIsolatedFromStore(t *testing.T) {
	s := NewStore()
	s.Set("count", "1", 0)

	path := tmpFile(t, ".json")
	if err := Save(s, path, FormatJSON); err != nil {
		t.Fatalf("Save: %v", err)
	}

	loaded, err := Load(path, FormatJSON)
	if err != nil {
		t.Fatalf("Load: %v", err)
	}

	snap1 := loaded.Snapshot()
	// Mutate the returned map.
	snap1["injected"] = Entry{Value: "evil"}

	snap2 := loaded.Snapshot()
	if _, found := snap2["injected"]; found {
		t.Error("mutating snapshot map leaked back into the store")
	}
}
