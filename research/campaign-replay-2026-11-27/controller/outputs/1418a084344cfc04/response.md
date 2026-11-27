{
  "decision": "reject",
  "changes": [
    {
      "target": "Release fixture and published manifest",
      "action": "Retain",
      "details": "Keep the original archive bytes and the published digest for this release. Verify the raw archive using the manifest’s algorithm. Verification must read the expected digest from the published manifest and must never regenerate it from the test input."
    },
    {
      "target": "Public importer tests",
      "action": "Retain and strengthen",
      "details": "Pair the existing corruption test with a successful import of the original. Corrupt a temporary copy and submit it with the original manifest. Include a parseable change, such as repacking identical entries with different supported compression settings. Reuse the corruption case if it already preserves the parsed contents."
    },
    {
      "target": "Implementation and content assertions",
      "action": "Allow refactoring",
      "details": "Allow changes to source formatting, helper structure and buffering. Remove any assertion that pins the live importer’s source hash. A historical source hash can identify the revision previously tested. Use parsed equality to check content returned by a successful import."
    }
  ],
  "retained_contracts": [
    "The importer accepts the genuine archive with its published manifest.",
    "The importer rejects an archive whose bytes fail the published digest check, even when every logical entry is preserved."
  ],
  "validation": [
    "Independently hash the original file and compare it with the manifest. For the format-valid altered copy, confirm the digest differs and an archive reader produces the same logical entries.",
    "Exercise the public import entry point before and after the refactor with the same manifest. Assert acceptance of the original and integrity rejection of the altered copy. Pass the altered copy through to the importer so a fixture check cannot supply the rejection.",
    "In a scratch copy, disable the digest comparison. Verify the format-valid altered archive is accepted and the rejection test fails on that acceptance."
  ],
  "cost_and_stop": "Use one release fixture and the focused importer tests. Stop when the refactor preserves both outcomes and the rejection test catches the disabled check. These checks are proposed.",
  "rationale": "A formatting change can preserve every parsed value while changing the bytes the publisher committed to. Parsed equality alone would accept that substitution."
}
