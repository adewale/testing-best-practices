{
  "decision": "approve",
  "changes": [
    {
      "target": "Changed parser function",
      "action": "Seed one off-by-one fault by hand in a scratch copy.",
      "details": "Use the escaped edit if it isolates this fault. Otherwise choose a comparison whose equality case matters to the grammar. For example, at a documented inclusive limit N, change <= N to < N."
    },
    {
      "target": "Existing boundary test",
      "action": "Extend it only if the four tests miss a demonstrated parsing error.",
      "details": "Add the distinguishing input to the nearest test table and assert the public parse result or rejection specified by the grammar. Keep the rest of the input valid so an earlier error cannot satisfy the assertion."
    }
  ],
  "retained_contracts": [
    "The public parser handles the exact boundary and its adjacent values according to the grammar. Derive the expected outcome from the rule or a reviewed example."
  ],
  "validation": [
    "Record the revision and focused test selector. Run it on the original parser and verify all four tests execute and pass.",
    "Apply the single edit and rerun the same four tests before changing any assertions. Record the diff and failing assertion. A failure showing the predicted wrong parse answers the question.",
    "If all four pass, compare the original and edited public parser on the distinguishing input. A contract violation on the edited copy establishes a miss. If the edit has no observable effect, record why or mark the result inconclusive. Treat setup, compilation, and timeout failures as inconclusive.",
    "For a confirmed miss, verify the added row fails on that same edit and passes on the original. Restore the parser byte-for-byte, rerun the focused tests, and retain the test change and observed results."
  ],
  "cost_and_stop": "The baseline and seeded runs cost about four seconds of test time together. Stop once the existing assertion detects the fault or a confirmed miss has a verified regression test. Cap setup, runs, and triage at ten minutes and report any unresolved question at the cap.",
  "rationale": "High coverage can coexist with an assertion that accepts the wrong boundary result. One targeted edit measures the existing suite's sensitivity to the specific fault directly."
}
