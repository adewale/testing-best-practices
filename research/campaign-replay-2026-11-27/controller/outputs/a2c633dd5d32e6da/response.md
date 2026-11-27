{
  "decision": "reject",
  "changes": [
    {
      "target": "Historical receipt verifier",
      "action": "Keep the public verification command and remove its dependency on the working tree.",
      "details": "Read the original receipt without writing it. Require one well-formed digest for each of the three historical script identities. When original bytes are available from the recorded revision or archive, hash them with the declared algorithm and fail on mismatch. When only a fingerprint was retained, report that script's historical bytes as unavailable. A missing artifact explicitly promised by the archive is an error."
    },
    {
      "target": "Candidate outputs and totals",
      "action": "Verify the archived evidence against the original run declaration.",
      "details": "Match each declared case, arm and repeat to its output, then hash the exact archived bytes. Fail on missing, duplicate or misassigned records. Reconcile enrollment, denominators, score bounds and per-arm totals against retained historical result rows under the recorded scoring rules. If only aggregates survive, identify which arithmetic can be checked and which totals lack row-level evidence."
    }
  ],
  "retained_contracts": [
    "The original output digests, script fingerprints, labels and totals remain the record of that run.",
    "The verdict identifies which evidence was verified. Any assessment using today's scorer receives its own labelled result."
  ],
  "validation": [
    "Use the public command on a temporary copy of a known-good receipt with distinct candidate bytes and independently tallied results. Expect exit zero. Separately add a comment to a current script and rename another current script away from its recorded path. The old check should fail each variant and the revised check should pass both with the receipt byte-for-byte intact.",
    "From the good fixture, change one archived output byte, then separately remove a required output. Each invocation must exit nonzero and identify the affected output and cause.",
    "Swap unequal per-arm totals while preserving the grand total. Separately substitute a duplicate case/repeat for a required one while preserving row count. Require failures identifying the incorrect arm total and enrollment respectively.",
    "Exercise the three script records with matching archived bytes. Corrupt one archived script and require a digest failure. For a fingerprint-only record, require explicit unavailable status alongside successful output checks. Remove or malform a required fingerprint and require a provenance-record failure."
  ],
  "cost_and_stop": "Reuse one small offline fixture with isolated variants. Stop after the focused public-command tests and one read-only check of the existing receipt. No evaluation rerun is needed.",
  "rationale": "Refreshing hashes would assign later code to an earlier run and could bless damaged outputs. Deleting verification would hide archive corruption and inconsistent totals. Historical fingerprints identify the code originally recorded. They provide no evidence about the behavior of a later revision."
}
