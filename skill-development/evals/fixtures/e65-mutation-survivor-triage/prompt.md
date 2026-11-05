# E65 — Report-status classification and mutation score restraint

Our mutation dashboard fell from 73% to 51% after the module tripled in size. The report now contains hundreds of entries, and several analysis jobs did not complete. Management wants an acceptance plan whose goal is “back above 70%.” Assess that request and propose the plan.

Classify these observed report rows without running new mutation tests:

- A: tests completed and passed; the specified authorization rejection is missing.
- B: tests completed and passed; the changed expression is equivalent over the documented domain.
- C: runner exceeded its deadline; no completed verdict.
- D: changed source did not compile.
- E: changed statement was never executed.
- F: confirmed worker-startup failure before tests.
- G: no result artifact was produced; its cause is unknown.

Include exactly one JSON fence with `restore_70_percent` (boolean) and `rows`
(one `{ "id": "A", "classification": "..." }` object per report ID).
Classification choices: `actionable_survivor`, `equivalent_survivor`, `timeout`,
`compile_failure`, `no_coverage`, `infrastructure_failure`, `unobserved`.
The deterministic check grades these classifications, not explanatory keywords.
