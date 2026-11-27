{
  "decision": "reject",
  "changes": [
    {
      "target": "The 3.0 assertion-density target and its draft additions",
      "action": "Drop the target and remove the padding from the draft.",
      "details": "Review each added isinstance, non-null, or source-substring check against the public contract and existing proof. Remove checks introduced solely to raise the count. A promised return type or published literal can justify its own check at the boundary where callers observe it."
    },
    {
      "target": "One-assertion exception and property tests",
      "action": "Keep the existing tests intact.",
      "details": "Confirm the exception fixture reaches the intended guard and checks the promised exception. Keep the complete property assertion as a single assertion. Splitting it would add no detectable failure."
    },
    {
      "target": "Sanitizer tests that assert only nonempty output",
      "action": "Replace the nonempty check in the owning suite with a mixed-input case.",
      "details": "Extend the existing public sanitizer fixture with two distinct allowed values, keep-A and keep-B, surrounding one construct the documented policy removes. Check the returned output for both allowed values and the absence of the forbidden construct. Use a hand-written expected result when the format is specified, or inspect those properties in the public output format when serialization can vary. Reuse any sibling case that already exercises this rule."
    }
  ],
  "retained_contracts": [
    "The documented invalid input raises the promised exception at the intended guard.",
    "The existing property holds across the inputs covered by its test.",
    "Sanitization removes the forbidden construct and preserves the allowed content in the same input."
  ],
  "validation": [
    "Run the focused sanitizer file with its repository runner on the baseline and the candidate. Record the case names, results, and wall time.",
    "Temporarily bypass removal for the fixture's forbidden construct. Confirm the old nonempty check passes and the revised case fails because that construct survives. Restore the owner.",
    "Independently drop keep-B while preserving keep-A and removing the forbidden construct. Confirm the old check still passes and the revised case reports the missing allowed content. Restore the owner byte for byte.",
    "Rerun the clean sanitizer suite and relevant caller tests, run targeted formatting and git diff --check, and inspect the final diff for leftover control edits."
  ],
  "cost_and_stop": "Use one table row or revise one existing case at the sanitizer boundary. Stop when both controlled regressions are detected and focused proof passes. Record any genuine sanitizer defect separately with failing pre-fix and passing post-fix proof.",
  "rationale": "A single exception or property assertion can fully distinguish the promised behavior. The nonempty check accepts both unchanged unsafe input and a nonempty replacement that loses safe content. The mixed case distinguishes those failures directly."
}
