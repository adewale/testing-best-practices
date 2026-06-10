package store

import (
	"path/filepath"
	"testing"
)

func TestSaveLoad(t *testing.T) {
	s := NewStore()
	s.Set("a", "1", 0)
	path := filepath.Join(t.TempDir(), "db")
	Save(s, path, FormatJSON)
	r, _ := Load(path, FormatJSON)
	if v, _ := r.Get("a"); v != "1" {
		t.Errorf("got %v", v)
	}
}
