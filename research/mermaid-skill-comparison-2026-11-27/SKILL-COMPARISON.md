# Skill comparison before the project audits

Our skill is version 0.3.3 at `7ea8838f`; OpenClaw guidance is pinned to `dff00f34`. All eight retrieved OpenClaw guidance/license files are byte-identical to the previous `9fd0b7de` snapshot. Agentic Mermaid main remains `f49196e7`.

| Dimension | Testing Best Practices | OpenClaw Test Audit |
|---|---|---|
| Primary scope | Cross-language Write, Assess, Upgrade and Detect; audit is a routed reference | Focused test authoring and pruning, composed with OpenClaw testing policy |
| Shared value bar | Observable contract, credible fault, missing proof, owner and callers, independent expectations | Substantially the same value bar, with explicit primary ownership and seam removal |
| Discovery | Search candidates, contextual review; risk-based and reproducible stratified samples with inventory/read/run accounting | Few high-confidence owner batches; read-only discovery before edits |
| Consolidation | Retain/repair/consolidate/delete ledger; old/keeper fault comparison and permitted-change controls | Same decisions; stronger emphasis on deleting obsolete test-only production seams and net-negative production LOC |
| Whole subsystem | Complete contract accounting and independent preservation review before retiring a layer | Explicit eight-stage campaign: file baselines, complete declaration/row ledgers by lane, second layer-plan pass, cutover, independent preservation, product-defect proof, upstream reconciliation |
| Oracle calibration | Dedicated guide; public accept/reject route, per-criterion controls, permitted forms, reachability and metric compatibility | Independent expected values, meaningful rejection guard and authentic owner receipts; fixture guide separates skill selection/compliance/workflow evals |
| Failure and evidence | Process failures/unavailability stay provisional; artifact delivery distinct from completion; historical hashes remain provenance | Exact-SHA/job diagnosis and failure classification; passing replay is not a proven repair; do not rerun for green |
| Costs and execution | Proportional proof, no assertion/deletion/mutation quotas; focused faults before tool campaigns | Strong native routing, broad proof deferred to PR CI, timing and line-budget policies tied to OpenClaw |
| Portability | Language/topical references and generic commands; development behavioral oracles cover specified fixtures | pnpm/Vitest/deadcode/live-provider policies require mapping to the target; native absolute budgets are not universal quality rules |
| Tooling claim | Development oracles execute specified reference/fault controls; not a general automatic bad-test detector | Skill composes repository tooling and human/agent review; not a universal detector either |

OpenClaw is more explicit about exhaustive pruning mechanics and support-seam cleanup. Ours is more explicit about measurement calibration, sampling disclosure and implementation alternatives. Both share significant source ideas and target-repository instructions; the downstream audits cannot cleanly attribute every behavior to a supplied skill. The fair comparison here is the ordinary bounded audit, not an exhaustive campaign with unequal staffing.

## Reading the tool comparison correctly

Testing Best Practices' new runtime oracles are **development evaluations of specified fixtures** (scheduler delivery, retry recovery, native SQLite search, release-verifier verdict propagation). They are evidence that those checkers discriminate declared faults and valid alternatives. They are not a drop-in scanner that automatically audits arbitrary Mermaid tests. Its reusable target-side audit is primarily instructions, candidate searches and native test execution.

OpenClaw likewise composes test-audit with its repository-native changed-check routing, dead-code checks, fixture helpers and CI workflow. Those tools are valuable in OpenClaw but cannot be claimed as operating on Agentic Mermaid merely by supplying their Markdown. Both auditors use Mermaid's actual commands and installed dependencies here.

The target's CLAUDE.md already supplies a strong shared contract-first test policy. This two-subject comparison evaluates useful findings under each supplied workflow, not whether either skill causally beats that common baseline. No no-guidance control or repeated trials are included in this request.

## Pinned reading links

- [Our entry point](https://github.com/adewale/testing-best-practices/blob/7ea8838f53590965926bc8a223b149aba2f822a9/testing-best-practices/SKILL.md), [audit workflow](https://github.com/adewale/testing-best-practices/blob/7ea8838f53590965926bc8a223b149aba2f822a9/testing-best-practices/references/test-audit.md), [larger-suite sampling](https://github.com/adewale/testing-best-practices/blob/7ea8838f53590965926bc8a223b149aba2f822a9/testing-best-practices/references/test-audit-patterns.md), [checker calibration](https://github.com/adewale/testing-best-practices/blob/7ea8838f53590965926bc8a223b149aba2f822a9/testing-best-practices/references/checker-calibration.md).
- [OpenClaw entry point](https://github.com/openclaw/openclaw/blob/dff00f34e82554ec5afb4422db2540e630a42b1b/.agents/skills/test-audit/SKILL.md), [audit workflow](https://github.com/openclaw/openclaw/blob/dff00f34e82554ec5afb4422db2540e630a42b1b/.agents/skills/test-audit/references/audit.md), [whole-subsystem campaign](https://github.com/openclaw/openclaw/blob/dff00f34e82554ec5afb4422db2540e630a42b1b/.agents/skills/test-audit/CAMPAIGN.md), [testing policy](https://github.com/openclaw/openclaw/blob/dff00f34e82554ec5afb4422db2540e630a42b1b/.agents/skills/openclaw-testing/SKILL.md), [boundary scenarios](https://github.com/openclaw/openclaw/blob/dff00f34e82554ec5afb4422db2540e630a42b1b/docs/help/testing/boundary-scenarios.md).

Both subjects also received the same evidence-reporting task brief, including encouragement to try a credible fault and a permitted change. That shared scaffold is recorded in task-packets.json; the presence of those controls in a report cannot be attributed solely to its assigned skill. The comparison is primarily of the selected findings and their verified scope, with content differences assessed separately above.
