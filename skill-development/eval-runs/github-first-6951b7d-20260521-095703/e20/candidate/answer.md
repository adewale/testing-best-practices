No. In Go every type has a zero value, so callers can still create `var e Email`, `Email{}` (where allowed), `new(Email)`, or receive zero values from containers/deserialization paths.

Keep invalid-email tests. At minimum test:
- `NewEmail` rejects empty/malformed emails.
- The zero-value `Email` is either explicitly valid by design or safely rejected/handled by all methods.
- Public APIs cannot be tricked by a zero-value `Email`.

Only delete tests that no longer exercise reachable behavior; do not remove sad-path validation tests just because fields are unexported.
