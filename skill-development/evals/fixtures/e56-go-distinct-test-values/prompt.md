# E56 — Write: unit tests for an in-memory key-value store

Write unit tests for this Go package. Put your tests in `kvstore_test.go`
using `package kvstore` (internal test package), following standard Go testing
conventions. Cover the behavior of `Put`, `Get`, and `Delete`.

`kvstore.go`:

```go
package kvstore

// Store is an in-memory key-value store.
type Store struct {
	m map[string]string
}

// New returns an empty Store.
func New() *Store { return &Store{m: map[string]string{}} }

// Put stores value under key, replacing any existing value.
func (s *Store) Put(key, value string) { s.m[key] = value }

// Get returns the value stored under key and whether it was present.
func (s *Store) Get(key string) (string, bool) {
	v, ok := s.m[key]
	return v, ok
}

// Delete removes key. Deleting an absent key is a no-op.
func (s *Store) Delete(key string) { delete(s.m, key) }
```

The deliverable is the `kvstore_test.go` file.
