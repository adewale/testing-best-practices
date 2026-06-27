# E48 Go store persistence

Package `store`: `Store` holds string keys; values are string, []string, or map[string]bool (a set); optional per-key TTL. `Save(s *Store, path string, format Format)` and `Load(path string, format Format)` support `FormatJSON` and `FormatGob`. `s.Snapshot() map[string]Entry` returns the full contents. Add Go tests for persistence using the standard `testing` package.
