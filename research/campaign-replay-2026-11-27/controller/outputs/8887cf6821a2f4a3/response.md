{
  "decision": "approve",
  "changes": [
    {
      "target": "Boundary check in the changed parser function",
      "action": "Hand-seed one temporary off-by-one fault.",
      "details": "Use the escaped fault if known. Otherwise change one inclusive comparison to exclusive, or vice versa. Identify the exact boundary input where the two versions should produce different parser behavior."
    },
    {
      "target": "Focused parser tests",
      "action": "Fill a demonstrated assertion gap.",
      "details": "If the mutant survives and changes behavior for a supported input, extend the nearest existing test or add one case through the current parser interface. Assert the specified outcome for that input. If an existing boundary assertion catches the fault, close the review with its test name and failure."
    }
  ],
  "retained_contracts": [
    "The parser's existing interface and specified boundary behavior.",
    "A one-time manual check of the changed function using the four focused tests."
  ],
  "validation": [
    "Run the four existing tests on the original code. Stop if the baseline fails.",
    "Apply the single mutation and rerun the same four tests with their original assertions. Record which assertion fails and its expected and actual values. A boundary assertion failing on the predicted difference answers yes. A build error or unrelated failure is inconclusive.",
    "If all four pass, record that the mutant survived. Check that the boundary input reaches the changed predicate and the difference is observable before adding a regression assertion.",
    "For a new or strengthened assertion, verify that it fails on the mutant. Restore the original predicate, rerun the four tests plus any added case, and check that the final diff contains only the intended test edit, if any."
  ],
  "cost_and_stop": "The baseline and mutant runs take about four seconds of test time combined. Stop sampling after this one fault. Cap the entire exercise at ten minutes, restore the original predicate, and report an inconclusive result if the comparison could not be completed.",
  "rationale": "High coverage can show that the suite executes the boundary check. Changing its result at equality tests whether an existing assertion can detect the error."
}
