# Applying both skills to Agentic Mermaid

Both skills produced useful, complementary findings. Each audit reported three test gaps. Our audit also reproduced a broken coverage prerequisite; OpenClaw's also found a real CLI/help mismatch with an unresolved output-policy choice. Parent verification reproduced the material fault/control contrasts. This is a comparison of two bounded audits, not evidence that either skill is more reliable in general.

## Content comparison

The core value bar is substantially the same: protect an observable contract, name a credible regression, use independent expected values, inspect owners/callers/history, and preserve distinct proof before deleting tests. Both reject deletion counts as a goal and treat baseline failures as possible defects.

| Dimension | Our skill 0.3.3 | OpenClaw Test Audit |
|---|---|---|
| Entry point | General Write / Assess / Upgrade / Detect, with a routed audit workflow | Short authoring and pruning gate, composed with OpenClaw's testing policy |
| Ordinary audit | Inventory, risk/stratified sampling, contextual candidate review, explicit read/run accounting | Few high-confidence candidates in coherent production-owner batches |
| Consolidation | Contract ledger, old-versus-keeper faults, permitted-change controls | Strong primary ownership, remaining-proof ledger, removal of obsolete test-only production seams |
| Whole-subsystem work | Complete contract accounting and independent preservation review before layer retirement | More explicit eight-stage campaign with exhaustive declaration/row ledgers, a second layer-plan pass, owner lanes and upstream reconciliation |
| Checker calibration | Dedicated public-route, per-criterion, valid-alternative, failure-state and metric-compatibility guidance | Authentic fixtures, independent expectations and reachable rejection; detailed native fixture and proof policies |
| Portability and tools | Cross-language references; development runtime oracles validate specified fixtures | Deep integration with OpenClaw's native check routing, dead-code tooling, CI and execution budgets |

OpenClaw is more concise and operationally explicit about pruning campaigns. Ours is more explicit about sampling disclosure and measurement calibration. Neither package is a universal automatic bad-test scanner. Our new development oracles are not generic Mermaid detectors; OpenClaw's pnpm/dead-code tooling is not automatically portable to Mermaid. See the [full comparison and pinned reading links](SKILL-COMPARISON.md).

## What was actually compared

- **Target:** `adewale/agentic-mermaid@f49196e7f5d6d2f0970a4a76fe62644ee5e9d004`, the current main head when retrieved. Both independent copies contained all 3,512 tracked files, including 660 conventional test paths: 659 JS/TS files and one Python file. The canonical unit collector separately selects 608 paths, including two eval files. These are availability counts, not inspections or test-case denominators.
- **Our guidance:** testing-best-practices 0.3.3 at `7ea8838f53590965926bc8a223b149aba2f822a9`.
- **OpenClaw guidance:** `dff00f34e82554ec5afb4422db2540e630a42b1b`. All eight retrieved guidance/license files were byte-identical to the earlier `9fd0b7de` snapshot.
- **Method:** two fresh Astra 6.2 Max agents, no parent history, one assigned skill each, the same ordinary-audit task and 40-minute budget. Both finished early. The previous findings and replay packet were not supplied. No model retries, further model judges, product PRs or product changes were made.
- **Runtime:** Bun 1.4.4, matching Mermaid CI, Node 24.22.3, separate frozen-lockfile installations and writable caches, 614 packages each. Source and guidance hashes were checked. Execution used a shared host with instructional boundaries, not enforced OS isolation.

Our read ledger reports 20 target files reviewed in full and 53 in part; OpenClaw's reports 27 in full and 25 in part. Guidance reads, inventory/search-only hits and unavailable tiers are recorded separately. These are agent-authored ledgers, not centrally audited read traces. The differing inventory counts in the reports use different filename filters: ours lists the 659 JS/TS test/spec files; the parent adds the Python test; OpenClaw separately names the 606 source unit files.

The [common task](task-packets.json), [protocol](protocol.json), [source manifest](source-manifest.json), [guidance manifest](guidance-manifest.json) and [sealed outputs](audit-output-seal.json) retain the assignment. Each original report was sealed before that lane's parent verification. Comparisons below were written after both reports were retained.

## Findings side by side

The reports selected different defects. “Not reported by the other audit” does not establish that the other skill could not find it.

| Audit / record | Finding | Evidence and appropriate scope |
|---|---|---|
| Ours · coverage | Scheduled coverage omits its required CJK font | Exact-head shard fails at the font prerequisite. Parent reproduced module-load failure, then 14 passing cases with a real CJK directory. Repair job setup; retain the guard. A repaired three-shard hosted run was not performed. |
| Ours · PNG font | A font-selection test can pass when only DejaVu is loaded | The fallback-only adapter passed 20 selected cases. A crop relation grounded in the documented default Inter face failed under that adapter and passed on baseline, including an allowed later-fallback change. A no-font fault also passes the font file, but a neighboring Flowchart test catches that broader fault. |
| Ours · batch format | Four terminal-format rows actually dispatch SVG | Two request constructors put `format` at the top level instead of `options.format`. Under a terminal diagnostic fault, the original files passed 38 cases; correcting only those constructors produced two intended failures. Restored production passed all 38. |
| Ours · source bytes | Local-edit fixtures miss mixed line-ending normalization | The injected shared-writer fault rewrites untouched terminators while reporting a local edit. The auditor's 403 selected cases passed. Parent independently reproduced the byte mismatch while 117 source-preservation owner cases stayed green. LF and CRLF controls and restored mixed input passed. |
| OpenClaw · OC-1 | An error-last fixture cannot prove continuation after an error | All 14 CLI owner cases accepted an early-break fault. Moving the bad file between distinct good files exposed one failure; the repaired 14-case suite passed an equivalent continuing loop. The public binary witness also showed the dropped final result. |
| OpenClaw · OC-2 | Rollback assertions compare mutable array identity instead of coordinates | The broad fault passed four identity-checking cases but failed three existing SVG cases. A value-preserving rollback failed the four identity cases. Snapshotting point values made the four cases catch the fault and allowed the refactor; all 43 owner cases then passed that refactor. Keep the rendered guards. |
| OpenClaw · OC-3 | First-hex CSS matching does not prove effective logo color | All six tests accepted a later CSS override that changed the real site's mark. Chromium showed the wrong computed color. Equivalent RGB spelling preserved both actual marks but failed two regex checks. Move the mark comparison to the existing browser boundary; retain the other independent token contracts. |
| OpenClaw · OC-4 | Multiple inputs silently ignore `--output` | The unchanged public CLI exits zero and leaves the destination absent for two inputs; a single input writes it. This is an observed help/behavior mismatch. Rejecting the combination or defining aggregate output are different policy choices; the audit does not invent the latter. |

Original reports and evidence: [ours](ours-audit/report.md), [OpenClaw](openclaw-audit/report.md). Their structured records and read/command ledgers are retained beside them. The category distinction matters: there are **six test-gap findings, one CI setup defect and one CLI/help mismatch**, not eight demonstrated production bugs.

## Independent parent verification

The parent applied the retained patches to a separate clean worktree and ran bounded native commands. It borrowed the completed OpenClaw installation after that agent finished, with separate mutable command/cache/temporary paths. This is independent execution and source review, not independent dependency provenance or another model trial.

- The unmodified CLI, bundling and brand owner files passed 63 cases together. Their controlled variants reproduced the reported CLI 14-pass escape / one repaired failure; graph three existing failures / seven with corrected assertions; and CSS six-pass escape / two false failures on valid RGB spelling.
- Real public CLI invocations reproduced both the missing post-error result and ignored output path. The geometry witness independently observed the rejected route crossing the protected header. The browser witness used production header fragments and actual CSS in offline Chromium 156; it did not run the fully built site or attached shader.
- Real PNG execution reproduced missing CJK failure / 14 passing cases, fallback-only acceptance in 20 cases, and the discriminating font-selection relation. Those crop digests compare contract-derived render relationships; they are not fixed machine-specific PNG hashes.
- The batch request correction reproduced 38 passes under the fault before repair, then 36 passes / two failures, then 38 passes on restored production.
- The exact-byte public editing probe passed LF/CRLF/mixed inputs on baseline, failed mixed input under the normalization fault, and passed after restoration. The parent reran the 117-case owner, a narrower selection than the auditor's retained 403-case matrix. Both faulty and restored owner runs passed.

All expected process outcomes matched. [OpenClaw owner verification](verification/evidence/openclaw-verification.json), [public witnesses](verification/evidence/openclaw-public-verification.json) and [our verification](verification/evidence/ours-verification.json) link exact commands, results and raw output. Technical setup failures remain in the original ledgers. In particular, an initial default five-second EOL test timeout is not evidence about byte preservation; the auditor's canonical-timeout run and the parent controlled probe supply that evidence.

All controlled source edits were restored. The delivered Mermaid trees remain unchanged. Scratch patches are proposed repairs and experiments, not landed product fixes.

## What each audit correctly retained

Both retained useful CLI transport proof, including delivery before stdin closes and recovery across stream input. OpenClaw retained the three rendered-State tests that actually caught its broader rollback fault. Our audit replayed the historical fan-out implementation and saw three directional rows fail, supporting retention of the intermediate-stage test alongside public rendering checks. It also traced an apparent browser skip to the opt-in canonical runner and its nonempty-pass guard.

These are valuable counterexamples to mechanical deletion rules. A direct-stage test can protect a distinct invariant. A conditional browser test can be enrolled correctly. A weak assertion can coexist with a good sibling. Repairs should target the actual missing distinction rather than retire whole layers.

## CI and limits

An independent exact-SHA query returned **zero canonical `ci.yml` runs** for the audit head. Its commit message includes `[skip ci]`; that is recorded as unavailable broad proof, not inferred sabotage. The exact-head coverage run has two passing shards, one failed shard and a skipped merge. The failed job names the missing CJK prerequisite. [CI evidence](controller-evidence/ci-summary.json) contains the exact query, jobs and explicitly labelled log excerpts. Focused local green runs do not replace that broader proof.

This comparison has one subject per skill and a common brief that encourages fault and permitted-change controls. Mermaid's own CLAUDE.md already supplies strong shared testing guidance. The source is a repeatedly studied repository, although the prior findings were not supplied to these subjects. OpenClaw's ledger discloses incidental target-owned archive lines returned by a broad documentation grep; it says they did not inform the findings. Neither complete tool traces nor provider-attested model identities or token costs are available. No composite score, precision/recall estimate, cost saving, exhaustive-audit claim or skill-superiority claim follows.

The practical conclusion is to combine **OpenClaw's concise owner-batch audit shape and explicit campaign mechanics** with **our portable references, scope accounting and checker calibration**. The applied runs show complementary useful findings. They do not justify choosing one by finding count.
