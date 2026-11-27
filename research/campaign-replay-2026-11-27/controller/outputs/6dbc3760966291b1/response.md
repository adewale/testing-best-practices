{
  "decision": "reject",
  "changes": [
    {
      "target": "Importer integrity check",
      "action": "Keep the digest comparison at the public import boundary.",
      "details": "Hash the raw archive bytes using the algorithm specified by the published manifest. Accept the archive only if the digest matches the manifest entry and the import otherwise succeeds. The refactor may change how the importer reads, buffers, hashes, and parses the archive."
    },
    {
      "target": "Release fixture and test expectations",
      "action": "Keep the original archive and its published manifest unchanged.",
      "details": "Use the manifest as the source of the expected digest. Make corruptions on temporary copies and pass the original manifest to every import. Remove duplicate digest literals if the tests can use the published entry directly."
    },
    {
      "target": "Parsed-content assertions",
      "action": "Use semantic equality to check the result of a successful import.",
      "details": "Assert the public output that callers rely on. Implementation details such as helper calls and buffer sizes may change freely."
    }
  ],
  "retained_contracts": [
    "The published digest commits to the complete distributed archive, including bytes that have no effect on parsed content.",
    "The original release imports successfully. An archive with a mismatched digest is rejected under the original manifest."
  ],
  "validation": [
    "Compute the original fixture's digest with an independent implementation of the manifest algorithm and compare it to the published entry.",
    "Import the untouched fixture with its manifest and check the expected public result.",
    "Run the existing intentional-corruption test through the importer on a temporary copy and assert the documented rejection behavior.",
    "Exercise a well-formed alternate encoding with the same parsed content, for example by changing an ignored archive metadata field. Confirm the byte strings differ and the parsed values agree. Import the alternate with the original manifest and require rejection. Reuse the existing corruption case if it already meets these conditions."
  ],
  "cost_and_stop": "Digest verification takes one linear pass over the archive and can share the importer's input read. Stop once the focused import tests pass for the original and altered inputs with the released files unchanged.",
  "rationale": "A formatting-only change is enough to break this release's byte commitment. The well-formed negative case catches a semantic-only verifier even when the existing corruption would also cause a parser error."
}
