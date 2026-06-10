package store

import (
	"fmt"
	"math/rand"
	"path/filepath"
	"reflect"
	"testing"
)

func buildStore(rng *rand.Rand, n int) *Store {
	s := NewStore()
	for i := 0; i < n; i++ {
		ttl := 0
		if rng.Intn(2) == 1 {
			ttl = rng.Intn(9999) + 1
		}
		switch rng.Intn(3) {
		case 0:
			s.Set(fmt.Sprintf("s%d", i), fmt.Sprintf("v%d", rng.Intn(1000000)), ttl)
		case 1:
			vals := make([]string, rng.Intn(5))
			for j := range vals {
				vals[j] = fmt.Sprintf("%d", rng.Intn(100))
			}
			s.Set(fmt.Sprintf("l%d", i), vals, ttl)
		default:
			set := map[string]bool{}
			for j := 0; j < rng.Intn(5); j++ {
				set[fmt.Sprintf("%d", rng.Intn(100))] = true
			}
			s.Set(fmt.Sprintf("x%d", i), set, ttl)
		}
	}
	return s
}

func TestSaveLoadRoundtripIdentity(t *testing.T) {
	for _, format := range []Format{FormatJSON, FormatGob} {
		t.Run(fmt.Sprintf("format-%v", format), func(t *testing.T) {
			rng := rand.New(rand.NewSource(1234))
			s := buildStore(rng, 60)
			before := s.Snapshot()

			path := filepath.Join(t.TempDir(), "db")
			if err := Save(s, path, format); err != nil {
				t.Fatalf("save: %v", err)
			}
			reloaded, err := Load(path, format)
			if err != nil {
				t.Fatalf("load: %v", err)
			}
			if !reflect.DeepEqual(reloaded.Snapshot(), before) {
				t.Fatalf("whole-state mismatch after %v roundtrip (ttl included)", format)
			}
		})
	}
}
