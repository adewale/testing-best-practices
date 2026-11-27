{
  "decision": "revise",
  "changes": [
    {
      "target": "Tamper fixture",
      "action": "Prepare the known-good input once for the focused cases.",
      "details": "Use the real preparation code and keep its output read-only. Give each case a fresh copy to edit. Share only work upstream of the edit. If a variant changes an input to a preparation stage, rerun that stage and its dependents for that case."
    },
    {
      "target": "Checker tests",
      "action": "Turn every existing variant into a named test row.",
      "details": "Each row specifies one edit and the rejection expected from the verifier's contract. Apply the edit, pass the changed artifact to the production checker, and assert its fresh verdict. Check the rejection reason when exposed. An untouched copy must be accepted. Setup failures and unrelated exceptions must fail the test."
    },
    {
      "target": "Full verifier test and timeout",
      "action": "Keep one end-to-end case in required CI and drop the global timeout increase.",
      "details": "Retain an existing case that prepares raw input, introduces one representative tamper, and runs the complete oracle pipeline. Assert rejection at the public entry point so the test catches a caller that discards the checker's verdict."
    }
  ],
  "retained_contracts": [
    "The checker accepts the independently known-good artifact.",
    "Each named tamper reaches its intended check and produces a rejection.",
    "A rejection reaches the caller through the complete preparation-to-verdict path."
  ],
  "validation": [
    "Compare the old and proposed case lists by edit and expected outcome. Run the normal CI selector and confirm it executes every named row, the valid control, and the full-path case.",
    "In a scratch copy, make one targeted rule accept its bad input. Run the old case and its replacement against that same change. Both must fail on unexpected acceptance and pass again after restoration.",
    "Time the old and revised tests on the same CI runner configuration with the same variants. Record preparation counts, complete pipeline runs, verifier seconds, and total unit-suite seconds alongside the reported 32% baseline."
  ],
  "cost_and_stop": "Each additional downstream variant should cost one isolated edit and one checker invocation. The number of full pipeline runs stays at one. Ship once every required outcome is preserved and comparable timings show lower verifier cost within the existing timeout. Add a proposed row only if it exposes a distinct verification gap.",
  "rationale": "Repeated preparation spends unit-suite time recreating identical inputs. Sharing those inputs saves that work while each changed artifact still has to earn its own verdict."
}
