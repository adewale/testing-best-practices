{
  "decision": "reject",
  "changes": [
    {
      "target": "Published archive and manifest fixture",
      "action": "Retain the exact release bytes and the independently published digest.",
      "details": "Use the manifest's algorithm over the complete archive as delivered. Keep the original manifest as the expected value for both test cases. A separately published release can supply a new archive and manifest pair."
    },
    {
      "target": "Existing importer integrity test",
      "action": "Exercise the public import entry point with a matching archive and an altered copy.",
      "details": "First import the untouched archive successfully. For the rejection case, change a format-permitted byte in a copy, such as a comment character if supported, so it remains readable and decodes to the same content. Import that copy with the original manifest and assert rejection. Check the public integrity-error category if the importer exposes one."
    },
    {
      "target": "Implementation-specific assertions",
      "action": "Remove any hash assertions whose only subject is a private representation.",
      "details": "The hashing library, buffering strategy and helper structure may change. The altered copy's precise digest can vary. Parsed-content equality can establish that the two fixtures decode alike or check an existing successful-import content contract."
    }
  ],
  "retained_contracts": [
    "The published manifest commits to the exact byte sequence of its release archive.",
    "The importer accepts that archive and rejects a byte-different archive under the same manifest, even when both yield identical parsed content."
  ],
  "validation": [
    "Use an independent digest utility with the manifest's algorithm on both raw archives. The original must match the published value and the altered copy must differ from it.",
    "Use an independent archive reader to validate the altered copy and compare its decoded content with the original. This rules out malformed input as the reason for rejection.",
    "Run the focused importer test on the original and refactored implementations with one worker. On each, verify success for the original and rejection for the altered copy. A verifier using parsed equality alone would fail the rejection case."
  ],
  "cost_and_stop": "Reuse the existing release fixture and importer test, create one disposable copy and record focused test wall time. Stop once the fixture check and both importer outcomes hold across the refactor.",
  "rationale": "Formatting and repacking can preserve parsed values while changing the bytes the publisher committed to. Replacing the digest check with parsed equality would let a different archive satisfy the test."
}
