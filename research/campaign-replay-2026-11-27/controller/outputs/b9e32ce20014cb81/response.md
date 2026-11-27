{
  "decision": "reject",
  "changes": [
    {
      "target": "Historical receipt verifier",
      "action": "Remove the comparison against checkout scripts.",
      "details": "Read the three script identities and digests from the receipt and validate their required fields and digest format. Treat the recorded paths as historical names. Verification must work with the archive and receipt alone."
    },
    {
      "target": "Archive integrity checks",
      "action": "Keep candidate hashes and totals as pass/fail checks.",
      "details": "Hash the bytes of every listed candidate output using the receipt’s algorithm. Fail if a file is missing or its digest differs. Compute totals from the archived data using the receipt’s counting rules and compare them with the recorded totals. Identify the affected file or total on failure."
    }
  ],
  "retained_contracts": [
    "The existing receipt stays read-only and preserves the identities and hashes of the scripts used for that run.",
    "An intact archive with matching totals yields a successful exit. Missing or corrupt evidence and inconsistent totals yield a nonzero exit."
  ],
  "validation": [
    "Verify a known-good receipt and archive. From fresh copies, edit only a comment in a checkout script, then separately rename a checkout script so its historical path is absent. Expect success in all three cases and byte-identical receipt contents after each run.",
    "With the checkout script still renamed, change one archived output in a way that preserves its contribution to the totals. Expect a digest failure naming that output. In a fresh copy, remove a listed output and expect a missing-file failure.",
    "Alter only one recorded total while preserving every archived byte and digest. Expect failure naming the total and reporting the recorded and computed values.",
    "Independently omit a required script digest and supply a malformed digest in a copied receipt. Expect receipt-format errors in both cases."
  ],
  "cost_and_stop": "Limit the patch to the verifier and focused fixture tests. Run those tests and the verifier on the existing receipt. Stop when both pass and the receipt diff is empty.",
  "rationale": "Refreshing hashes after a refactor would attribute later script bytes to the historical run and could bless an altered output. Deleting the verifier would remove the archive integrity check. The stored script hashes retain their value as provenance. Confirming them byte for byte requires the original script snapshots."
}
