{
  "decision": "approve",
  "changes": [
    {
      "target": "Endpoint test fixture and assertions",
      "action": "Replace the fake with temporary SQLite initialized from the production migrations.",
      "details": "Seed two records with distinct lookup keys and returned IDs in the same database. Call the normal endpoint with each key and a third valid but absent key. Assert the exact returned IDs for each match and the endpoint's documented no-match response. Take expected values directly from the seeded examples."
    },
    {
      "target": "SQL substring assertions",
      "action": "Remove assertions that pin incidental query spelling.",
      "details": "Carry any distinct caller-visible rule encoded by an old assertion into the endpoint tests. Retain a SQL-level assertion if it enforces an independently specified requirement."
    }
  ],
  "retained_contracts": [
    "Each matching request returns its own record exactly once and excludes the other record.",
    "An absent key produces the specified empty or missing response even when the database contains records.",
    "Preserve any independently specified response fields, status or ordering already covered by this suite."
  ],
  "validation": [
    "Run the focused endpoint suite with its existing runner. Confirm all three requests execute and the expected responses pass.",
    "In a scratch copy, bind the first record's key for every lookup while keeping the SQL text intact. Run the old and repaired tests against that same change. Expect the old checks to pass. The repaired suite should fail because the second and absent keys now return the first record. Restore the binding and rerun the focused suite."
  ],
  "cost_and_stop": "Keep the six-second repair in the existing suite. Stop after the wrong-binding check exposes the result mismatch and the restored suite passes.",
  "rationale": "The fake supplies rows independently of the predicate. Executing the query against the migrated schema makes the request's bound value determine the observed result and leaves equivalent SQL spellings free to change."
}
