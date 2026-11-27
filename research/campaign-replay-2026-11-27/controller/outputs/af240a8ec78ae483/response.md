{
  "decision": "reject",
  "changes": [
    {
      "target": "Proposed 3.0 assertion-density target",
      "action": "Drop the target and its padding.",
      "details": "Remove the draft's redundant isinstance and not-null checks and its searches for substrings in implementation source. Use counts only to locate tests for review. Keep a type or presence check when callers independently rely on that guarantee."
    },
    {
      "target": "Existing exception and property tests",
      "action": "Retain both as written.",
      "details": "The exception assertion exercises the triggering input and identifies the promised exception. The property assertion expresses the complete invariant over its input domain. Splitting either assertion adds no coverage of a distinct failure."
    },
    {
      "target": "Sanitizer tests whose sole assertion is nonempty output",
      "action": "Replace the assertion with checks on the public sanitizer's returned content.",
      "details": "Choose expected results from the documented policy. For example, if it allows em and strips event attributes, sanitize <em onclick=''>Receipt-17</em>. Parse the returned fragment, require an em containing Receipt-17, and check that it has no onclick attribute. A safe-only row such as <em>Invoice-28</em> must retain its allowed element and text. Use the corresponding documented constructs for the actual sanitizer."
    }
  ],
  "retained_contracts": [
    "The specified invalid input raises the promised exception.",
    "The existing property holds over its stated domain.",
    "Sanitization removes prohibited content and preserves the allowed content alongside it."
  ],
  "validation": [
    "Using the project's focused runner, establish the baseline and confirm the named sanitizer cases, exception test and property test actually execute.",
    "In isolated copies, run the old and revised sanitizer cases against the same two temporary faults. First return the mixed input untouched. Then strip the forbidden attribute correctly but replace the allowed text with a fixed nonempty placeholder. Expect the old nonempty assertion to pass both. Expect the revised cases to fail specifically on the surviving attribute and the lost text, respectively.",
    "Rename a private sanitizer helper without changing its behavior. The revised tests should pass. Restore the original code, rerun the focused cases and required CI checks, and record exit statuses and any skipped cases."
  ],
  "cost_and_stop": "Limit edits to the proposed padding and the identified weak sanitizer cases. Stop once both faults are detected for the intended reasons, the allowed refactor passes, and the restored suite passes its required checks. Report any baseline policy violation separately.",
  "rationale": "An unchanged input and a fixed placeholder can both satisfy several type, presence and source-text checks. The mixed fixture distinguishes unsafe pass-through from loss of legitimate content even when both outputs are nonempty."
}
