{
  "decision": "reject",
  "changes": [
    {
      "target": "Historical receipt verifier",
      "action": "Verify the archive against the original receipt.",
      "details": "Read each listed candidate output as bytes, hash it with the receipt's algorithm, and compare it with that candidate's recorded digest. Recompute the recorded totals from the archived records using the evaluation's aggregation rules. A missing output, digest mismatch, or total mismatch must produce a failing exit status and identify the affected candidate or total."
    },
    {
      "target": "Script provenance",
      "action": "Validate the historical metadata without consulting the working tree.",
      "details": "Keep the three recorded script identities and digests. Check that each required entry is present and its digest is valid for the recorded format. Treat a recorded path as a name from the run. Remove the lookup and hashing of current scripts. Preserve the receipt byte for byte across refactors."
    },
    {
      "target": "Verifier owner tests",
      "action": "Exercise the existing verifier entry point with one small archive fixture.",
      "details": "Use fixed candidate bytes, independently calculated digests, and hand-counted totals. Start from a passing receipt. In separate cases, edit only a comment in a current script and rename a current script so its old path is absent. Both must still pass with the same receipt. For rejection cases, change one input at a time and assert the failing status and diagnostic."
    }
  ],
  "retained_contracts": [
    "Every listed output exists and its exact bytes match the digest attributed to that candidate.",
    "Reported totals agree with the archived evidence.",
    "The receipt preserves the script identities and hashes recorded at evaluation time. Independently confirming those hashes would require the historical script bytes."
  ],
  "validation": [
    "On the pre-fix verifier, reproduce the comment case at the script hash comparison and the rename case at the script lookup. On the revised verifier, expect exit zero for both.",
    "Make a parseable one-byte edit to a candidate that preserves its score and totals. Expect a digest error naming that candidate. Remove an output in a fresh fixture and expect a missing-output error.",
    "Change only a recorded total and expect a total mismatch. Separately omit a required script entry and supply a malformed script digest, checking for the corresponding provenance error in each case.",
    "Run the verifier owner test file with `pnpm test <verifier-test-file> --maxWorkers=1`, run the existing verifier on the unchanged historical receipt, and run `git diff --check`."
  ],
  "cost_and_stop": "Reuse one temporary fixture and table-driven mutations. Record single-worker wall time and CI seconds when available. Stop when the focused cases and the original receipt verify as expected.",
  "rationale": "Refreshing hashes after a refactor rewrites the record of which tools produced the outputs and can bless altered evidence. Deleting the verifier loses detection of damaged archives and incorrect totals. Current script contents cannot establish what ran in the past."
}
