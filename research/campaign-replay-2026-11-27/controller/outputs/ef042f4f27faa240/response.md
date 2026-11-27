{
  "decision": "revise",
  "changes": [
    {
      "target": "Mutation workflow",
      "action": "Remove the nightly trigger and keep a manual diagnostic.",
      "details": "Use one job restricted to a selected route function and its focused tests. Drop the four-job matrix, all-module enrollment and score floor of 60. Keep reports advisory and surface incomplete runs as failures of the diagnostic."
    },
    {
      "target": "Focused route tests",
      "action": "Keep the existing suite in normal CI and check its sensitivity to a lost destination.",
      "details": "Use a diagram with distinct endpoints. Temporarily omit the final segment in the production router. If an existing assertion catches the missing attachment, retain it. If the visible defect survives, extend the focused renderer test with the expected destination derived from the fixture geometry and documented attachment rules. Allow any valid intermediate path."
    },
    {
      "target": "Result ownership",
      "action": "Assign each manual run to the maintainer requesting it.",
      "details": "Record their name and the unresolved routing question at dispatch. Deliver the report to them for a test or code decision. Consider recurring execution only after a complete target-runner baseline, demonstrated detection of an actionable fault beyond the retained regression, measured capacity and a named ongoing owner. Use relevant code, test or configuration changes as the trigger. Any future score policy needs comparable history under the same scope and operators."
    }
  ],
  "retained_contracts": [
    "Preserve every existing focused route assertion and its CI coverage.",
    "Check the rendered edge reaches its specified destination through the public renderer. Equivalent waypoint choices remain acceptable."
  ],
  "validation": [
    "Inspect default-branch job logs for the pinned SHA, selected route tests, skip count, exit status and where the mutation run stopped. Check the revised workflow selects zero mutation jobs on a timer and one scoped job on manual dispatch.",
    "Run the focused CI command on clean source, on the seeded fault in an isolated checkout, and after restoring the source byte-for-byte. Capture the failing endpoint assertion and restored green result. If the original suite misses the defect, repeat the same fault with the strengthened test.",
    "If a distinct question remains, dispatch the exact restricted configuration on the target runner. Verify nonempty route mutant and test selection. Retain the SHA, tool version, command, operators, elapsed time, runner-minutes and full report.",
    "Report assertion kills, completed survivors, uncovered mutants, timeouts and infrastructure errors separately. Inspect representative survivors for observable defects, equivalent behavior or documented fallback. Record the reviewer's decision."
  ],
  "cost_and_stop": "Four perfectly balanced jobs would each take about 41.25 minutes for routes alone. Total estimated compute stays around 165 runner-minutes per night, or 1,155 per week, before extra shard setup or expansion. Budget one 30-minute runner and 30 minutes of review for a scoped pilot. Stop when the focused probe answers the question or the budget expires. Narrow a timed-out pilot before retrying. Disable any future lane after three consecutive operational failures or untriaged reports, and retire it when it stops informing decisions.",
  "rationale": "Green focused tests establish the current examples pass. The unfinished 90-minute job supplies no comparable score or evidence that mutation finds additional routing defects. Sharding addresses elapsed time alone."
}
