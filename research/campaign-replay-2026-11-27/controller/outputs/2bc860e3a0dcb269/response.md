{
  "decision": "revise",
  "changes": [
    {
      "target": "Audit acceptance criteria and draft additions",
      "action": "Drop the per-file 3.0 threshold and discard the checks added solely to reach it.",
      "details": "Remove redundant isinstance and non-null assertions and searches for substrings in implementation source. For each proposed test edit, identify a contract violation that the existing test would accept and the edit would catch."
    },
    {
      "target": "Sanitizer tests that check only for nonempty output",
      "action": "Replace the nonempty checks with comparisons against the promised public output.",
      "details": "For each distinct removal rule already exercised, include a recognizable allowed fragment alongside the prohibited construct. Derive the expected result from the policy. For example, if paragraphs are allowed and event attributes must be stripped, sanitizing <p onclick=\"\">keep-42</p> should yield a paragraph containing keep-42 with the onclick attribute absent. Compare the parsed structure if serialization can vary. One comparison can cover both removal and preservation."
    }
  ],
  "retained_contracts": [
    "Keep the one-assertion exception test that exercises the triggering input and checks the promised exception.",
    "Keep the complete property assertion and its existing input coverage."
  ],
  "validation": [
    "Run the edited sanitizer cases against the current implementation using the project's test runner. Check any mismatch against the documented rule.",
    "In a temporary working copy, bypass the removal rule so the mixed input passes through. Verify that the old nonempty check passes and the revised test fails on the retained prohibited construct.",
    "Restore the rule, then temporarily replace the allowed fragment with a different nonempty marker while still removing the prohibited construct. Verify that the old check passes and the revised test fails on the lost allowed content.",
    "Restore the implementation, inspect the diff for temporary edits, and run the normal test suite, including the exception and property tests."
  ],
  "cost_and_stop": "Limit edits to the audit proposal and sanitizer cases with an identified gap. Use the two targeted fault checks on a representative mixed case. Stop when the distinct removal rules under review have behavioral coverage, both faults are detected, and the restored suite passes.",
  "rationale": "A single assertion can establish an entire contract. Several assertions can all pass while a sanitizer returns its input untouched or discards allowed content. Checking the promised output distinguishes those failures and permits internal refactoring."
}
