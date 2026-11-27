{
  "decision": "approve",
  "changes": [
    {
      "target": "Endpoint suite",
      "action": "Replace the SQL-substring checks with endpoint response assertions.",
      "details": "Apply the real migrations to a fresh temporary SQLite database and connect the endpoint to it through its existing setup. Seed A and B together with distinct lookup keys and distinguishable returned values. Request A, B and an unused valid key. Assert exact record membership and the relevant returned fields against literal fixture expectations."
    }
  ],
  "retained_contracts": [
    "A lookup for A returns only A, a lookup for B returns only B, and the unused key produces the endpoint's established no-match status and payload.",
    "Keep any existing independent wiring or database-error response checks. A controlled failure double can still exercise an error path. Retire assertions whose sole expectation is SQL spelling."
  ],
  "validation": [
    "Run the existing focused endpoint suite before and after the repair. Confirm the repaired suite executes all three requests against the migrated database and passes.",
    "In a scratch copy, broaden the predicate so every row qualifies while preserving the original SQL substring and bindings. Run the old and repaired tests against that same fault. Record the old result and verify the repaired test fails on an unexpected record in a matching or no-match response.",
    "Restore the correct predicate with a harmless SQL whitespace change in the scratch copy. Rerun the repaired suite and expect the same passing responses. Discard the scratch change."
  ],
  "cost_and_stop": "The stated six-second cost fits the existing suite. Ship the test-only change after the focused checks and ordinary required CI pass. The existing test route is sufficient.",
  "rationale": "The fake supplies the expected rows even when filtering is broken. With both records present in real SQLite, the endpoint must filter and bind the lookup key correctly to return the three expected responses."
}
