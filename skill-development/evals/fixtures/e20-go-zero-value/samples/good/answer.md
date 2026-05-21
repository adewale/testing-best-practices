No. In Go, unexported fields push outside callers through NewEmail, but the zero value still exists: `var e Email`. That means invalid states are not fully unconstructible unless the zero value is valid by design or every use checks validity.

Keep constructor/boundary tests for NewEmail/ParseEmail rejecting malformed addresses, add coverage for zero-value behavior, and only delete downstream invalid-email tests after the boundary and zero-value contract are covered.
