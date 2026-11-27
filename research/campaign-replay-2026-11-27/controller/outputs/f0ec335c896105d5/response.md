{
  "decision": "approve",
  "changes": [
    {
      "target": "Changed parser function",
      "action": "Seed one off-by-one fault by hand in a scratch copy.",
      "details": "Use the escaped boundary condition if known. For example, if the grammar accepts an item ending exactly at the limit, change the inclusive comparison from <= to <. Write down the expected public result at that endpoint from the grammar or a reviewed bug example."
    },
    {
      "target": "Parser boundary tests",
      "action": "Ship one regression if the four existing tests miss a demonstrated error.",
      "details": "Use the smallest input that distinguishes the two versions and assert the specified parsed value or error through the public parser. If an existing assertion already catches the fault, record that test as the witness."
    }
  ],
  "retained_contracts": [
    "Inputs at the endpoint and on either side receive the result specified by the parser grammar.",
    "All four existing tests participate with their original fixtures and assertions when measuring detection."
  ],
  "validation": [
    "Record the starting revision and focused runner invocation. Run the four tests on the original parser and confirm all four execute and pass.",
    "Apply only the boundary edit and rerun the identical invocation before adding a test. Record which assertion fails and its expected and actual results. An unrelated failure or timeout leaves boundary detection unresolved.",
    "If all four pass, check whether their inputs reach the edited comparison at equality and whether its changed result reaches the public output. Compare both versions on the endpoint input. Distinguish a missing input or assertion from a change the grammar makes unobservable.",
    "For a confirmed gap, run the new regression against the mutant and verify it fails on the predicted result. Restore the parser byte-for-byte, check it against the starting copy, and rerun the four tests plus any new regression on the restored version."
  ],
  "cost_and_stop": "Baseline, mutant and restoration runs take about six seconds of test time at two seconds per four-test run. Allow one additional focused run if a regression is needed. Stop once this fault is classified and the source restored, or at ten minutes total including setup and triage. Record any unresolved outcome at the cap.",
  "rationale": "A single comparison edit directly tests whether the current assertions detect the suspected error. Line coverage shows that code ran. The failing assertion identifies which observable boundary behavior the tests protect."
}
