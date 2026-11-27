{
  "decision": "approve",
  "changes": [
    {
      "target": "Changed parser function",
      "action": "Hand-seed one temporary off-by-one fault.",
      "details": "Use a disposable copy of the revision under review. Recreate the escaped fault if its diff is known. Otherwise, change the relevant comparison by one boundary value, for example from < to <=. Identify an input for which the public result should differ. Leave all four tests untouched for the experiment."
    },
    {
      "target": "Existing parser boundary tests",
      "action": "Add one regression case only if the four tests miss a real behavior change.",
      "details": "If the mutant survives, pass the distinguishing input through the public parser. If it produces the wrong result, extend the existing test table or assertion with that input and the expected value or error from the parser contract. If an existing boundary assertion already catches the mutant, report which one and ship no test change."
    }
  ],
  "retained_contracts": [
    "The public parser produces the specified value or error at the changed boundary. Existing assertions for neighboring inputs and other parser behavior remain in place."
  ],
  "validation": [
    "Run the four focused tests against the unmodified revision using the repository test wrapper with --maxWorkers=1. Verify all four execute and pass.",
    "Run the identical selection against the mutant. Count it as caught only if a boundary assertion fails because the public result differs as predicted. Record the test, input, expected result and observed result.",
    "If a regression case is added, verify it fails on the mutant for that reason. Remove the mutation and rerun the focused tests to confirm they pass. Check the final diff for the intended test change only."
  ],
  "cost_and_stop": "Budget two seconds per four-test run and ten minutes total, including setup. Stop at the first conclusive result. A failed baseline, setup error, indistinguishable mutation or expired budget leaves the question unresolved. Discard the temporary mutation on every exit.",
  "rationale": "One targeted mutation answers whether the current assertions detect this particular fault. High line coverage establishes that code ran. The observed assertion failure establishes whether the suite notices the changed result."
}
