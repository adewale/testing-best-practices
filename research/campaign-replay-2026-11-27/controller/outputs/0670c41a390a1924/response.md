{
  "decision": "approve",
  "changes": [
    {
      "target": "SQLite endpoint test suite",
      "action": "Replace the unconditional fake and SQL-substring assertions with the proposed endpoint test.",
      "details": "Apply the production migrations to an isolated temporary database and seed two records with distinct filter values and recognizable IDs. With both rows present, call the endpoint for each value and assert the exact returned IDs against fixture literals. A third, valid but absent value must produce the endpoint's documented no-match response. Close the database before removing the temporary directory."
    }
  ],
  "retained_contracts": [
    "Each lookup returns only its matching record, and a valid lookup with no match has the documented result.",
    "Review each displaced assertion for a distinct contract. If one guards another promised behavior, retain that behavior through an observable assertion. SQL spelling alone needs no coverage."
  ],
  "validation": [
    "Set suite to the changed test file's path. Temporarily widen the filter while keeping its parameter bindings valid and run pnpm test \"$suite\" --maxWorkers=1. Confirm a result assertion fails because an unrelated record reaches the response.",
    "Restore the predicate and run time pnpm test \"$suite\" --maxWorkers=1. Confirm both lookups and the no-match case pass, and record wall time.",
    "Run git diff --check."
  ],
  "cost_and_stop": "Six seconds is reasonable for exercising the real query and migrated schema. Keep the proof in this suite and stop after the focused validation.",
  "rationale": "The fake can return the expected rows even when the filter is broken. With competing rows in real SQLite, the endpoint's response exposes a filtering regression and equivalent query rewrites can still pass."
}
