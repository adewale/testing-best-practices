{
  "decision": "reject",
  "changes": [
    {
      "target": "Per-file assertion-density proposal",
      "action": "Remove the 3.0 acceptance criterion and discard its padding.",
      "details": "Drop the draft's isinstance, non-null and source-substring assertions added solely to raise the count. Keep checks of types or published text when an independent contract promises them."
    },
    {
      "target": "Existing exception and property tests",
      "action": "Retain the single assertions.",
      "details": "Confirm the invalid call reaches the intended guard and the property exercises its intended inputs. Each assertion already identifies a specific broken promise."
    },
    {
      "target": "Sanitizer tests whose only assertion is nonempty",
      "action": "Replace the weak assertions with checks on the public sanitizer's output.",
      "details": "Choose a forbidden construct from the sanitizer's documented examples. Place it between two distinct allowed fragments such as 'cedar' and 'birch'. Check that the forbidden construct is gone and both fragments survive. Include a safe-only row with an independently specified expected result. Compare content or parsed structure at the level the contract promises."
    }
  ],
  "retained_contracts": [
    "The specified invalid operation raises the promised exception.",
    "The complete existing property holds over its intended input domain.",
    "The sanitizer removes specified unsafe content and preserves specified safe content."
  ],
  "validation": [
    "Record the baseline with the project's runner selecting the affected tests and confirm each selected case executes.",
    "On an isolated copy, bypass removal. On the same mixed input, the old nonempty assertion should pass and the revised check should identify the surviving forbidden construct.",
    "On a separate copy, drop 'birch' while preserving 'cedar' and removing the forbidden construct. The old nonempty assertion should pass and the revised check should identify the missing safe fragment.",
    "Record observed outcomes and failure reasons. Run the repaired tests and their owning suite against the original sanitizer. A behavior-preserving helper rename should also leave the assertions green."
  ],
  "cost_and_stop": "Limit the change to the draft and affected tests. Stop once the two controls demonstrate detection for the intended reasons and the owning suite passes against the original implementation.",
  "rationale": "Assertion density can flag a file for inspection. It cannot distinguish an exact exception or property check from several assertions that all accept the same wrong output."
}
