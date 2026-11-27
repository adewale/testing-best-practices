{
  "decision": "reject",
  "changes": [
    {
      "target": "Release archive and manifest fixtures",
      "action": "Retain the published digest as the expected value.",
      "details": "Pin the original archive and its published manifest. Verify the digest over the complete archive byte stream using the manifest's algorithm. Treat both fixtures as read-only during verification."
    },
    {
      "target": "Public importer integrity tests",
      "action": "Keep the acceptance and corruption checks.",
      "details": "Import the original archive with its manifest and expect success. Pass a corrupted copy to the same entry point with the original manifest and expect integrity rejection. Include a well-formed, byte-different copy with identical extracted contents so a decoding error cannot explain the rejection."
    },
    {
      "target": "Implementation-specific assertions",
      "action": "Remove any hashes that pin only importer source or private intermediates.",
      "details": "The importer may change its helpers, hash library or read chunk size. Keep parsed-content assertions where they verify a separately promised import result."
    }
  ],
  "retained_contracts": [
    "The published manifest identifies this exact release artifact, including byte-level formatting.",
    "The importer accepts the published artifact and rejects a digest mismatch even when both archives decode to the same contents."
  ],
  "validation": [
    "Independently compute the fixture digest and compare it with the published manifest entry.",
    "Confirm the well-formed alternative extracts to identical contents and has a different digest. Run the acceptance and rejection cases against both importer versions with the same manifest and inputs.",
    "In a scratch copy, bypass the digest comparison. The well-formed alternative should then import, making its rejection test fail for the intended reason."
  ],
  "cost_and_stop": "Limit the work to the release fixtures and focused importer tests. Stop when the refactor passes the same cases and the rejection test detects the bypass.",
  "rationale": "Repacking identical contents can change the bytes the publisher committed to. Parsed equality would accept that substitution. An internal refactor can preserve the published digest without any fixture update."
}
