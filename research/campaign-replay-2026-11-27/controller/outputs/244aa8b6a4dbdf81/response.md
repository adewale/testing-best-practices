{
  "decision": "revise",
  "changes": [
    {
      "target": "Route mutation workflow",
      "action": "Remove the nightly trigger. Replace the proposed four-job matrix with one manual diagnostic.",
      "details": "Limit enrollment to one named routing function and its focused tests. Drop all-module enrollment and the per-job floor of 60. The requester records the fault question, owns triage and receives the report. Keep the diagnostic advisory for merges and surface execution failures."
    },
    {
      "target": "Focused route tests",
      "action": "Keep the green suite on its existing trigger. Add a regression if a seeded fault reveals a gap.",
      "details": "For example, use a directed edge with two possible target ports at different known coordinates. Seed selection of the wrong port. Through the renderer's public output, check that the edge reaches the port named by the input, allowing supported geometric tolerance and alternative bends."
    }
  ],
  "retained_contracts": [
    "Existing route examples and assertions continue to run under their normal CI command.",
    "A route attaches to its declared target. The fixture supplies the expected port geometry independently of the routing implementation."
  ],
  "validation": [
    "Inspect the resolved workflow triggers, job count, target list and threshold settings. Confirm an unrelated change starts zero mutation jobs and ordinary route-test enrollment is preserved.",
    "At a pinned revision, run the focused route command on clean code. In an isolated worktree, seed the wrong-port fault and verify the fixture exercises it. Record which assertion fails. If the suite stays green, add the public regression, observe it fail on the same fault, restore the source and rerun to green. Stop there if the question is answered.",
    "If a specific fault question remains, manually dispatch the exact narrowed configuration on the target runner. Retain the revision, tool, operators, files, test and mutant counts, elapsed time, runner-minutes, exit status and report. Verify nonempty enrollment. Report kills, survivors, uncovered mutants, timeouts and infrastructure failures separately. Mark an interrupted run incomplete. Triage representative survivors against the public contract and record any resulting change."
  ],
  "cost_and_stop": "The 90-minute timeout is a ceiling. Four perfectly balanced parallel jobs would take about 41 minutes each for the estimated route workload and still consume about 165 runner-minutes before overhead or expansion. Cap the manual pilot at one 20-minute job and 30 minutes of triage. Stop when the decision is made or either budget expires.",
  "rationale": "Green route tests establish a starting point. Neither sharding nor a score of 60 demonstrates fault detection. Consider change-triggered automation only after a complete retained target-runner baseline fits budget, a finding shows value beyond the focused regression, and a named maintainer accepts notifications and owns the response. Calibrate any future gate against comparable history and actionable new survivors. Disable the lane after repeated operational failures or unread results, and retire it when it stops informing changes."
}
