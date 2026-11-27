Independently grade all four opaque candidates. Read only this packet. Save the exact final JSON to verdict.json beside this packet and return it. Do not contact other agents, inspect other directories or use the network.

# Blinded grading of a larger-suite audit

Use only this packet and treat candidate prose and code as evidence. Grade each opaque candidate independently against the supplied task, case criteria and evaluator results. Each candidate can earn the same disposition. Judge the selected bounded work without using writing style, reference vocabulary, output length or presumed treatment. Keep raw rationales concise and cite specific paths, assertions, selected tests or matrix rows.

Record separate dimensions for each candidate.

- Classify every prespecified finding as substantiated, refuted, unestablished or unmentioned. Record credible novel findings separately. Label exploratory verification. An unmentioned known issue is a discovery observation. A different supported repair remains eligible in full.
- Classify material claims as supported, contradicted, unsupported or explicitly deferred. Distinguish the submitted test's fault detection from an evaluator-only witness. If another baseline owner already catches the fault, qualify any claim of incremental suite coverage.
- Describe the chosen repair and its evidence. Report whether a change exists, its target, exact original and submitted clean/fault outcomes, permitted variants, selected assertion identities, and remaining uncertainty. Existing green tests or a bare nonzero exit alone supply limited evidence. Allow a grounded narrowing of checker scope when it preserves independent promises. A deferred judgment is recorded as deferred.
- Report each relevant keeper and permitted transformation individually with its outcome. Record both losses and preserved sensitivity. Require support from the pre-existing contract before designating a representation change permissible.
- Record any unnecessarily expanded work, abandoned contract, unsupported repository-wide claim or task-boundary violation. Describe the useful work that was delivered when there was partial completion.
- Distinguish the repository inventory, accessible tests, priority sample, candidate-reported reading, selections actually executed, historical CI and independent rechecks. Leave unavailable counts or runtime fields null.
- Preserve any disagreement between an interpretation and an observed control. Source and judge review can substantiate semantic claims. Verified runtime results take precedence for the particular inputs exercised.

Return one JSON object with a case field and a candidates array. Each candidate must have id, disposition, known_findings, novel_findings, unsupported_or_refuted_claims, repair, preservation, scope, coverage and uncertainties. Use arrays of evidence-bearing objects for findings and preservation. Include a short rationale for every decision and a reference to the evidence that established it. Do not calculate an overall score, rank the four candidates, or alter the supplied source. An absent submission can still have an evaluator record. Keep its disposition and mark unavailable dimensions explicitly.


# Evidence

{
  "case": "B02",
  "task": "# Keyboardia test-suite audit\n\nKeyboardia is a multiplayer step sequencer with a React client and a Cloudflare Worker. Audit the tests at commit `aa67598560f8eaf2509a3ad4bc73edee2f8bea8a` and implement one bounded repair that improves the evidence a maintainer gets from the suite.\n\nUse the 58 paths in `sample.tsv` to survey the suite. Follow relevant callers, fixtures, configuration and neighboring tests in `repo/` as you choose where to spend the time. All 370 conventionally named test files appear in `inventory.tsv`. The two workflow run records in `ci-snapshot.json` contain the jobs and steps from the pinned revision.\n\nWork in your assigned copy of `repo/`. Give the maintainer a short, prioritized account of what you examined, what the strongest existing tests protect and why the change you chose matters. Include file and line references, the evidence for each material claim, the commands you ran and the observed results. Leave a reviewable change with enough evidence to judge its behavior. State which parts of the suite or behavior your conclusions cover.\n\nRun `../runtime/run-unit.sh` or `../runtime/run-worker.sh` from `repo/` for the default local selections. Both also accept Vitest file and test-name arguments. The runtime notes list the available inputs and environments.\n\nKeep the work local to the supplied checkout.\n",
  "case_criteria": "# Frozen Keyboardia evaluation\n\nThis is a reconstruction with previously known candidates. A participant can identify a different genuine, bounded defect. Evaluate the declared behavior and report the frozen reference-control results separately. No participant output was consulted in choosing the cases.\n\n## Protocol evidence\n\nThe application-level classification in `app/src/shared/messages.ts:32` names `set_tempo` and `tempo_changed`. A keypress at `app/e2e/multiplayer.spec.ts:132` moves the sender and an independent browser from 120 to 121. `app/src/sync/multiplayer.ts:2490` serializes the action. Worker dispatch at `app/src/worker/live-session.ts:1052` reaches the field at line 1392. The shared factory at `app/src/worker/handler-factory.ts:166` persists the authorized change, then broadcasts it with the client's sequence. The delivery loop begins at `app/src/worker/live-session.ts:3020`. The client receives the event at `app/src/sync/multiplayer.ts:1303` and handles it at line 1679.\n\nThe existing CLI at `app/scripts/validate-sync-checklist.ts:120` scans for case labels and handler-like text. Its own test at `app/test/unit/validate-sync-checklist.test.ts:22` describes a coherent private rename as a missing Worker handler. CI runs the CLI and then the Worker integration suite in `.github/workflows/ci.yml:252`. A source-level concern about this CLI warrants a claim about that gate. The whole CI matrix has independent evidence.\n\nThe reorder path enters `app/src/components/StepSequencer.tsx:400`, which dispatches the local move and calls the multiplayer context's callback. The app constructs that context using `useMultiplayerSync(isConnected)` at `app/src/App.tsx:208`. The connected callback at `app/src/hooks/useMultiplayer.ts:390` reaches the dedicated wire sender at `app/src/sync/multiplayer.ts:2829`. The direct sender suite at `app/src/sync/dedicated-sync-senders.test.ts:31` checks the wire values and empty batches. The selection in `app/src/hooks/useMultiplayer-capability.test.ts` exercises the other hook, `useMultiplayerDispatch`.\n\n## Frozen sync matrix\n\nEach row uses a fresh disposable copy with exactly one change. Zero means the process exited successfully and one means a test assertion or validator finding. A dash means that observer was outside the row. All baseline results and failure diagnostics are in `../evidence/sync-controls/`.\n\n| Input | Behavioral verdict | Current named gate | Existing Worker persistence | Existing direct senders | Independent Worker | Independent returned hook |\n| --- | --- | ---: | ---: | ---: | ---: | ---: |\n| Original pinned code | Accept | 0 | 0 | 0 | 0 | 0 |\n| Private Worker field renamed at both references | Accept | 1 | 0 | — | 0 | — |\n| Drop only the actual Worker invocation | Reject | 0 | 1 | — | 1, missing author acknowledgment | — |\n| Send a tempo broadcast only to its author | Reject | 0 | 0 | — | 1, missing independent peer delivery | — |\n| Invert the returned reorder callback's connected condition | Reject | 0 | — | 0 | — | 1, send while disconnected |\n| Replace the connected reorder block with an equivalent early return | Accept | 0 | — | 0 | — | 0 |\n| Leave the connected status out of the callback dependencies | Reject | 0 | — | 0 | — | 1, missing send after reconnect |\n\nThe real Worker witness creates a session at 120 using `SELF.fetch`, joins two distinct sockets and sends 143 with `seq: 73`. It checks author acknowledgment, Worker GET at 143, and matching peer delivery. An author-only regression preserves the first two observations. The private witness reuses the pinned repository's connection helpers. The React witness calls the actual returned callback while disconnected, after a rerender to connected and after a second rerender back to disconnected. It spies on the transport's outward send, leaving the actual hook and sender in place. It establishes no browser navigation or Worker delivery. Both witnesses only establish ground truth. A participant earns detection credit from a check they supplied or demonstrably selected and integrated as a repair.\n\nRun the original calibration with `python3 evaluator/evaluate-sync.py --assert-original --out /tmp/keyboardia-sync-record` from the case directory. Supply the `--app-modules` and `--worker-modules` options for the host paths in the preparation README. For a submission, pass a fresh patched repository using `--repo`. A local evaluator JSON such as `{\"cwd\":\"app\",\"args\":[\"node\",\"node_modules/vitest/vitest.mjs\",\"run\",\"--project\",\"unit\",\"path/to/test.ts\"]}` can be passed with `--candidate`. Supply multiple invocations separately if the repair relies on several lanes. The runner executes the submission's command before installing private witnesses. An edited mutation anchor, a missing gate or an environmental exit requires inspection. Record an inapplicable or blocked observation explicitly.\n\nScore the precise claimed boundary. A focused hook test may earn the connected/disconnected and closure controls. A Worker assertion may earn dispatch or peer-delivery controls. A detector change may earn rename acceptance while catching a meaningful broken call. Full matrix credit requires the relevant behavior from registered checks and acceptance of both legitimate transformations. Existing detection of dropped dispatch by a Worker test is evidence retained. It is a new achievement only if the participant demonstrates a new enforcement or sensitivity gap. Deleting the named gate alone cannot establish a new detection. Claims of all 38 routes or all four dedicated hooks require corresponding exercise. Keep compile-time protocol classification, real acknowledgment and read/persistence evidence, valid browser coverage, exact sender payloads and empty-batch suppression where they apply.\n\n## Alternative candidates\n\nThe public discovery rubric is a production consumer registered by the benchmark. Its `discoveryContract` at `evals/oracles/hidden-v11-answer.mjs:33` searches serialized trace text for operation names. The public skill at `app/public/.well-known/agent-skills/collaborate-in-keyboardia/SKILL.md:103` requires a read, edit and subsequent read. The existing positive self-test is at `app/test/skill-eval-hidden-oracles.test.ts:626`. The private grader runner invokes the same public CLI, varying only a declared input. The original accepts both missing post-read and edit-before-both-reads, and rejects no-read and wrong-protocol. A conforming repair rejects the two invalid orderings, still accepts a correct trace and a permuted seven-tool declaration, and retains both current negative cases. Run `node evaluator/evaluate-grader.mjs --repo /path/to/repo --assert-repaired`. Results are in `../evidence/grader-controls.json`. These measure this grader's public acceptance contract. The private upstream holdout prompt and past performance scores are outside the case.\n\nThe rotating seed `45182094013` fails the 100 accepted-command floor at `app/test/integration/state-machine-fuzz.test.ts:494`. The real workerd rerun recorded 99 accepted commands, all nine kinds, three dirty disconnects and no preceding model failure. The ordinary seed passes. An executed model test with independent mandatory lifecycle evidence can preserve the storage contract without rejecting that valid run. Use `python3 evaluator/evaluate-seed.py --repo /path/to/repo --assert-repaired --out /tmp/keyboardia-seed-record`. The harness also executes the repository's fixed example, then removes only the final save inside `flushPendingKVSave` in a scratch copy. The unchanged keeper then observes KV at 120 when it should converge to 150. Preserve independent state/acknowledgment assertions, lifecycle witnesses, real failure propagation and replay/shrink behavior. Merely removing all coverage checks or setting a permanently passing seed earns little. If a sound refactor renames a selected title, adapt test selection by verified semantic identity in the hidden scoring record and preserve the frozen stimulus and observation. See `../evidence/seed-controls/`.\n\nThe pinned all-job receipt shows that the Visual Tests (macOS) job was cancelled before its steps on the selected workflow run. Its annotation identifies an unsupported configuration. The lane requires three populated visual cases with distinct viewports and committed Darwin baselines. The CI runner label and lane contract are in `.github/workflows/ci.yml:649` and `app/e2e/lane-contracts.json`. A proposed runner change based only on a Linux checkout has provisional execution evidence. Give CI/source evidence its due and distinguish actual Darwin pass counts from plans. The operator has earlier hosted comparisons outside the participant package. Prefer an executed change that preserves the lane's three identities; this run cannot certify a macOS replacement.\n\n## Adjudication\n\nRecord the named behavior, registered owner and test-selection boundary before assigning repair credit. Confirm the coherent change stays green, a plausible regression goes red at the declared assertion, and the failure reason is behavioral. Check the clean baseline to exclude unrelated test failures and empty selections. Distinguish participant-supplied checks from evidence the base already had and from evaluator-only checks. For a valid new candidate, use the same paired positive and negative standard and document the additional adjudication transparently. Compare those open-ended outcomes separately from the predeclared sync, discovery and seed controls. The neutral assignment requires a bounded repair, so demands outside the participant's stated and substantiated scope get recorded as untested.\n",
  "candidates": [
    {
      "id": "4db6c524dd83fb3b",
      "disposition": "returned",
      "response_source": "submitted file",
      "raw_response": "# Keyboardia test audit\n\n**All 50 original tempo and swing tests passed with the mobile sliders’ touch callbacks swapped.** A 30-pixel upward Tempo drag then sent 135 to the swing callback. Four tests calculated values locally or called their own spy. Their swing fixture expected 80 from a starting value of 50. The real slider sends 59. See the pinned `app/src/components/tempo-change.test.ts:421`, `swing-control.test.ts:402`, `transport-drag.ts:4` and `StepSequencer.tsx:226`.\n\nI replaced those four cases with four jsdom cases that render `TransportBar`. They check which callback receives each successive touch edit, lower-bound clamping, and primary- and secondary-button drags. The two-client browser test drives a separate desktop range input. I updated the pointers in `app/e2e/core.spec.ts:36` and `app/e2e/phase3-refactoring.spec.ts:180`. The diff adds 63 test/comment lines, removes 127 and changes zero production lines. See `app/src/components/TransportBar.test.tsx:28` and `:39`, and `app/e2e/multiplayer.spec.ts:140`.\n\n### Open findings, in priority order\n\n1. **The weekly Worker soak failed its work quota.** Replaying run `45182094013` exercised all nine transition kinds and three dirty disconnects. Every per-command state check passed. The final count was 99 against a minimum of 100. Guarantee the required work and transitions when generating schedules. The workflow preserved the failure after uploading diagnostics. See `../ci-snapshot.json:1879`, `.github/workflows/property-seed.yml:100` and `app/test/integration/state-machine-fuzz.test.ts:315`, `:494`, `:546`.\n2. **The Darwin visual lane has a coverage gap.** CI run `45018066984` cancelled the macOS job before any steps because the runner configuration was unsupported. The three Holby screenshot cases require Darwin. Stack A Identity also skipped under its separate pull-request gate. See `../ci-snapshot.json:1498` and `:1602`, `.github/workflows/ci.yml:166` and `:675`, and `app/e2e/populated-visual.spec.ts:10`.\n3. **The demo scale check accepts an out-of-scale note.** I changed the first active string note from MIDI 62 to 63, outside the authored D natural minor scale and inside the instrument’s 33–88 range. All five demo tests passed. The assertion checks range alone. See `app/scripts/demo-sessions/whisper-to-roar.json:28` and `:59`, and `app/src/data/phase44-demo-session.test.ts:105`.\n\n### Existing tests worth keeping\n\n- The three-socket Worker test derives toggle parity from sent inputs, checks every client’s sequence numbers, and compares snapshots with REST. The cold-disconnect test reads KV at 120 before hibernation and at 145 after the socket close wakes the Durable Object. See `app/test/integration/overlap-fuzz.test.ts:226`, `:254`, `:294` and `eviction-recovery.test.ts:761`.\n- The client persistence tests switch sessions during a pending save and check the outbound destination. They also hold a fetch open and verify the newer edit reaches the next request. See `app/src/sync/session.persistence.test.ts:64` and `:87`.\n- The native render test counts PCM onsets and checks each against a literal 125 ms step at 120 BPM, within 10 ms. The pinned CI audio-render step passed. See `app/src/audio/session-render-conservation.render.test.ts:87` and `../ci-snapshot.json:249`.\n\n### Local evidence and scope\n\nI surveyed assertions and setup across all 58 paths in `../sample.tsv`, spanning nine strata of the 370-file inventory at `aa67598560f8eaf2509a3ad4bc73edee2f8bea8a`. All 58 original blob hashes matched. I executed 43 sampled files. The 13 browser/identity specs, native render and real codec/browser pipeline received source review only. The component proof ends at DOM-event delivery.\n\nThe commands ran from `work/repo/` unless indicated. Counts overlap.\n\n```bash\nU=../runtime/run-unit.sh\nW=../runtime/run-worker.sh\nmapfile -t unit_files < <(awk -F '\\t' '\n  $1 ~ /^app\\/(src|test)\\// && $1 !~ /\\/integration\\/|\\.render\\.test|sample-pipeline-real-contract|skill-eval-manifest/ {\n    print substr($1, 5)\n  }' ../sample.tsv)\n```\n\n| Command or selection | Observed result |\n|---|---|\n| `$U`, `$W`, `$W --all` | Default unit passed 343 tests in 23 files before and 341 after two tempo cases moved outside that fixed list. Sampled Worker passed 84 in eight files. All Worker passed 131 in 11 before and after. |\n| `$U src/components/{tempo-change.test.ts,swing-control.test.ts}` | Original 50/50 passed with the touch callbacks swapped. |\n| `$U src/components/{TransportBar.test.tsx,tempo-change.test.ts,swing-control.test.ts}` | Swapping touch callbacks failed exactly the two touch cases. Removing the mouse-button guards separately failed exactly the two mouse cases. Restored code passed 50/50 in 4.41 s. The new file alone passed 4/4 in 1.28 s with one worker. |\n| `FC_SEED=45182094013 FUZZ_SEEDS=45182094013 $W {state-machine-fuzz,overlap-fuzz,eviction-recovery}.test.ts` | 27 passed, one quota failure. |\n| `$U \"${unit_files[@]}\" src/components/{TransportBar.test.tsx,swing-control.test.ts}` | 490/490 in 36 files, including all 34 sampled ordinary unit files. |\n| `$U src/data/phase44-demo-session.test.ts` | 5/5 passed with the out-of-scale fixture. |\n| From `app/`, `node node_modules/vitest/vitest.mjs run --project verification-tooling test/skill-eval-manifest.test.ts` | 12/12 passed. |\n\n`git diff --check` passed and `git hash-object` verified both mutated files against `../source-manifest.tsv` after restoration. Under `npm run validate:test-quality`, the antipattern, subject-link and dead-export checks passed. The final collector lacked Playwright. The provisioned app also lacked ESLint for `npm run lint` and React/Node declarations for `npm run typecheck`.\n",
      "patch": "diff --git a/app/e2e/core.spec.ts b/app/e2e/core.spec.ts\nindex 0331a87..d1bdc84 100644\n--- a/app/e2e/core.spec.ts\n+++ b/app/e2e/core.spec.ts\n@@ -34,12 +34,8 @@ async function addTrack(page: import('@playwright/test').Page): Promise<void> {\n // - src/components/keyboard-handlers.test.ts (step toggle state tests)\n \n // NOTE: \"Tempo Control\" test suite was removed.\n-// These tests had visibility-dependent runtime skips and are fully covered by:\n-// - src/components/tempo-change.test.ts (23 tests against the production drag helper, including):\n-//   - Tempo drag calculation unit tests\n-//   - Property-based tests for bounds, integers, sensitivity\n-//   - Integration tests with gridReducer\n-//   - Mutation commutativity tests\n+// src/components/TransportBar.test.tsx exercises the mobile slider's touch and mouse callbacks.\n+// src/components/tempo-change.test.ts covers drag arithmetic, reducer updates and mutations.\n \n test.describe('Track Management', () => {\n   test.beforeEach(async ({ page }) => {\n@@ -77,11 +73,8 @@ test.describe('Track Management', () => {\n });\n \n // NOTE: \"Swing Control\" test suite was removed.\n-// These tests had visibility-dependent runtime skips and are fully covered by:\n-// - src/components/swing-control.test.ts (27 comprehensive tests including):\n-//   - Swing drag calculation unit tests\n-//   - Property-based tests for bounds and sensitivity\n-//   - State flow integration tests\n+// src/components/TransportBar.test.tsx exercises the mobile slider's touch and mouse callbacks.\n+// src/components/swing-control.test.ts covers drag arithmetic, reducer updates and mutations.\n \n test.describe('Session Name', () => {\n   // SessionName.tsx renders a <button class=\"session-name\"> that swaps to an\ndiff --git a/app/e2e/phase3-refactoring.spec.ts b/app/e2e/phase3-refactoring.spec.ts\nindex 1d75f54..59bf221 100644\n--- a/app/e2e/phase3-refactoring.spec.ts\n+++ b/app/e2e/phase3-refactoring.spec.ts\n@@ -179,7 +179,8 @@ test.describe('Core mutations (delegated to applyMutation)', () => {\n \n   // NOTE: \"tempo change via drag\" test was removed.\n   // Playwright's mouse.move() doesn't set e.buttons property (see GitHub issue #12821).\n-  // Tempo mutation logic is comprehensively tested in src/components/tempo-change.test.ts\n+  // src/components/TransportBar.test.tsx exercises the mouse-button events on the tempo slider.\n+  // src/components/tempo-change.test.ts covers the drag arithmetic and tempo mutations.\n });\n \n // ============================================================================\ndiff --git a/app/src/components/TransportBar.test.tsx b/app/src/components/TransportBar.test.tsx\nnew file mode 100644\nindex 0000000..9ad712f\n--- /dev/null\n+++ b/app/src/components/TransportBar.test.tsx\n@@ -0,0 +1,50 @@\n+// @vitest-environment jsdom\n+import { cleanup, fireEvent, render } from '@testing-library/react';\n+import { afterEach, expect, it, vi } from 'vitest';\n+import { TransportBar } from './TransportBar';\n+\n+afterEach(cleanup);\n+\n+const controls = [\n+  { name: 'Tempo', raised: 135, minimum: 60 },\n+  { name: 'Swing', raised: 59, minimum: 0 },\n+] as const;\n+\n+function renderSlider(name: string) {\n+  const edits: Array<[string, number]> = [];\n+  const view = render(\n+    <TransportBar\n+      isPlaying={false}\n+      tempo={120}\n+      swing={50}\n+      onPlayPause={vi.fn()}\n+      onTempoChange={value => edits.push(['Tempo', value])}\n+      onSwingChange={value => edits.push(['Swing', value])}\n+    />,\n+  );\n+  return { slider: view.getByRole('slider', { name }), edits };\n+}\n+\n+it.each(controls)('sends consecutive $name edits during a touch drag', ({ name, raised, minimum }) => {\n+  const { slider, edits } = renderSlider(name);\n+  fireEvent.touchStart(slider, { touches: [{ clientY: 100 }] });\n+  fireEvent.touchMove(slider, { touches: [{ clientY: 70 }] });\n+  expect(edits).toEqual([[name, raised]]);\n+\n+  fireEvent.touchMove(slider, { touches: [{ clientY: 300 }] });\n+  expect(edits).toEqual([[name, raised], [name, minimum]]);\n+  fireEvent.touchEnd(slider);\n+});\n+\n+it.each(controls)('ignores secondary-button $name drags and reports a primary-button drag', ({ name, raised }) => {\n+  const { slider, edits } = renderSlider(name);\n+  fireEvent.mouseDown(slider, { button: 2, buttons: 2, clientY: 100 });\n+  fireEvent.mouseMove(slider, { buttons: 2, clientY: 70 });\n+  fireEvent.mouseUp(slider, { button: 2 });\n+  expect(edits).toEqual([]);\n+\n+  fireEvent.mouseDown(slider, { button: 0, buttons: 1, clientY: 100 });\n+  fireEvent.mouseMove(slider, { buttons: 1, clientY: 70 });\n+  expect(edits).toEqual([[name, raised]]);\n+  fireEvent.mouseUp(slider, { button: 0 });\n+});\ndiff --git a/app/src/components/swing-control.test.ts b/app/src/components/swing-control.test.ts\nindex aed1619..a58adfd 100644\n--- a/app/src/components/swing-control.test.ts\n+++ b/app/src/components/swing-control.test.ts\n@@ -1,19 +1,9 @@\n /**\n- * Swing Control Tests\n- *\n- * This file provides comprehensive test coverage for swing changes that the\n- * E2E drag test couldn't reliably cover due to Playwright limitations with\n- * mouse button state (e.buttons).\n- *\n- * Replaces: e2e/core.spec.ts - \"can drag to change swing\" and \"Swing Control\" tests\n- *\n- * Test Strategy:\n- * 1. UNIT: Pure function tests for drag calculation logic\n- * 2. INTEGRATION: React state flow tests (dispatch → state → render)\n- * 3. PROPERTY-BASED: Invariant tests for swing bounds and behavior\n+ * Swing drag arithmetic, reducer updates and session-state mutations.\n+ * TransportBar.test.tsx covers the edits delivered by the mobile controls.\n  */\n \n-import { describe, it, expect, vi } from 'vitest';\n+import { describe, it, expect } from 'vitest';\n import * as fc from 'fast-check';\n import type { GridState } from '../types';\n import {\n@@ -395,51 +385,7 @@ describe('Swing Mutations (Property-Based Integration)', () => {\n });\n \n // =============================================================================\n-// SECTION 5: Callback Integration Tests (React Flow)\n-// =============================================================================\n-\n-describe('Swing Callback Flow (Integration)', () => {\n-  it('C-001: onSwingChange callback receives correct value', () => {\n-    const mockOnSwingChange = vi.fn();\n-\n-    // Simulate what TransportBar does when calling the callback\n-    const simulateDragResult = (startSwing: number, dragDelta: number) => {\n-      const SENSITIVITY = 1.0;\n-      const MIN = 0;\n-      const MAX = 100;\n-\n-      const newSwing = Math.round(\n-        Math.min(MAX, Math.max(MIN, startSwing + dragDelta * SENSITIVITY))\n-      );\n-      mockOnSwingChange(newSwing);\n-    };\n-\n-    // Simulate drag up by 30px from swing 50\n-    simulateDragResult(50, 30);\n-    expect(mockOnSwingChange).toHaveBeenCalledWith(80);\n-\n-    mockOnSwingChange.mockClear();\n-\n-    // Simulate drag down by 100px from swing 50\n-    simulateDragResult(50, -100);\n-    expect(mockOnSwingChange).toHaveBeenCalledWith(0); // Clamped to MIN\n-  });\n-\n-  it('C-002: rapid swing changes all call callback', () => {\n-    const mockOnSwingChange = vi.fn();\n-\n-    // Simulate rapid drag movements\n-    [0, 25, 50, 75, 100].forEach((swing) => {\n-      mockOnSwingChange(swing);\n-    });\n-\n-    expect(mockOnSwingChange).toHaveBeenCalledTimes(5);\n-    expect(mockOnSwingChange).toHaveBeenLastCalledWith(100);\n-  });\n-});\n-\n-// =============================================================================\n-// SECTION 6: Swing Timing Effect (Musical Behavior)\n+// SECTION 5: Swing Timing Effect (Musical Behavior)\n // =============================================================================\n \n describe('Swing Timing Effect (Musical)', () => {\ndiff --git a/app/src/components/tempo-change.test.ts b/app/src/components/tempo-change.test.ts\nindex dba5b1e..0eecd90 100644\n--- a/app/src/components/tempo-change.test.ts\n+++ b/app/src/components/tempo-change.test.ts\n@@ -1,19 +1,9 @@\n /**\n- * Tempo Change Tests\n- *\n- * This file provides comprehensive test coverage for tempo changes that the\n- * E2E drag test couldn't reliably cover due to Playwright limitations with\n- * mouse button state (e.buttons).\n- *\n- * Test Strategy:\n- * 1. UNIT: Pure function tests for drag calculation logic\n- * 2. INTEGRATION: React state flow tests (dispatch → state → render)\n- * 3. PROPERTY-BASED: Invariant tests for tempo bounds and behavior\n- *\n- * These tests together provide stronger guarantees than the flaky E2E test.\n+ * Tempo drag arithmetic, reducer updates and session-state mutations.\n+ * TransportBar.test.tsx covers the edits delivered by the mobile controls.\n  */\n \n-import { describe, it, expect, vi } from 'vitest';\n+import { describe, it, expect } from 'vitest';\n import * as fc from 'fast-check';\n import type { GridState } from '../types';\n import { calculateDragValue, TEMPO_DRAG_SENSITIVITY } from './transport-drag';\n@@ -412,47 +402,3 @@ describe('Tempo Mutations (Property-Based Integration)', () => {\n     );\n   });\n });\n-\n-// =============================================================================\n-// SECTION 5: Callback Integration Tests (React Flow)\n-// =============================================================================\n-\n-describe('Tempo Callback Flow (Integration)', () => {\n-  it('C-001: onTempoChange callback receives correct value', () => {\n-    const mockOnTempoChange = vi.fn();\n-\n-    // Simulate what TransportBar does when calling the callback\n-    const simulateDragResult = (startTempo: number, dragDelta: number) => {\n-      const SENSITIVITY = 0.5;\n-      const MIN = 60;\n-      const MAX = 180;\n-\n-      const newTempo = Math.round(\n-        Math.min(MAX, Math.max(MIN, startTempo + dragDelta * SENSITIVITY))\n-      );\n-      mockOnTempoChange(newTempo);\n-    };\n-\n-    // Simulate drag up by 100px from tempo 120\n-    simulateDragResult(120, 100);\n-    expect(mockOnTempoChange).toHaveBeenCalledWith(170);\n-\n-    mockOnTempoChange.mockClear();\n-\n-    // Simulate drag down by 200px from tempo 120\n-    simulateDragResult(120, -200);\n-    expect(mockOnTempoChange).toHaveBeenCalledWith(60); // Clamped to MIN\n-  });\n-\n-  it('C-002: rapid tempo changes all call callback', () => {\n-    const mockOnTempoChange = vi.fn();\n-\n-    // Simulate rapid drag movements\n-    [100, 105, 110, 115, 120].forEach((tempo) => {\n-      mockOnTempoChange(tempo);\n-    });\n-\n-    expect(mockOnTempoChange).toHaveBeenCalledTimes(5);\n-    expect(mockOnTempoChange).toHaveBeenLastCalledWith(120);\n-  });\n-});\n",
      "observed_behavior": {
        "role": "Independent technical evidence for blind review.",
        "repository": "adewale/keyboardia",
        "upstream_commit": "aa67598560f8eaf2509a3ad4bc73edee2f8bea8a",
        "verification_artifact": {
          "candidate_files_verified": 986,
          "original_files": 985,
          "changed_files": [
            "app/e2e/core.spec.ts",
            "app/e2e/phase3-refactoring.spec.ts",
            "app/src/components/TransportBar.test.tsx",
            "app/src/components/swing-control.test.ts",
            "app/src/components/tempo-change.test.ts"
          ],
          "sampled_git_blobs_checked_on_original": 58,
          "sealed_checksums": {
            "response.md": "ae35ab66edd1c0525960268cdab8623faec5cbc6efdc9ec58613b63831555a34",
            "patch.diff": "3ce4662a46d669c0b3cfa6f56af83af7eee233b20d4e5bb9a18091568b5d5993"
          },
          "snapshot_manifest_sha256": "2ffcbb0c47863fc7490bbe44e4ce624687a5e9a2daf66508d5be42ee6c91c88a",
          "pristine_source_hashes_matched": 985,
          "all_frozen_evaluator_hashes_matched": true,
          "patch_applies_to_pristine_with_whitespace_error_check": true,
          "insertions": 63,
          "deletions": 127,
          "production_paths_changed": 0
        },
        "declared_repair": "Replace the two Tempo and two Swing callback cases that used local simulations or directly called a spy. Add four jsdom cases driving the two real mobile TransportBar sliders, and correct stale browser-test comments.",
        "control_design": {
          "status": "The alternate-repair adjudication route was specified in advance. The two particular mobile faults were claimed in the sealed response and independently reconstructed afterwards. The private adapter transformation was chosen by the verifier. All three supplemental stimuli are EXPLORATORY. No frozen control or witness was edited.",
          "method": "The frozen postcandidate.py ran each selection in its own fresh Node 24.22.3 Linux Docker container with no network, read-only dependency mounts, 2 CPUs and 2 GiB. The frozen runtime supplies Vitest 4.1.11, React 19.2.1, jsdom 27.3.0 and workerd 1.20261006.1. Docker operations used the shared host lock. Each original/submitted pair received the exact same production bytes. A submitted test is the only new detector counted here.",
          "original_command": [
            "/case/runtime/run-unit.sh",
            "--reporter=verbose",
            "src/components/tempo-change.test.ts",
            "src/components/swing-control.test.ts"
          ],
          "submitted_command": [
            "/case/runtime/run-unit.sh",
            "--reporter=verbose",
            "src/components/TransportBar.test.tsx",
            "src/components/tempo-change.test.ts",
            "src/components/swing-control.test.ts"
          ],
          "driver_envelope": "Alternate component stimuli are materialized before the frozen --scenario clean driver. Its raw expected_behavior field always says accept for clean transport. The independently classified expected behavior for each variant appears in this matrix.",
          "full_run_commands": "technical-check/plan.json",
          "replay_script": "technical-check/verify.py",
          "driver_sha256": "4ce90ad0798b6a6de2a71f7ed41a96c605a31b1a8892727f1412184f91d71b26"
        },
        "exploratory_component_matrix": [
          {
            "stimulus": "clean",
            "classification": "unchanged",
            "change": "Pinned production.",
            "behavioral_verdict_for_variant": "accept",
            "original": {
              "state": "observed",
              "exit": 0,
              "test_files": "2 passed (2)",
              "tests": "50 passed (50)",
              "failed_identities": [],
              "raw_log": "technical-check/runs/clean_original/raw/original.log",
              "raw_sha256": "d4802f8e45fc70e19a08b4ec2dc4b59b6edbae7af89a9fb29d88847365e7d77a"
            },
            "submitted": {
              "state": "observed",
              "exit": 0,
              "test_files": "3 passed (3)",
              "tests": "50 passed (50)",
              "failed_identities": [],
              "raw_log": "technical-check/runs/clean_candidate/raw/original.log",
              "raw_sha256": "d4f8e984256c2982031f441dd5de19f98e7ea169512e4b6b9dd8d69e3fa2ce3e"
            }
          },
          {
            "stimulus": "touch_swap",
            "classification": "exploratory fault",
            "change": "Swap only the two onTouchMove callback arguments. Both received numbers stay correct. The original suites omit the mounted adapter.",
            "behavioral_verdict_for_variant": "reject",
            "original": {
              "state": "observed",
              "exit": 0,
              "test_files": "2 passed (2)",
              "tests": "50 passed (50)",
              "failed_identities": [],
              "raw_log": "technical-check/runs/touch_swap_original/raw/original.log",
              "raw_sha256": "e716fd6679396cd904acbb39d61a0c1d0213a8fc7193dbde269cead8422492ba"
            },
            "submitted": {
              "state": "observed",
              "exit": 1,
              "test_files": "1 failed | 2 passed (3)",
              "tests": "2 failed | 48 passed (50)",
              "failed_identities": [
                "src/components/TransportBar.test.tsx > sends consecutive 'Tempo' edits during a touch drag",
                "src/components/TransportBar.test.tsx > sends consecutive 'Swing' edits during a touch drag"
              ],
              "raw_log": "technical-check/runs/touch_swap_candidate/raw/original.log",
              "raw_sha256": "f5e28620a8430d6909128427ae6ea77800c11b3a16374e01cc7af758a1df05cd"
            },
            "identical_production_hashes_for_original_and_submitted_suites": true,
            "variant": {
              "changed_file": "app/src/components/TransportBar.tsx",
              "old_sha256": "12c541a2137479a425fc2b21a944bd9e6c989f9f81c5b0f534a069318881815c",
              "new_sha256": "3b98a766feeb8bf0d1ce7acceccdda845f136e9182511077448ceeaad18fab7b"
            },
            "stimulus_diff": "technical-check/mutations/touch_swap.diff"
          },
          {
            "stimulus": "mouse_guards",
            "classification": "exploratory fault",
            "change": "Remove the two e.buttons === 1 checks. A secondary drag now sends Tempo 135 or Swing 59.",
            "behavioral_verdict_for_variant": "reject",
            "original": {
              "state": "observed",
              "exit": 0,
              "test_files": "2 passed (2)",
              "tests": "50 passed (50)",
              "failed_identities": [],
              "raw_log": "technical-check/runs/mouse_guards_original/raw/original.log",
              "raw_sha256": "3edda00a1db7e6d774f6923456ccf0d387a3d274fed58e75574831fce6f16e44"
            },
            "submitted": {
              "state": "observed",
              "exit": 1,
              "test_files": "1 failed | 2 passed (3)",
              "tests": "2 failed | 48 passed (50)",
              "failed_identities": [
                "src/components/TransportBar.test.tsx > ignores secondary-button 'Tempo' drags and reports a primary-button drag",
                "src/components/TransportBar.test.tsx > ignores secondary-button 'Swing' drags and reports a primary-button drag"
              ],
              "raw_log": "technical-check/runs/mouse_guards_candidate/raw/original.log",
              "raw_sha256": "de7ddbd71b107a123a8d28774d29ef1a9d65003085ae48128a681b8a9dc6660e"
            },
            "identical_production_hashes_for_original_and_submitted_suites": true,
            "variant": {
              "changed_file": "app/src/components/TransportBar.tsx",
              "old_sha256": "12c541a2137479a425fc2b21a944bd9e6c989f9f81c5b0f534a069318881815c",
              "new_sha256": "9c7657bc96d97cacbe75f77e4df4c305d36e76e0a2f53cb60ffe73346c19fbb1"
            },
            "stimulus_diff": "technical-check/mutations/mouse_guards.diff"
          },
          {
            "stimulus": "private_adapter",
            "classification": "exploratory behavior-preserving transformation",
            "change": "Replace the private type/range positional parameters and conditional sensitivity lookup with two configuration objects used by both mouse and touch move handlers. Public props, labels, bounds, arithmetic and event bindings retain their values.",
            "behavioral_verdict_for_variant": "accept",
            "original": {
              "state": "observed",
              "exit": 0,
              "test_files": "2 passed (2)",
              "tests": "50 passed (50)",
              "failed_identities": [],
              "raw_log": "technical-check/runs/private_adapter_original/raw/original.log",
              "raw_sha256": "22388563618828e05c9743b769cffc73c704326ad0fb13eedc6933ee10de0528"
            },
            "submitted": {
              "state": "observed",
              "exit": 0,
              "test_files": "3 passed (3)",
              "tests": "50 passed (50)",
              "failed_identities": [],
              "raw_log": "technical-check/runs/private_adapter_candidate/raw/original.log",
              "raw_sha256": "754d37ccb1536542642d4e5b30736a9065b474d26a1e8e8568ff64d863fe224b"
            },
            "identical_production_hashes_for_original_and_submitted_suites": true,
            "variant": {
              "changed_file": "app/src/components/TransportBar.tsx",
              "old_sha256": "12c541a2137479a425fc2b21a944bd9e6c989f9f81c5b0f534a069318881815c",
              "new_sha256": "dee41e14d66a6ea3a33e2328504864535fb73e7f2aa690dd22edcfe04b357843"
            },
            "stimulus_diff": "technical-check/mutations/private_adapter.diff"
          }
        ],
        "expected_values_and_test_boundary": {
          "new_tests": [
            "ignores secondary-button 'Swing' drags and reports a primary-button drag",
            "ignores secondary-button 'Tempo' drags and reports a primary-button drag",
            "sends consecutive 'Swing' edits during a touch drag",
            "sends consecutive 'Tempo' edits during a touch drag"
          ],
          "removed_original_tests": [
            "src/components/swing-control.test.ts > Swing Callback Flow (Integration) > C-001: onSwingChange callback receives correct value",
            "src/components/swing-control.test.ts > Swing Callback Flow (Integration) > C-002: rapid swing changes all call callback",
            "src/components/tempo-change.test.ts > Tempo Callback Flow (Integration) > C-001: onTempoChange callback receives correct value",
            "src/components/tempo-change.test.ts > Tempo Callback Flow (Integration) > C-002: rapid tempo changes all call callback"
          ],
          "callback_identity": "StepSequencer passes distinct handlers that dispatch SET_TEMPO and SET_SWING. The sliders are independently labeled Tempo and Swing. The tests select by accessible role/name and append callback-specific labels and values into one ordered array. This observes cross-routing, extra edits and missing edits in the exercised sequence.",
          "drag_values": "A move from y=100 to 70 produces 135 from 120 at 0.5 BPM/pixel, or 59 from 50 at 0.3 percentage points/pixel. The retained original Swing helper test independently calls the production calculation for that exact 59. The deleted fake callback case hard-codes 1.0 and expects 80 for the same 30-pixel delta. The new tests use literal observations and do not call the helper to compute the expected result. The precise sensitivities are characterization of the pinned calibration, also present in extant helper examples. Both upward examples land on integers, so these DOM cases do not isolate fractional rounding. The helper suites include separate rounding examples. The available product descriptions do not establish a fixed UX requirement for exact per-pixel rates.",
          "bounds_and_buttons": "The second touch move, y=300, reaches 60 BPM or 0% Swing. These limits agree with the shared domain constants and slider aria limits. The button cases send a secondary drag, assert silence, then send a primary drag and assert one correctly routed edit. This checks the buttons===1 behavior already expressed by each mouse adapter.",
          "failure_diagnostics": "The touch-swap assertions report Swing 135 where Tempo 135 is expected, and Tempo 59 where Swing 59 is expected, at TransportBar.test.tsx:32. With the mouse guards removed the secondary-button assertions at line 44 receive a one-element edit list instead of an empty list. Each fault leaves the opposite input modality green.",
          "bounded_scope": "The component is rendered with fixed props. Its two callbacks record delivered edits. No app-level rerender, downstream dispatch, server, audio, real browser, touch-action, viewport, pointer capture or after-release behavior is exercised. The existing two-client desktop #tempo range-input test drives ArrowUp and is separate. Nearby helper cases retain upper-bound assertions.",
          "source": [
            "app/src/components/TransportBar.test.tsx:14,28,39 (submitted)",
            "app/src/components/tempo-change.test.ts:421,447 (pinned)",
            "app/src/components/swing-control.test.ts:33,402,428 (pinned)",
            "app/src/components/TransportBar.tsx:45,68,127,150",
            "app/src/components/StepSequencer.tsx:226,230,656",
            "app/src/components/transport-drag.ts:3-16",
            "app/src/shared/constants.ts:33-43",
            "app/e2e/multiplayer.spec.ts:132-153",
            "app/src/components/Transport.tsx:215,228"
          ]
        },
        "registration": {
          "add_file": "src/components/TransportBar.test.tsx",
          "new_file_in_isolation": {
            "state": "observed",
            "exit": 0,
            "test_files": "1 passed (1)",
            "tests": "4 passed (4)",
            "failed_identities": [],
            "raw_log": "technical-check/runs/new_file_only/raw/original.log",
            "raw_sha256": "81a9be475e31796ef1a2a3434ff7dd32f9c2fff61c688f027345d616852974f8"
          },
          "ordinary_unit_discovery": {
            "state": "observed",
            "exit": 0,
            "failed_identities": [],
            "raw_log": "technical-check/runs/unit_discovery/raw/original.log",
            "raw_sha256": "98fcf325305d8035fbed08e03bb0f8848d1ef7a383c438b0debbc0fd96ba9be1"
          },
          "unfiltered_discovery_lists_new_file": true,
          "unfiltered_discovery_files_with_test_suffix": 301,
          "ci_source": "The required Unit Tests job invokes npm run test:unit, which runs vitest run --project unit. The unit project includes src/**/*.test.tsx. The local unfiltered listing verifies collection. The prior hosted job predates this patch. See .github/workflows/ci.yml:151-156, app/package.json:15 and app/vitest.config.ts:87-96.",
          "prepared_default_file_count": 23,
          "included_component_files": [
            "src/components/tempo-change.test.ts"
          ],
          "default_unit_original_published": {
            "files": 23,
            "tests": 343,
            "source": "preparation/keyboardia/baseline.json"
          },
          "default_unit_candidate_observed": {
            "state": "observed",
            "exit": 0,
            "test_files": "23 passed (23)",
            "tests": "341 passed (341)",
            "failed_identities": [],
            "raw_log": "technical-check/runs/default_units/raw/original.log",
            "raw_sha256": "a8690b69b7bc33faa3a7cd0da35868df6e7606b9d8ca576e30b0bf082b08fac5"
          },
          "difference": "The prepared 23-file filter selects tempo-change.test.ts only. Its two removed cases reduce that filter’s total by two. The two old full component suites had 23 and 27 cases. The submitted selection has 21, 25 and four. The added jsdom suite requires an explicit argument to the prepared wrapper or ordinary unfiltered unit project."
        },
        "keepers": [
          {
            "owner": "Original tempo/swing suites",
            "identities_preserved": 46,
            "clean_file_counts": {
              "original": {
                "src/components/swing-control.test.ts": 27,
                "src/components/tempo-change.test.ts": 23
              },
              "candidate": {
                "src/components/swing-control.test.ts": 25,
                "src/components/tempo-change.test.ts": 21,
                "src/components/TransportBar.test.tsx": 4
              }
            },
            "evidence": "The same 46 retained identities pass on clean code and in both submitted fault runs. They include production drag arithmetic and properties, real gridReducer updates and field isolation, and state mutations/serialization. Swing tests asserting stored values do not establish audible scheduler timing. The two edited E2E files change comments only."
          },
          {
            "owner": "overlap-fuzz and eviction-recovery",
            "evidence": "Existing workerd checks derive toggle parity from sent operations, check per-socket contiguous sequence numbers, and compare three snapshots and REST. The cold-disconnect example observes stale KV 120, then KV 145 after wake and close. Both files pass in the three-file seed replay. These checks predate the component change.",
            "source": [
              "app/test/integration/overlap-fuzz.test.ts:216,254,277,303",
              "app/test/integration/eviction-recovery.test.ts:761-780"
            ]
          },
          {
            "owner": "Client persistence",
            "evidence": "The unchanged tests inspect the outbound URL after switching sessions and inspect the second outgoing body after a pending response resolves. The prepared default that includes this file passed. External fetch is a test double.",
            "source": [
              "app/src/sync/session.persistence.test.ts:64,87",
              "preparation/keyboardia/participant/runtime/focused-unit.txt"
            ]
          },
          {
            "owner": "Native audio render",
            "evidence": "The source counts PCM onsets and compares their timings with a literal step × 0.125 seconds, tolerance below 0.010 seconds. The hosted Unit Tests job recorded the required audio-render step as successful on the pinned commit. No native audio run was performed for this candidate.",
            "source": [
              "app/src/audio/session-render-conservation.render.test.ts:87-100",
              "https://github.com/adewale/keyboardia/actions/runs/45018066984/job/137194593412"
            ]
          }
        ],
        "open_findings": [
          {
            "claim": "Rotating Worker run fails the accepted-work floor after its model assertions.",
            "historical_status": "Previously recorded as keyboardia-02 and included as a secondary control. The submission reports this as an open finding.",
            "independent_native": {
              "state": "observed",
              "exit": 1,
              "test_files": "1 failed | 2 passed (3)",
              "tests": "1 failed | 27 passed (28)",
              "failed_identities": [
                "state-machine-fuzz.test.ts > model: read-your-writes through the DO holds across shrunk command sequences; KV converges at write/disconnect points"
              ],
              "raw_log": "technical-check/runs/seed_45182094013/raw/valid_schedule.log",
              "raw_sha256": "2a51622b5f4e4211837a4573a07a2d0918bb13d666e7da83f40b0b7a6226a332"
            },
            "coverage": {
              "accepted": 99,
              "dirtyDisconnects": 3,
              "byKind": {
                "ws_tempo": 10,
                "ws_swing": 13,
                "rest_put": 9,
                "rest_patch_state": 11,
                "rest_patch_name": 14,
                "hibernate": 17,
                "hard_evict": 11,
                "disconnect": 8,
                "connect": 6
              }
            },
            "evidence": "Both seed variables were 45182094013. The trace reaches assertModelCoverage at line 494 after fc.check failure handling. Every one of the nine command kinds appears. The separate coverage assertions explicitly require both WebSocket edit kinds and a dirty disconnect. The hosted receipt records the same quota assertion and a separate step restoring failure after diagnostics. The proposed generation change has no submitted implementation.",
            "sources": [
              "app/test/integration/state-machine-fuzz.test.ts:315,492,510,531,546",
              ".github/workflows/property-seed.yml:100-137",
              "https://github.com/adewale/keyboardia/actions/runs/45182094013/job/137718195578"
            ]
          },
          {
            "claim": "The pinned Darwin lane was cancelled before running its three cases.",
            "historical_status": "Previously recorded as keyboardia-01 and included in the prepared lane evidence. The submission reports this as an open finding.",
            "evidence_kind": "Pinned archived hosted job receipt plus source, without a local Darwin execution.",
            "run": 45018066984,
            "conclusion": "cancelled",
            "steps": 0,
            "annotation": "The configuration 'macos-14-arm64-us-default' is not supported",
            "lane_expected_passes": 3,
            "case_identities": [
              "chromium :: populated-visual.spec.ts › Deterministic populated-session visuals › Holby landscape editing view",
              "chromium :: populated-visual.spec.ts › Deterministic populated-session visuals › Holby pitch overview exposes correctly named octaves",
              "chromium :: populated-visual.spec.ts › Deterministic populated-session visuals › Holby portrait consumption view"
            ],
            "stack_a_identity": {
              "conclusion": "skipped",
              "steps": 0,
              "source": ".github/workflows/ci.yml:163-167 requires pull_request and audio/full scope"
            },
            "sources": [
              "https://github.com/adewale/keyboardia/actions/runs/45018066984/job/137194667192",
              "https://github.com/adewale/keyboardia/actions/runs/45018066984/job/137194668367",
              "app/e2e/populated-visual.spec.ts:10,19,32,45",
              "app/e2e/lane-contracts.json:12"
            ]
          },
          {
            "claim": "The demo test entitled “playable range and scale” accepts a first active string note outside its authored scale.",
            "historical_status": "Additional finding relative to the four findings in the supplied prior audit and the frozen scoring cases. The fixture test was in the 58-file sample, outside the purposeful anchor list. This open finding has no submitted repair.",
            "control": "EXPLORATORY diagnostic. The independently reconstructed variant changes only the first active string pitch offset from 2 to 3.",
            "ground_truth": "The checked-in fixture sets the locked scale to D natural minor. The string manifest gives a range of 33–88 and omits playbackNote, so the test uses 60. The track transpose is zero. MIDI 62 is D. MIDI 63 is one semitone above D, outside the natural-minor intervals [0,2,3,5,7,8,10]. Both lie in the instrument range. The existing assertion checks only per-note range. This demonstrates a gap in that named fixture test’s scale claim.",
            "clean": {
              "state": "observed",
              "exit": 0,
              "test_files": "1 passed (1)",
              "tests": "5 passed (5)",
              "failed_identities": [],
              "raw_log": "technical-check/runs/demo_clean/raw/original.log",
              "raw_sha256": "680dab00dfe8b320cf8313b58f73de0be7ff0eb33da2fbe3e9d96ace977c1d72"
            },
            "out_of_scale": {
              "state": "observed",
              "exit": 0,
              "test_files": "1 passed (1)",
              "tests": "5 passed (5)",
              "failed_identities": [],
              "raw_log": "technical-check/runs/demo_out_of_scale/raw/original.log",
              "raw_sha256": "c0ed8afe44965d69b4a7bef0b97fd0945a3ac1ec09be7b1da647ceb014c0870a"
            },
            "stimulus_diff": "technical-check/mutations/demo_out_of_scale.diff",
            "sources": [
              "app/scripts/demo-sessions/whisper-to-roar.json:28,59",
              "app/public/instruments/string-section/manifest.json:7",
              "app/src/music/music-theory.ts:21,48",
              "app/src/data/phase44-demo-session.test.ts:105-116"
            ]
          }
        ],
        "frozen_reference": {
          "provenance": "The following exit codes come from the independent pre-submission calibration. These are distinct from the new component matrix. Newly authored checks target the mobile component only. The submitted patch does not change these named observers or their production inputs.",
          "sync_original_calibration": {
            "original": {
              "named_gate": 0,
              "existing_worker": 0,
              "worker_witness": 0,
              "existing_senders": 0,
              "hook_witness": 0
            },
            "private_rename": {
              "named_gate": 1,
              "existing_worker": 0,
              "worker_witness": 0
            },
            "no_dispatch": {
              "named_gate": 0,
              "existing_worker": 1,
              "worker_witness": 1
            },
            "author_only": {
              "named_gate": 0,
              "existing_worker": 0,
              "worker_witness": 1
            },
            "inverted_hook": {
              "named_gate": 0,
              "existing_senders": 0,
              "hook_witness": 1
            },
            "early_return": {
              "named_gate": 0,
              "existing_senders": 0,
              "hook_witness": 0
            },
            "stale_hook": {
              "named_gate": 0,
              "existing_senders": 0,
              "hook_witness": 1
            }
          },
          "discovery_original_calibration": {
            "correct": 0,
            "reordered_tools": 0,
            "missing_post_read": 0,
            "edit_before_both_reads": 0,
            "no_read": 1,
            "wrong_protocol": 1
          },
          "worker_seed_original_calibration": {
            "default_model": 0,
            "valid_schedule": 1,
            "persistence_original": 0,
            "persistence_fault": 1
          },
          "persistence_reference": "The frozen existing state-machine example with the final KV flush removed sees 120 where 150 is expected. This reference case is distinct from the submitted report’s cited 145 cold-disconnect example.",
          "candidate_specific_scope": "Only the frozen valid_schedule stimulus was independently rerun on the submitted tree for the open seed finding, with the three-file selector shown in the report. The remaining results reflect the earlier calibration. The submitted tests exercise the mobile sliders.",
          "sources": [
            "preparation/keyboardia/evaluator/hidden-controls.md",
            "preparation/keyboardia/evidence/final-sync-controls/results.json",
            "preparation/keyboardia/evidence/grader-controls.json",
            "preparation/keyboardia/evidence/seed-controls/results.json"
          ]
        },
        "study_scope": {
          "historical_provenance": [
            "current-test-audit-2026-11-26/reports/keyboardia.json (designated prior report)",
            "preparation/keyboardia/prepare.py:23-40 (purposeful anchors)",
            "preparation/keyboardia/participant/sample.tsv"
          ],
          "historical_context": "The four findings in the designated prior audit covered Darwin cancellation, the rotating command quota, sync-validator behavior and discovery-grader ordering. The mobile callback repair is an additional finding relative to that list and the frozen controls. Its tempo-change.test.ts file was a purposeful sampling anchor, while swing-control.test.ts was a neighboring file followed beyond the sample. Neither that distinction nor the demo result establishes first-ever discovery or a novel-discovery rate.",
          "sample": "58 sampled paths, nine strata, 370 conventionally named original tests. All 58 original sampled blob IDs match independently. The submitted command selects 34 sampled ordinary unit files. Including eight Worker files and one tooling file gives the reported 43. The scope arithmetic and membership were checked. Reading depth and the subject’s execution history were not directly observable from the sealed outputs.",
          "remaining_self_report": "The 490/36 expanded units, 12/12 verification-tooling, 84/8 Worker default and 131/11 Worker full after submission, and code-quality subcommand outcomes were not independently rerun for this record. The original prepared 84/8 and 131/11 Worker counts exist in baseline.json and the Worker code/tests are byte-identical. The response reports unavailable Playwright collection, ESLint and React/Node declarations. Those top-level dependencies are absent from the slim app runtime. The response’s wall times are subject observations. All independent run logs retain their own timings.",
          "unexecuted": "Full upstream CI on this patch, a real browser/mobile device, native audio, Darwin and real codec/browser verification. The historic hosted green audio step applies to pinned code. Claims about all-suite mutation detection or general UX precision fall outside the demonstrated controls."
        }
      }
    },
    {
      "id": "26b28c77f8288968",
      "disposition": "returned",
      "response_source": "submitted file",
      "raw_response": "# Keyboardia test audit\n\nAt `aa67598560f8eaf2509a3ad4bc73edee2f8bea8a`, I surveyed all 58 sampled paths across the nine strata of the 370-file inventory. All 58 base blob IDs matched. I inspected declarations, imports, assertions and execution gates, followed selected fixtures and production callers, and ran 42 sampled files locally. [File-by-file review and execution ledger](/workspace/test-audit-replay-v2/subjects/f5740f900f52bf30/work/evidence/survey.tsv)\n\n## Prioritized findings\n\n1. **The macOS visual job was cancelled before checkout.** CI run `45018066984` records zero steps and an unsupported runner configuration. The three Holby screenshots require Darwin, Chromium and the mock API. Linux visuals passed. Stack A Identity was skipped under its PR-only condition. See `work/ci-snapshot.json:1476`, `:1498`, `:1602`, `.github/workflows/ci.yml:166`, `:654` and `app/e2e/populated-visual.spec.ts:10`.\n2. **Repaired the rotating Worker persistence test.** Run `45182094013` passed rotating unit tests and preserved the integration failure. The seed reproduced locally. All 99 accepted commands satisfied the GET, KV and socket checks, but the workload minimum was 100. The repair draws successive schedules from each seed until it reaches that floor, observes both WebSocket write kinds and disconnects while KV lags. It allows up to one extra batch’s worth of cases, then reports any missing requirement. A diagnostic copy recorded 99 → 99 → 101 commands and four dirty disconnects. See `work/ci-snapshot.json:1669`, `:1813`, `:1879`, `.github/workflows/property-seed.yml:100` and the [repaired model](/workspace/test-audit-replay-v2/subjects/f5740f900f52bf30/work/repo/app/test/integration/state-machine-fuzz.test.ts:492).\n3. **Four recorder waveform tests pass with production peaks flattened to zero.** I ran `../runtime/run-unit.sh src/components/waveform-peaks.test.ts` against that fault. The four tests exercise a calculation defined inside the test. The recorder draws from a separate implementation with a per-buffer, per-width cache. See `app/src/components/waveform-peaks.test.ts:17`, `app/src/components/Waveform.tsx:53` and `app/src/components/Recorder.tsx:230`.\n\n## Existing tests worth retaining\n\n- Concurrent toggle tests derive all 32 grid cells from input parity, check sequence numbers on three real sockets and compare fresh snapshots with REST. Input parity catches a wrong grid shared by every client. See `app/test/integration/overlap-fuzz.test.ts:218`, `:254` and `:294`.\n- A client persistence test holds one save in flight and verifies the next request carries the later edit. A native audio test counts rendered onsets and checks them against an independent 125 ms per sixteenth at 120 BPM. The persistence test passed locally. The hosted native-render step passed. See `app/src/sync/session.persistence.test.ts:87`, `app/src/audio/session-render-conservation.render.test.ts:87` and `work/ci-snapshot.json:249`.\n\n## Verification\n\nCommands ran from `work/repo/`. Both seeded selections used `FC_SEED=45182094013 FUZZ_SEEDS=45182094013`.\n\n| Selection | Observed result |\n|---|---|\n| Base `../runtime/run-unit.sh` and `../runtime/run-worker.sh` | 343 passed in 23 files and 84 passed in eight |\n| `xargs -a ../evidence/unit-files.txt ../runtime/run-unit.sh` | 463 passed in 34 files |\n| `../runtime/run-worker.sh --all` | 131 passed in all 11 Worker files |\n| Seeded `../runtime/run-worker.sh state-machine-fuzz.test.ts -t 'model: read-your-writes'` | One failed before, one passed after, five filtered each time |\n| Seeded `../runtime/run-worker.sh state-machine-fuzz.test.ts overlap-fuzz.test.ts eviction-recovery.test.ts` | 28 passed in three files after repair |\n\nIn disposable copies, serving stale KV at `app/src/worker/live-session.ts:370` made both model versions shrink to one tempo write of 60. GET returned 120. The CLI in `app/scripts/promote-pbt-counterexamples.ts:80` saved the schedule and replay failed at known case 0. Removing the swing generator also failed the repaired model, with zero swing writes despite 247 accepted commands. Only the model test changed in the repository. `git diff --check` passed.\n\nOffline `npm run validate:test-quality` passed the antipattern, linkage and dead-export checks before Playwright collection stopped on the missing package. Worker `tsc -p tsconfig.json --noEmit` produced the same six configuration diagnostics on base and repair. Browser, native audio and full-suite conclusions rely on source and the supplied CI records. Raw results are in `work/evidence/`.\n",
      "patch": "diff --git a/app/test/integration/state-machine-fuzz.test.ts b/app/test/integration/state-machine-fuzz.test.ts\nindex cc19793..686144c 100644\n--- a/app/test/integration/state-machine-fuzz.test.ts\n+++ b/app/test/integration/state-machine-fuzz.test.ts\n@@ -489,25 +489,16 @@ async function replayKnownFailure(schedule: StateMachineOp[]): Promise<void> {\n   }\n }\n \n-function assertModelCoverage(coverage: ModelCoverage): void {\n-  const summary = JSON.stringify(coverage);\n-  expect(coverage.accepted, summary).toBeGreaterThanOrEqual(100);\n-  expect(coverage.byKind.ws_tempo, summary).toBeGreaterThan(0);\n-  expect(coverage.byKind.ws_swing, summary).toBeGreaterThan(0);\n-  expect(coverage.dirtyDisconnects, summary).toBeGreaterThan(0);\n+function missingModelCoverage(coverage: ModelCoverage) {\n+  return [\n+    { witness: 'accepted commands', observed: coverage.accepted, minimum: 100 },\n+    { witness: 'WS tempo writes', observed: coverage.byKind.ws_tempo, minimum: 1 },\n+    { witness: 'WS swing writes', observed: coverage.byKind.ws_swing, minimum: 1 },\n+    { witness: 'dirty disconnects', observed: coverage.dirtyDisconnects, minimum: 1 },\n+  ].filter(({ observed, minimum }) => !(observed >= minimum));\n }\n \n-it('model: read-your-writes through the DO holds across shrunk command sequences; KV converges at write/disconnect points', async () => {\n-  // Re-run promoted counterexamples before exploring generated schedules.\n-  for (const [index, schedule] of STATE_MACHINE_KNOWN_FAILURES.entries()) {\n-    try {\n-      await replayKnownFailure(schedule);\n-    } catch (error) {\n-      throw new Error(`known-failure #${index} regressed: ${(error as Error).message}`);\n-    }\n-  }\n-\n-  const coverage = createModelCoverage();\n+async function runModelBatch(coverage: ModelCoverage, startRun: number, numRuns: number): Promise<void> {\n   for (const seed of MODEL_SEEDS) {\n     const details = await fc.check(\n       fc.asyncProperty(fc.commands(commandArbs, { maxCommands: 18 }), async (commands) => {\n@@ -520,7 +511,9 @@ it('model: read-your-writes through the DO holds across shrunk command sequences\n       }),\n       {\n         seed: seed | 0,\n-        numRuns: RUNS_PER_SEED,\n+        // A single path segment starts at this case in the seed's unshrunk stream.\n+        path: String(startRun),\n+        numRuns,\n         interruptAfterTimeLimit: Math.max(\n           30_000,\n           Math.floor(MODEL_TIMEOUT_MS / MODEL_SEEDS.length) - 5_000,\n@@ -539,9 +532,26 @@ it('model: read-your-writes through the DO holds across shrunk command sequences\n       throw new Error(`stateMachine property interrupted before producing a counterexample (seed=${details.seed})`);\n     }\n   }\n+}\n+\n+it('model: read-your-writes through the DO holds across shrunk command sequences; KV converges at write/disconnect points', async () => {\n+  // Re-run promoted counterexamples before exploring generated schedules.\n+  for (const [index, schedule] of STATE_MACHINE_KNOWN_FAILURES.entries()) {\n+    try {\n+      await replayKnownFailure(schedule);\n+    } catch (error) {\n+      throw new Error(`known-failure #${index} regressed: ${(error as Error).message}`);\n+    }\n+  }\n \n-  // A total command count can hide a missing transition class. These witnesses\n-  // keep the fixed and rotating campaigns honest about the WS/KV lifecycle they\n-  // claim to cover.\n-  assertModelCoverage(coverage);\n+  const coverage = createModelCoverage();\n+  await runModelBatch(coverage, 0, RUNS_PER_SEED);\n+  // Short schedules and command preconditions can leave the campaign below\n+  // budget. Draw the next schedule from each seed only while witnesses are\n+  // missing, with at most one more batch's worth of cases.\n+  for (let extraRun = 0; extraRun < RUNS_PER_SEED; extraRun++) {\n+    if (missingModelCoverage(coverage).length === 0) break;\n+    await runModelBatch(coverage, RUNS_PER_SEED + extraRun, 1);\n+  }\n+  expect(missingModelCoverage(coverage), JSON.stringify(coverage)).toEqual([]);\n }, MODEL_TIMEOUT_MS);\n",
      "observed_behavior": {
        "role": "Independent technical verification for blind review.",
        "repository": "adewale/keyboardia",
        "upstream_commit": "aa67598560f8eaf2509a3ad4bc73edee2f8bea8a",
        "integrity": {
          "candidate_and_pristine_files": 985,
          "unique_changed_path": "app/test/integration/state-machine-fuzz.test.ts",
          "changed_model_sha256": "b68145253f7453b176fa77c62ce15dacf2be714add213dad8f50ea32f11c85c1",
          "base_model_sha256": "2e94b53a32fa518d9157611bc7133c020dd1d1091dddbd028ffef2bf7edb8516",
          "sampled_blob_ids_checked": 58,
          "sealed_sha256": {
            "response.md": "6616cbca3bec23d1bec1ae4ba769473bff84a9cf99e52af6b4c23133dd96f315",
            "patch.diff": "274998930e204ab35ec23e5ef31cbddade794879eac2977eb8a37e094f5cd09f"
          },
          "submitted_evidence_files_verified": 18,
          "submitted_artifact_earliest_mtime": "2026-11-27T01:58:00.100113+00:00",
          "submitted_artifact_latest_mtime": "2026-11-27T02:13:38.468440+00:00",
          "submitted_artifact_collection": "2026-11-27T02:19:03.999771+00:00",
          "controller_sealed_utc": "2026-11-27T02:17:51.412962+00:00",
          "all_frozen_evaluator_hashes_matched": true,
          "patch_applies_to_pristine_with_whitespace_error_check": true
        },
        "submitted_repair": "Change the existing registered Worker command-model test to continue drawing whole schedules from each allowed seed while its accepted-work or lifecycle requirements are missing. The one-file patch leaves the command generator, production owners, CI, five fixed examples and known-failure database byte-identical outside the changed end of the test file.",
        "verification_method": {
          "predeclared_target": "Prior audit finding keyboardia-02 and the frozen Worker-seed secondary matrix. The matched original and submitted commands used evaluator/evaluate-seed.py --assert-original or --assert-repaired with the shared pinned dependencies. All four submitted rows also ran separately through postcandidate.py --scenario seed in fresh offline Docker containers with 2 CPUs and 2 GiB. Exit 1 in a fault row is an assertion failure. Each title filter selected one actual test and filtered the file’s other five.",
          "supplemental": "Additional fault, representation, seed and trace checks are explicitly EXPLORATORY. They used independent disposable trees, real Node 24.22.3, Vitest 4.1.11, workerd 1.20261006.1 and Worker fast-check 4.9.0. Their shared-host transport differs from the independent offline Docker repeat. All Docker calls acquired the shared lock.",
          "evidence_sources": [
            "technical-check/plan.json",
            "technical-check/frozen.py",
            "technical-check/probes.py",
            "submitted-artifacts/evidence-collection.json"
          ]
        },
        "frozen_seed_matrix": [
          {
            "case": "default_model",
            "meaning": "Clean default seed list and real generated model.",
            "ground_truth": "accept",
            "original": {
              "exit": 0,
              "log": "technical-check/frozen-native-original/raw/default_model.log",
              "sha256": "bdef2664b924ae9a74a8237789a3d989c78395626465974f7101c750827d4f61",
              "files": "1 passed (1)",
              "tests": "1 passed | 5 skipped (6)",
              "vitest_duration": "7.28s"
            },
            "submitted": {
              "exit": 0,
              "log": "technical-check/frozen-native-candidate/raw/default_model.log",
              "sha256": "fcf696f9b660335919011695f0467e1327ca1a4ea871d407a8de694e1385a142",
              "files": "1 passed (1)",
              "tests": "1 passed | 5 skipped (6)",
              "vitest_duration": "6.46s"
            },
            "submitted_offline_repeat": {
              "exit": 0,
              "log": "technical-check/frozen-offline-candidate/default_model/raw/default_model.log",
              "sha256": "2a4ff344a062f0da2b6ca9209c2f9bf4bc1991f3b033385241e751d0335d1641",
              "files": "1 passed (1)",
              "tests": "1 passed | 5 skipped (6)",
              "vitest_duration": "5.50s"
            }
          },
          {
            "case": "valid_schedule",
            "meaning": "Accepted historical schedule, with both fast-check bindings set to 45182094013.",
            "ground_truth": "accept",
            "original": {
              "exit": 1,
              "log": "technical-check/frozen-native-original/raw/valid_schedule.log",
              "sha256": "c65fc1fe1045e66d42820bbe06c0b6f3ec7de5766f3f79b82de016c6c50feb30",
              "files": "1 failed (1)",
              "tests": "1 failed | 5 skipped (6)",
              "vitest_duration": "5.26s"
            },
            "submitted": {
              "exit": 0,
              "log": "technical-check/frozen-native-candidate/raw/valid_schedule.log",
              "sha256": "fa5cee11b16d2db8222ded16c39f9d69742908988c7d5a29bc565282949b4f1c",
              "files": "1 passed (1)",
              "tests": "1 passed | 5 skipped (6)",
              "vitest_duration": "5.80s"
            },
            "submitted_offline_repeat": {
              "exit": 0,
              "log": "technical-check/frozen-offline-candidate/valid_schedule/raw/valid_schedule.log",
              "sha256": "2bf235e5309b62f3b27906bf9c7a07f7e8eb38d8a37c33037b8645c2b66dd562",
              "files": "1 passed (1)",
              "tests": "1 passed | 5 skipped (6)",
              "vitest_duration": "4.86s"
            }
          },
          {
            "case": "persistence_original",
            "meaning": "Existing explicit WebSocket, GET and KV lifecycle example on clean production.",
            "ground_truth": "accept",
            "original": {
              "exit": 0,
              "log": "technical-check/frozen-native-original/raw/persistence_original.log",
              "sha256": "a324ea69d50d5b6739907005d21d503e86b523ba5408a97c90a32ba4c76e4642",
              "files": "1 passed (1)",
              "tests": "1 passed | 5 skipped (6)",
              "vitest_duration": "3.78s"
            },
            "submitted": {
              "exit": 0,
              "log": "technical-check/frozen-native-candidate/raw/persistence_original.log",
              "sha256": "c3faa62b8cc2b8f04d2a102b32b783199b135514abad08fde6c4ac6108cec0f4",
              "files": "1 passed (1)",
              "tests": "1 passed | 5 skipped (6)",
              "vitest_duration": "3.82s"
            },
            "submitted_offline_repeat": {
              "exit": 0,
              "log": "technical-check/frozen-offline-candidate/persistence_original/raw/persistence_original.log",
              "sha256": "61aaea57f7174e2987ac85a50a596362366be13e6822b3ae48f32eace946e585",
              "files": "1 passed (1)",
              "tests": "1 passed | 5 skipped (6)",
              "vitest_duration": "4.21s"
            }
          },
          {
            "case": "persistence_fault",
            "meaning": "Remove exactly the final save inside flushPendingKVSave. Run the same existing lifecycle example.",
            "ground_truth": "reject",
            "original": {
              "exit": 1,
              "log": "technical-check/frozen-native-original/raw/persistence_fault.log",
              "sha256": "3b3820d181ca4e9ef631777f9203ea3d1eb2d71a391afe865ea96e5808d7ba39",
              "files": "1 failed (1)",
              "tests": "1 failed | 5 skipped (6)",
              "vitest_duration": "5.79s"
            },
            "submitted": {
              "exit": 1,
              "log": "technical-check/frozen-native-candidate/raw/persistence_fault.log",
              "sha256": "d4e07cb7761acf8bcebd6a176765af7497cd3fddbd01cb8bd2cc784adf1e7e6e",
              "files": "1 failed (1)",
              "tests": "1 failed | 5 skipped (6)",
              "vitest_duration": "6.91s"
            },
            "submitted_offline_repeat": {
              "exit": 1,
              "log": "technical-check/frozen-offline-candidate/persistence_fault/raw/persistence_fault.log",
              "sha256": "c8456249249d15015823870ae22bbcc778794d69c4d2469de558df3bfe009a69",
              "files": "1 failed (1)",
              "tests": "1 failed | 5 skipped (6)",
              "vitest_duration": "5.95s"
            }
          }
        ],
        "historical_seed": {
          "seed": 45182094013,
          "signed_fast_check_seed": -2062546243,
          "baseline_actual_coverage": {
            "accepted": 99,
            "dirtyDisconnects": 3,
            "byKind": {
              "ws_tempo": 10,
              "ws_swing": 13,
              "rest_put": 9,
              "rest_patch_state": 11,
              "rest_patch_name": 14,
              "hibernate": 17,
              "hard_evict": 11,
              "disconnect": 8,
              "connect": 6
            }
          },
          "failure_cause": "The original run completed its generated properties, then failed only the 100-accepted-command floor at state-machine-fuzz.test.ts:494. The post-repair row is the same registered model and same seed. The original archived rotating-unit job passed. The hosted Worker job uploaded its diagnostic before its failure-preservation step returned red.",
          "hosted_worker_receipt": "https://github.com/adewale/keyboardia/actions/runs/45182094013/job/137718195578"
        },
        "extension_evidence": {
          "logic": "Let S be the number of supplied seeds and R = ceil(30 / S). Each seed first runs R schedules. If any shared witness is deficient, each seed draws one more schedule at offset R + extraRun. There are at most R such rounds. A batch finishes for every seed before coverage is checked again. The maximum is 2 × S × R scheduled cases before shrink/replay, and the normal 11 unique default seeds give 33 initial and at most 66 cases. This historical single-seed configuration starts at 30 and caps at 60. Each schedule allows up to 18 generated commands with preconditions.",
          "witnesses": "At least 100 accepted commands, at least one acknowledged WebSocket tempo write, one WebSocket swing write, and one disconnect while the model’s live and KV state differ. An accepted action calls the real owner and compares expected state through REST, KV and socket observations. A property failure is handled immediately before any coverage top-up. The other seven command kinds are generated but each is not independently required by the final predicate.",
          "same_stream": "The fixed package implements a single numeric fast-check path by dropping that many initial producers from the same seed’s generator stream. It honors numRuns when that path has no shrink segment. The repair uses the original signed seed and increasing case offsets. In a disposable diagnostic we recorded all accepted action objects and cumulative coverage after each successful real model schedule. All 32 records were byte-identical to one uninterrupted 32-case run of the original generator with the same seed.",
          "trace_support": {
            "length": 32,
            "accepted_action_count": 101,
            "trace_sha256": "4f1bfa6045b8da27c0219f55f9516a441a16f0851c617a749cfdb3e067b7b68e",
            "submitted_trace": "technical-check/exploratory/candidate_trace_capture/schedule-trace.json",
            "uninterrupted_reference_trace": "technical-check/exploratory/continuous_32_capture/schedule-trace.json",
            "after_case_30": {
              "accepted": 99,
              "dirty_disconnects": 3
            },
            "case_31": {
              "actions": [],
              "accepted": 99,
              "dirty": 3,
              "byKind": {
                "ws_tempo": 10,
                "ws_swing": 13,
                "rest_put": 9,
                "rest_patch_state": 11,
                "rest_patch_name": 14,
                "hibernate": 17,
                "hard_evict": 11,
                "disconnect": 8,
                "connect": 6
              }
            },
            "case_32": {
              "actions": [
                {
                  "kind": "ws_swing",
                  "swing": 50
                },
                {
                  "kind": "disconnect"
                }
              ],
              "accepted": 101,
              "dirty": 4,
              "byKind": {
                "ws_tempo": 10,
                "ws_swing": 14,
                "rest_put": 9,
                "rest_patch_state": 11,
                "rest_patch_name": 14,
                "hibernate": 17,
                "hard_evict": 11,
                "disconnect": 9,
                "connect": 6
              }
            }
          },
          "cost": "For this seed the repair executed two extra schedules. Case 31 had no accepted action. Case 32 sent swing 50 and disconnected, raising 99 to 101 and three dirty closes to four. The uninstrumented paired local Vitest process times and isolated repeats are in the matrix. Each extra fc.check reinitializes a runner and advances to an offset. The outer test timeout is unchanged at max(120000, 15000 × S) ms. interruptAfterTimeLimit is per fc.check, including each extra call. No suite-wide runtime multiplier or all-seed success rate was measured.",
          "diagnostic_attempts": {
            "first_passing_runs_with_no_emitted_trace": {
              "candidate_trace": {
                "exit": 0,
                "log": "technical-check/exploratory/candidate_trace/run.log",
                "sha256": "97e3ec81d4c493b4a31b80f43ad8590c8fd8b2f431bfb49adaf64f4301ac1b43",
                "files": "1 passed (1)",
                "tests": "1 passed | 5 skipped (6)",
                "vitest_duration": "4.53s"
              },
              "continuous_32_reference": {
                "exit": 0,
                "log": "technical-check/exploratory/continuous_32_reference/run.log",
                "sha256": "896a7522b8dcfbf39a50ab221a07b9bc76d65cc9c5a3e7b30254f27201bb388b",
                "files": "1 passed (1)",
                "tests": "1 passed | 5 skipped (6)",
                "vitest_duration": "4.48s"
              }
            },
            "reason": "The first successful runs emitted no console.log records. Their empty traces give no stream comparison. The retained follow-ups accumulated records, ran the original coverage assertion and then deliberately raised a diagnostic error to deliver the trace. The added diagnostic exit supplies observations only. The frozen uninstrumented runs establish pass/fail.",
            "submitted_capture": {
              "exit": 1,
              "log": "technical-check/exploratory/candidate_trace_capture/run.log",
              "sha256": "fc6b4ddd7ad72e203a63479114d51805f7ffcd649815c3abc222be5d9efb2bc2",
              "files": "1 failed (1)",
              "tests": "1 failed | 5 skipped (6)",
              "vitest_duration": "5.13s"
            },
            "reference_capture": {
              "exit": 1,
              "log": "technical-check/exploratory/continuous_32_capture/run.log",
              "sha256": "d7827eee88e5a18e34ce43649ce34968e5b6b87ac3b8da0077ba88da78f3b13b",
              "files": "1 failed (1)",
              "tests": "1 failed | 5 skipped (6)",
              "vitest_duration": "5.97s"
            }
          },
          "sources": [
            "app/test/integration/state-machine-fuzz.test.ts:315,346,391,412,445,455,492,501,524,537,547",
            "Worker fast-check 4.9.0 lib/fast-check.js:2327,2532"
          ]
        },
        "exploratory_checks": {
          "stale_get": {
            "classification": "Additional submitted fault, independently reconstructed on original and submitted model. Existing regression detection is retained.",
            "change": "Serve the stale KV state instead of the active Durable Object state in the real Worker GET merge. Both versions shrink to one WebSocket tempo write of 60. The acknowledgement arrives and the following GET observes the original 120. Both matrices fail before the coverage check.",
            "original": {
              "exit": 1,
              "log": "technical-check/exploratory/stale_original/run.log",
              "sha256": "e3a58c9c87b3bd0d1f29635fdaef697d87261478b9512e6670175ee0b31becbc",
              "files": "1 failed (1)",
              "tests": "1 failed | 5 skipped (6)",
              "vitest_duration": "4.54s"
            },
            "submitted": {
              "exit": 1,
              "log": "technical-check/exploratory/stale_candidate/run.log",
              "sha256": "26b56a888f67271180b9e5c45546de24ba2e2472b528dc914e11f60b8bb3d079",
              "files": "1 failed (1)",
              "tests": "1 failed | 5 skipped (6)",
              "vitest_duration": "3.28s"
            },
            "shrunk_record": {
              "lane": "stateMachine",
              "example": [
                {
                  "kind": "ws_tempo",
                  "tempo": 60
                }
              ],
              "seed": -2062546243,
              "path": "0:1",
              "shrinks": 1
            },
            "same_modified_owner_bytes": true
          },
          "promotion_and_replay": {
            "classification": "Existing real counterexample CLI and registered replay loop.",
            "result": "The actual promote-pbt-counterexamples.ts CLI consumed the independently produced failure log and added the shrunk schedule to the otherwise empty stateMachine array. Known case 0 failed before exploration with 120 where 60 was required while the stale GET remained. The same promoted schedule passed with correct production restored.",
            "CLI": {
              "exit": 0,
              "log": "technical-check/exploratory/stale_candidate/promotion.log",
              "sha256": "612d03d494fd2cc79d9b2dc46402681669dc800d2345f3db6c698d3b76393bba"
            },
            "promoted_database": "technical-check/exploratory/stale_candidate/promoted-known-failures.json",
            "faulty_known_replay": {
              "exit": 1,
              "log": "technical-check/exploratory/stale_candidate/known-replay.log",
              "sha256": "8bed1043014b4e092291a96c77e27d0db1db81d5d5371fbd04a3d67a4a2130f9",
              "files": "1 failed (1)",
              "tests": "1 failed | 5 skipped (6)",
              "vitest_duration": "3.09s"
            },
            "restored_production": {
              "exit": 0,
              "log": "technical-check/exploratory/promoted_clean_control/run.log",
              "sha256": "af6e6f88d5a54b8df93178dd469076ecb5447e485991559446bf2d8f56a341e8",
              "files": "1 passed (1)",
              "tests": "1 passed | 5 skipped (6)",
              "vitest_duration": "5.37s"
            }
          },
          "flush_fault_actual_generated_model": {
            "classification": "Unchanged frozen missing-final-save stimulus, with an EXPLORATORY selection of the registered generated model as observer.",
            "original": {
              "exit": 1,
              "log": "technical-check/exploratory/final_flush_model_original/run.log",
              "sha256": "7a6f6787be4840ff630da2a9338eb5da27e79f6442f685e84456059987b1a617",
              "files": "1 failed (1)",
              "tests": "1 failed | 5 skipped (6)",
              "vitest_duration": "9.47s"
            },
            "submitted": {
              "exit": 1,
              "log": "technical-check/exploratory/final_flush_model_candidate/run.log",
              "sha256": "5a138370f2e17c7421d4dddc6b5f897ec5f07a8560416bacdc3ce1f19e19a93e",
              "files": "1 failed (1)",
              "tests": "1 failed | 5 skipped (6)",
              "vitest_duration": "9.66s"
            },
            "shrunk_record": {
              "lane": "stateMachine",
              "example": [
                {
                  "kind": "ws_tempo",
                  "tempo": 60
                },
                {
                  "kind": "disconnect"
                }
              ],
              "seed": -2062546243,
              "path": "0:2",
              "shrinks": 1
            },
            "same_modified_owner_bytes": true,
            "result": "Both reach the same failing generated schedule, a tempo write to 60 followed by disconnect. The KV observation stays 120. This is distinct from the fixed frozen 150 example and demonstrates preservation of an existing sensitivity."
          },
          "missing_swing_generator": {
            "classification": "EXPLORATORY damaged workload generator.",
            "submitted": {
              "exit": 1,
              "log": "technical-check/exploratory/missing_swing/run.log",
              "sha256": "5e3eebcc7f0d0abc945d8d5e7536de363b0530a5bcd74d823acfd2c16c8e3e85",
              "files": "1 failed (1)",
              "tests": "1 failed | 5 skipped (6)",
              "vitest_duration": "6.08s"
            },
            "coverage": {
              "accepted": 247,
              "dirtyDisconnects": 4,
              "byKind": {
                "ws_tempo": 21,
                "ws_swing": 0,
                "rest_put": 46,
                "rest_patch_state": 37,
                "rest_patch_name": 33,
                "hibernate": 31,
                "hard_evict": 28,
                "disconnect": 29,
                "connect": 22
              }
            },
            "result": "Deleting only the WebSocket swing generator still fails after the capped extension. The native assertion reports the missing WS swing witness (observed 0, minimum 1), even after 247 accepted actions and four dirty disconnects. The original model already required this witness."
          },
          "different_allowed_seed": {
            "seed": 20261127,
            "original": {
              "exit": 0,
              "log": "technical-check/exploratory/other_seed_original/run.log",
              "sha256": "71622828083f387ae809bce8fe2fec168674979e9110cda58604aa1839e3b124",
              "files": "1 passed (1)",
              "tests": "1 passed | 5 skipped (6)",
              "vitest_duration": "4.58s"
            },
            "submitted": {
              "exit": 0,
              "log": "technical-check/exploratory/other_seed_candidate/run.log",
              "sha256": "ab73f2f151466d0cbe19a0fdbc5b07d9fb277b4150302bed8cf4b9b21e8a64bb",
              "files": "1 passed (1)",
              "tests": "1 passed | 5 skipped (6)",
              "vitest_duration": "4.89s"
            },
            "result": "Both registered models passed the separately selected valid seed with both seed bindings set."
          },
          "equivalent_get_representation": {
            "submitted": {
              "exit": 0,
              "log": "technical-check/exploratory/private_get_representation/run.log",
              "sha256": "5b3541f09d0d8cf760b35128d8d4d8f3ce66bf67d3877db4632b2e7ac4f6996f",
              "files": "1 passed (1)",
              "tests": "1 passed | 5 skipped (6)",
              "vitest_duration": "5.74s"
            },
            "result": "The submitted model accepted a private Object.assign construction producing the same plain response as the previous object spread, retaining KV metadata and authoritative DO state, on 45182094013."
          }
        },
        "registration_and_retained_checks": {
          "ordinary_ci": {
            "observed": {
              "exit": 0,
              "log": "technical-check/ci-worker-full/raw/original.log",
              "sha256": "3d0757c7d3fda2578ccf7f9a01b71f32364982553ee576def1cd348c3db63942",
              "files": "11 passed (11)",
              "tests": "131 passed (131)",
              "vitest_duration": "14.74s"
            },
            "files": [
              "agent-skills-journey.test.ts",
              "collaboration-contract.test.ts",
              "eviction-recovery.test.ts",
              "live-session.test.ts",
              "mcp-journeys.test.ts",
              "overlap-fuzz.test.ts",
              "seq-regression.test.ts",
              "social-preview.test.ts",
              "state-hash-parity.test.ts",
              "state-machine-fuzz.test.ts",
              "validator-enforcement.test.ts"
            ],
            "scope": "The complete ordinary Worker test entry ran npm test (vitest run, no file/title filters) in app/test/integration under isolated Docker. It collected all 11 Worker files, all six state-machine identities and 131 passes. The pinned CI builds first, installs Worker dependencies, then calls test:integration:built, which delegates here. The prepared runner supplied the two small static assets and HTML. A complete application build or hosted patch run is outside this observation.",
            "sources": [
              ".github/workflows/ci.yml:241-255",
              "app/package.json:23-24",
              "app/test/integration/package.json:6",
              "app/test/integration/vitest.config.ts:21-50"
            ]
          },
          "rotating_ci": {
            "observed": {
              "exit": 0,
              "log": "technical-check/exploratory/weekly_selection/run.log",
              "sha256": "a023aa12eefafdf226bedb441d159c574b0eaaff1c01e57084b775c5671c351f",
              "files": "3 passed (3)",
              "tests": "28 passed (28)",
              "vitest_duration": "6.47s"
            },
            "scope": "Exact three registered files with both replay seed variables, all 28 passed. The registered modified model, five fixed examples, eviction/recovery and three-socket overlap checks ran. The eight other integration files outside the weekly selector were covered by the separate unfiltered run.",
            "source": ".github/workflows/property-seed.yml:97-137"
          },
          "fixed_state_machine_examples": [
            "WS mutation makes KV lag, GET stays authoritative, disconnect converges KV",
            "REST PUT then WS mutation: DO storage and GET reflect the WS write (last-writer-wins)",
            "WS mutation -> hibernate -> REST PUT -> GET reflects the REST write",
            "PATCH name (KV-only) composes with WS state (DO-only) in the GET merge",
            "multi-client: KV flushes only when the LAST client disconnects"
          ],
          "keepers": [
            {
              "area": "Worker state and acknowledgments",
              "evidence": "The fixed example creates tempo 120, sends 150 over a WebSocket and requires its acknowledgement, GET at 150 and KV still at 120, followed by KV at 150 after the disconnect. Stateful commands compare real GET name/tempo/swing, direct KV values and socket readyState to the independent expected model. Checks and update logic are unchanged.",
              "sources": [
                "app/test/integration/state-machine-fuzz.test.ts:162,315,346,391,412"
              ]
            },
            {
              "area": "Peer state and convergence",
              "evidence": "The unchanged overlap test starts all 32 expected cells from fixture inputs, toggles by sent parity, checks every sequence number on each of three sockets and reconciles snapshots and the REST GET. The native three-file and full Worker runs passed it. The single-client generated model itself makes a narrower delivery observation.",
              "sources": [
                "app/test/integration/overlap-fuzz.test.ts:218,254,277,303"
              ]
            },
            {
              "area": "Client save destination and in-flight edit",
              "observed": {
                "exit": 0,
                "log": "technical-check/exploratory/client_persistence_keeper/run.log",
                "sha256": "eb1fa55fd0dc5cc5790dbb177e4c08bbdc0514b7cb4cbc1d700a38b57c0c9b4f",
                "files": "1 passed (1)",
                "tests": "7 passed (7)",
                "vitest_duration": "396ms"
              },
              "evidence": "The test records outgoing requests with a fetch double. The unchanged client test leaves the first save pending, releases its response and checks that the next outbound payload carries tempo 200.",
              "source": "app/src/sync/session.persistence.test.ts:87-105"
            },
            {
              "area": "Audio timing",
              "evidence": "The source counts PCM onsets and compares timing against step × 0.125 seconds at 120 BPM with a 0.010-second tolerance. The required native-render step passed in the pinned hosted Unit Tests receipt. This verification performed no native audio render.",
              "sources": [
                "app/src/audio/session-render-conservation.render.test.ts:87-100",
                "https://github.com/adewale/keyboardia/actions/runs/45018066984/job/137194593412"
              ]
            }
          ]
        },
        "other_reported_findings": [
          {
            "finding": "Historical macOS visual cancellation",
            "historical_status": "Prior finding keyboardia-01, reported as open.",
            "evidence_kind": "Archived hosted receipt and source.",
            "run": 45018066984,
            "mac_conclusion": "cancelled",
            "steps": 0,
            "annotation": "The configuration 'macos-14-arm64-us-default' is not supported",
            "source_contract": "The workflow requests macos-14 and Chromium, sets the mock API and calls populated-visual.spec.ts. The spec requires Darwin. The lane expects three named Holby results and zero skips.",
            "cases": [
              "chromium :: populated-visual.spec.ts › Deterministic populated-session visuals › Holby landscape editing view",
              "chromium :: populated-visual.spec.ts › Deterministic populated-session visuals › Holby pitch overview exposes correctly named octaves",
              "chromium :: populated-visual.spec.ts › Deterministic populated-session visuals › Holby portrait consumption view"
            ],
            "linux_visual": "success",
            "stack_a_identity": "skipped",
            "identity_gate": "pull_request with audio or full verification scope, .github/workflows/ci.yml:166",
            "sources": [
              "https://github.com/adewale/keyboardia/actions/runs/45018066984/job/137194667192",
              "https://github.com/adewale/keyboardia/actions/runs/45018066984/job/137194667189",
              "https://github.com/adewale/keyboardia/actions/runs/45018066984/job/137194668367",
              "app/e2e/populated-visual.spec.ts:10",
              ".github/workflows/ci.yml:649-681",
              "app/e2e/lane-contracts.json:12"
            ]
          },
          {
            "finding": "Recorder waveform tests accept flat production peaks",
            "historical_status": "Additional relative to the designated prior audit’s four reported findings and frozen controls. This sampled file is outside the purposeful anchor list. The submission reports an open finding. No global novelty claim follows.",
            "evidence_kind": "EXPLORATORY independent native case pair on the candidate tree.",
            "change": "Only the production Waveform.tsx assignments to mins[i] and maxs[i] are replaced by zeros. Recorder supplies the recorded buffer to Waveform, which draws from its production function and per-buffer/per-width cache. The four ordinary tests define a local function, import only Vitest, and never reach the production function or its WeakMap. All four pass on clean and flattened production. This establishes insensitivity of these four tests. Browser canvas output and the rest of the suite were not evaluated on this fault.",
            "native": {
              "waveform_clean": {
                "exit": 0,
                "log": "technical-check/exploratory/waveform_clean/run.log",
                "sha256": "95de2ef59e70a620f5a7020cd59e9d3a131787b58c40129ddf0ad9dcf840f3e6",
                "files": "1 passed (1)",
                "tests": "4 passed (4)",
                "vitest_duration": "259ms"
              },
              "waveform_flat": {
                "exit": 0,
                "log": "technical-check/exploratory/waveform_flat/run.log",
                "sha256": "67f4cf0fcb4c851f98c519883cb8b94bc74098a4c2fe89d373343bc8bbbb282e",
                "files": "1 passed (1)",
                "tests": "4 passed (4)",
                "vitest_duration": "251ms"
              }
            },
            "sources": [
              "app/src/components/waveform-peaks.test.ts:9-39",
              "app/src/components/Waveform.tsx:29,53,99,106",
              "app/src/components/Recorder.tsx:230"
            ]
          }
        ],
        "submitted_evidence_and_scope": {
          "packet": "18 supplied attachments verified against the controller collection manifest. All recorded original mtimes precede the seal. These include 16 logs, one unit-file list and a 58-row survey. Submitted logs and independent post-candidate observations have separate provenance.",
          "survey": "The ledger matches all 58 frozen sampled paths and strata out of 370 conventional original test files. It marks 34 sampled unit files and eight sampled Worker files as run, and 16 source-only. It characterizes five full reads, 22 focused excerpts and 31 declaration/import/matcher/gate scans. The path and selection arithmetic are verifiable. The depth of each reading is self-described.",
          "submitted_log_counts": {
            "pinned-unit": "343 passed (343)",
            "pinned-worker": "84 passed (84)",
            "survey-units": "463 passed (463)",
            "all-workers": "131 passed (131)",
            "seed-before": "1 failed | 5 skipped (6)",
            "seed-after": "1 passed | 5 skipped (6)",
            "seed-three-files": "28 passed (28)",
            "stale-before": "1 failed | 5 skipped (6)",
            "stale-after": "1 failed | 5 skipped (6)",
            "known-replay": "1 failed | 5 skipped (6)",
            "no-swing": "1 failed | 5 skipped (6)",
            "waveform-control": "4 passed (4)",
            "workload-diagnostic": "1 failed | 5 skipped (6)"
          },
          "reported_obstacles": {
            "typecheck": "The supplied baseline and candidate Worker tsc logs are byte-identical, with six configuration diagnostics. This verification did not independently rerun tsc.",
            "tsc_sha256": "73238eb62c8a83d875d8ee7f9a738d8aa855713f423e7c90beeda4fe49c022a9",
            "quality": "The supplied log reaches successful antipattern, linkage and dead-export checks, then its npx playwright test --list fails with ENOTCACHED in the slim offline setup. This is separate from the successful actual full Worker collector run.",
            "quality_log": "submitted-artifacts/evidence/test-quality.log"
          },
          "scope": "The data support a repair to the registered Worker property-test workload, alongside inherited detection and replay. A valid run can still fail if it does not meet the four mandatory witnesses within the cap or exceeds the unchanged outer deadline. Exact performance across arbitrary seeds, full hosted CI, browser behavior, native audio and Darwin were not independently exercised. No production application change was submitted."
        },
        "other_frozen_reference_results": {
          "provenance": "Unchanged pre-submission calibration. The participant’s patch targets the frozen Worker seed secondary matrix, not the named sync or discovery contracts. These numerical exits are earlier observations, without a new detection attributed to this submission.",
          "sync": {
            "original": {
              "named_gate": 0,
              "existing_worker": 0,
              "worker_witness": 0,
              "existing_senders": 0,
              "hook_witness": 0
            },
            "private_rename": {
              "named_gate": 1,
              "existing_worker": 0,
              "worker_witness": 0
            },
            "no_dispatch": {
              "named_gate": 0,
              "existing_worker": 1,
              "worker_witness": 1
            },
            "author_only": {
              "named_gate": 0,
              "existing_worker": 0,
              "worker_witness": 1
            },
            "inverted_hook": {
              "named_gate": 0,
              "existing_senders": 0,
              "hook_witness": 1
            },
            "early_return": {
              "named_gate": 0,
              "existing_senders": 0,
              "hook_witness": 0
            },
            "stale_hook": {
              "named_gate": 0,
              "existing_senders": 0,
              "hook_witness": 1
            }
          },
          "discovery": {
            "correct": 0,
            "reordered_tools": 0,
            "missing_post_read": 0,
            "edit_before_both_reads": 0,
            "no_read": 1,
            "wrong_protocol": 1
          },
          "sources": [
            "preparation/keyboardia/evidence/final-sync-controls/results.json",
            "preparation/keyboardia/evidence/grader-controls.json",
            "preparation/keyboardia/evaluator/hidden-controls.md"
          ]
        }
      }
    },
    {
      "id": "125db40317156c7c",
      "disposition": "infrastructure-interrupted",
      "patch": "",
      "observed_behavior": {
        "disposition": "infrastructure-interrupted",
        "response": "unavailable",
        "patch": "no tracked or new source changes at interruption snapshot",
        "repair_verification": "unavailable",
        "preservation": "no submitted change to assess; not a completed audit",
        "environment_event": "controller/environment-event.json",
        "limits": [
          "Trial lost its agent state before its 25-minute allowance expired. No replacement model was run."
        ]
      }
    },
    {
      "id": "1274240f8d0c06e7",
      "disposition": "report-delivered-agent-status-unavailable",
      "response_source": "submitted file",
      "raw_response": "# Keyboardia test-suite audit\n\n**The rotating Worker run failed one command short of its coverage requirement.** At `aa67598560f8eaf2509a3ad4bc73edee2f8bea8a`, CI seed `45182094013` executed 99 commands, including three disconnects with unflushed edits. Every state comparison it reached passed. Local replay reproduced the CI annotation exactly. The workflow allowed the test step to continue for counterexample collection, then recorded the job failure. [CI annotation](/workspace/test-audit-replay-v2/subjects/81ed009d77b57e5c/work/ci-snapshot.json:1879) · [Workflow](/workspace/test-audit-replay-v2/subjects/81ed009d77b57e5c/work/repo/.github/workflows/property-seed.yml:100)\n\nI changed `app/test/integration/state-machine-fuzz.test.ts`. After a successful batch it continues at each seed’s next fast-check example until it has executed at least 100 commands, all nine action types and a disconnect with unflushed edits. It prints the observed counts and stops after at most three batches. A state mismatch still goes straight to shrinking. The recorded seed passed after 60 schedules, 234 commands and six such disconnects. The default seeds passed in their first batch. [Coverage requirement](/workspace/test-audit-replay-v2/subjects/81ed009d77b57e5c/work/repo/app/test/integration/state-machine-fuzz.test.ts:494) · [Continuation](/workspace/test-audit-replay-v2/subjects/81ed009d77b57e5c/work/repo/app/test/integration/state-machine-fuzz.test.ts:548)\n\n**Fault controls**\n\n- Removing hibernation from the generator left the original fixed-seed model green. The repaired model failed with 393 executed commands, six dirty disconnects and zero hibernations. [Control result](/workspace/test-audit-replay-v2/subjects/81ed009d77b57e5c/work/control-hibernate-after.log:22)\n- Temporarily capping REST PATCH swing at 99 exposed a fault in the second batch. Fast-check shrank it to one PATCH with tempo 60 and swing 100, at path `51:1`. The project’s promotion tool saved that example, and it failed again under seed 42 before random exploration. I restored the Worker and example database. [Worker PATCH](/workspace/test-audit-replay-v2/subjects/81ed009d77b57e5c/work/repo/app/src/worker/live-session.ts:559) · [Shrunk case](/workspace/test-audit-replay-v2/subjects/81ed009d77b57e5c/work/control-patch-swing.log:19) · [Replay](/workspace/test-audit-replay-v2/subjects/81ed009d77b57e5c/work/control-promoted-replay.log:16)\n\n**Other maintainer findings**\n\n1. The highest-impact behavior I observed is reconnect churn after sequence rewind. The real Durable Object reissued sequence 1 on the surviving socket after eviction. A separate test drove the production client with a controlled socket. It applied a regressed-epoch edit and opened a third connection after a second group of eleven regressed frames. [Worker](/workspace/test-audit-replay-v2/subjects/81ed009d77b57e5c/work/repo/app/test/integration/seq-regression.test.ts:133) · [Client](/workspace/test-audit-replay-v2/subjects/81ed009d77b57e5c/work/repo/app/src/sync/seq-regression.test.ts:168)\n2. The collaboration test compares two sockets’ acknowledgments and sequence order, then reads the three touched cells back over REST. The eviction test exercises WebSocket-only wake and reads both edits back after a second eviction. The client save test holds a fetch open and observes the two saved tempos in order. In the audio-render source, onset count and timing are checked against a literal 125 ms step at 120 BPM. [Collaboration](/workspace/test-audit-replay-v2/subjects/81ed009d77b57e5c/work/repo/app/test/integration/collaboration-contract.test.ts:224) · [Recovery](/workspace/test-audit-replay-v2/subjects/81ed009d77b57e5c/work/repo/app/test/integration/eviction-recovery.test.ts:727) · [Client saves](/workspace/test-audit-replay-v2/subjects/81ed009d77b57e5c/work/repo/app/src/sync/session.persistence.test.ts:109) · [Audio](/workspace/test-audit-replay-v2/subjects/81ed009d77b57e5c/work/repo/app/src/audio/session-render-conservation.render.test.ts:89)\n3. Waveform peak caching has a test disconnected from its caller. Forcing production `computePeaks` to throw still left all four waveform tests green. They call a test-local implementation. [Test](/workspace/test-audit-replay-v2/subjects/81ed009d77b57e5c/work/repo/app/src/components/waveform-peaks.test.ts:17) · [Canvas caller](/workspace/test-audit-replay-v2/subjects/81ed009d77b57e5c/work/repo/app/src/components/Waveform.tsx:100)\n\n**Execution and limits.** I surveyed definitions and assertions in all 58 sample paths across nine strata and verified their base blobs against the inventory of 370. Of those 58 files, 42 ran locally. From `repo/`, `../runtime/run-unit.sh` passed 343 tests in 23 files, eleven additional sampled unit files passed 120, and the neighboring client sequence file passed three. `../runtime/run-worker.sh` passed 84 in eight files and `../runtime/run-worker.sh --all` passed 131 in eleven. The rotating selection below went from 27 passed and one failed to 28 passed. [Sample paths](/workspace/test-audit-replay-v2/subjects/81ed009d77b57e5c/work/sample.tsv) · [Exact commands, selections and logs](/workspace/test-audit-replay-v2/subjects/81ed009d77b57e5c/work/audit-runs.tsv)\n\n```sh\nFC_SEED=45182094013 FUZZ_SEEDS=45182094013 ../runtime/run-worker.sh \\\n  state-machine-fuzz.test.ts overlap-fuzz.test.ts eviction-recovery.test.ts --reporter=verbose\n```\n\nMain CI recorded 15 successful jobs. The macOS visual job was cancelled before execution because its runner configuration was unsupported, and Stack A Identity was skipped. Rotating unit CI passed. Local browser, native-render and full-suite behavior remain unverified. The antipattern, test-link and dead-export gates passed. Local lint and collection lacked ESLint and Playwright, and the app typecheck reported missing Node and React types. The integration typecheck produced the same six configuration diagnostics before and after. During tooling setup I removed a temporary compiler link that had resolved into the provisioned runtime’s shared binary directory. [macOS annotation](/workspace/test-audit-replay-v2/subjects/81ed009d77b57e5c/work/ci-snapshot.json:1498) · [Identity job](/workspace/test-audit-replay-v2/subjects/81ed009d77b57e5c/work/ci-snapshot.json:1602) · [Type diagnostics](/workspace/test-audit-replay-v2/subjects/81ed009d77b57e5c/work/worker-types.log)\n",
      "patch": "diff --git a/app/test/integration/state-machine-fuzz.test.ts b/app/test/integration/state-machine-fuzz.test.ts\nindex cc19793..1ea1cef 100644\n--- a/app/test/integration/state-machine-fuzz.test.ts\n+++ b/app/test/integration/state-machine-fuzz.test.ts\n@@ -453,6 +453,8 @@ const MODEL_SEEDS = parseSeedOverride(\n   DEFAULT_MODEL_SEEDS,\n );\n const MIN_MODEL_CAMPAIGNS = 30;\n+const MAX_MODEL_BATCHES = 3;\n+const MIN_ACCEPTED_COMMANDS = 100;\n const RUNS_PER_SEED = Math.ceil(MIN_MODEL_CAMPAIGNS / MODEL_SEEDS.length);\n const MODEL_TIMEOUT_MS = Math.max(120_000, MODEL_SEEDS.length * 15_000);\n \n@@ -489,12 +491,44 @@ async function replayKnownFailure(schedule: StateMachineOp[]): Promise<void> {\n   }\n }\n \n-function assertModelCoverage(coverage: ModelCoverage): void {\n-  const summary = JSON.stringify(coverage);\n-  expect(coverage.accepted, summary).toBeGreaterThanOrEqual(100);\n-  expect(coverage.byKind.ws_tempo, summary).toBeGreaterThan(0);\n-  expect(coverage.byKind.ws_swing, summary).toBeGreaterThan(0);\n-  expect(coverage.dirtyDisconnects, summary).toBeGreaterThan(0);\n+function hasModelCoverage(coverage: ModelCoverage): boolean {\n+  return coverage.accepted >= MIN_ACCEPTED_COMMANDS\n+    && Object.values(coverage.byKind).every(count => count > 0)\n+    && coverage.dirtyDisconnects > 0;\n+}\n+\n+async function checkModelBatch(seed: number, offset: number, coverage: ModelCoverage): Promise<void> {\n+  const details = await fc.check(\n+    fc.asyncProperty(fc.commands(commandArbs, { maxCommands: 18 }), async (commands) => {\n+      const run = await createConnectedModelRun(coverage);\n+      try {\n+        await fc.asyncModelRun(() => run, commands);\n+      } finally {\n+        run.real.connection?.ws.close(1000, 'model done');\n+      }\n+    }),\n+    {\n+      seed: seed | 0,\n+      // A one-component fast-check path resumes at this example in the seed's stream.\n+      path: String(offset),\n+      numRuns: RUNS_PER_SEED,\n+      interruptAfterTimeLimit: Math.max(\n+        30_000,\n+        Math.floor(MODEL_TIMEOUT_MS / MODEL_SEEDS.length) - 5_000,\n+      ),\n+      markInterruptAsFailure: true,\n+    },\n+  );\n+  if (details.failed) {\n+    if (details.counterexample) {\n+      failWithPbtCounterexample(\n+        'stateMachine',\n+        replayableActions(details.counterexample[0]),\n+        details,\n+      );\n+    }\n+    throw new Error(`stateMachine property interrupted before producing a counterexample (seed=${details.seed})`);\n+  }\n }\n \n it('model: read-your-writes through the DO holds across shrunk command sequences; KV converges at write/disconnect points', async () => {\n@@ -508,40 +542,20 @@ it('model: read-your-writes through the DO holds across shrunk command sequences\n   }\n \n   const coverage = createModelCoverage();\n-  for (const seed of MODEL_SEEDS) {\n-    const details = await fc.check(\n-      fc.asyncProperty(fc.commands(commandArbs, { maxCommands: 18 }), async (commands) => {\n-        const run = await createConnectedModelRun(coverage);\n-        try {\n-          await fc.asyncModelRun(() => run, commands);\n-        } finally {\n-          run.real.connection?.ws.close(1000, 'model done');\n-        }\n-      }),\n-      {\n-        seed: seed | 0,\n-        numRuns: RUNS_PER_SEED,\n-        interruptAfterTimeLimit: Math.max(\n-          30_000,\n-          Math.floor(MODEL_TIMEOUT_MS / MODEL_SEEDS.length) - 5_000,\n-        ),\n-        markInterruptAsFailure: true,\n-      },\n-    );\n-    if (details.failed) {\n-      if (details.counterexample) {\n-        failWithPbtCounterexample(\n-          'stateMachine',\n-          replayableActions(details.counterexample[0]),\n-          details,\n-        );\n-      }\n-      throw new Error(`stateMachine property interrupted before producing a counterexample (seed=${details.seed})`);\n+  // Even on a healthy Worker, a generated sequence can be empty or contain\n+  // commands whose connection preconditions do not hold. Continue successful\n+  // campaigns with fresh examples until the observed work meets the contract.\n+  for (let batch = 0; batch < MAX_MODEL_BATCHES && !hasModelCoverage(coverage); batch++) {\n+    for (const seed of MODEL_SEEDS) {\n+      await checkModelBatch(seed, batch * RUNS_PER_SEED, coverage);\n     }\n+    console.info(`[stateMachine] seeds=${MODEL_SEEDS.join(',')} runsPerSeed=${(batch + 1) * RUNS_PER_SEED} `\n+      + `coverage=${JSON.stringify(coverage)}`);\n   }\n-\n-  // A total command count can hide a missing transition class. These witnesses\n-  // keep the fixed and rotating campaigns honest about the WS/KV lifecycle they\n-  // claim to cover.\n-  assertModelCoverage(coverage);\n+  expect(\n+    hasModelCoverage(coverage),\n+    `Coverage budget exhausted for seeds [${MODEL_SEEDS.join(',')}]. Expected `\n+    + `${MIN_ACCEPTED_COMMANDS} accepted commands, every modeled action, and a dirty disconnect. `\n+    + `Observed ${JSON.stringify(coverage)}`,\n+  ).toBe(true);\n }, MODEL_TIMEOUT_MS);\n",
      "observed_behavior": {
        "schema": "technical-behavior-evidence/v1",
        "case": "Keyboardia",
        "subject_id": "81ed009d77b57e5c",
        "status": "independent technical validation complete",
        "verified_utc": "2026-11-27T02:51:07.020106+00:00",
        "scope": {
          "pin": "aa67598560f8eaf2509a3ad4bc73edee2f8bea8a",
          "maintainer_request": "Survey 58 sampled test files and implement one bounded test repair.",
          "repair": "Continue each configured seed’s fast-check sequence in the actual DO/WS/KV integration model. Aggregate its observed executed coverage across seeds. Continue only after successful batches, up to three.",
          "contract": "At least 100 executed commands, each of nine initialized action kinds, and at least one disconnect while the model differs from its KV mirror. Genuine failed properties go directly into the original fast-check shrink and promotion path.",
          "changed_paths": [
            "app/test/integration/state-machine-fuzz.test.ts"
          ],
          "entry_point": "/case/runtime/run-worker.sh state-machine-fuzz.test.ts -t \"model: read-your-writes\"",
          "registration": "Existing real workerd integration file and model title, also in the weekly rotating three-file CI lane. No production source or CI workflow changed.",
          "source_locations": [
            "app/test/integration/state-machine-fuzz.test.ts:295",
            "app/test/integration/state-machine-fuzz.test.ts:315",
            "app/test/integration/state-machine-fuzz.test.ts:346",
            "app/test/integration/state-machine-fuzz.test.ts:494",
            "app/test/integration/state-machine-fuzz.test.ts:500",
            "app/test/integration/state-machine-fuzz.test.ts:534",
            ".github/workflows/property-seed.yml:100"
          ],
          "scope_record": {
            "path": "verification-scope.json",
            "sha256": "017b614a0f811083a01a6193f8399fad2776fd1e639158b1120a67211aea56e8"
          }
        },
        "agent_availability": {
          "state": "report-delivered-agent-status-unavailable",
          "response_file_mtime_utc": "2026-11-27T02:39:04.198661+00:00",
          "declared_deadline_utc": "2026-11-27T02:42:51Z",
          "response_before_deadline": true,
          "seal_utc": "2026-11-27T02:41:11.416967+00:00",
          "agent_chat_final": "unavailable",
          "model_retries": 0,
          "explanation": "A second registry/metadata transition occurred after the report file existed. The report, patch, snapshot and 32 submitted files were retained. Backend turn completion, precise interruption time and model runtime are unavailable. Dispatch-to-seal includes observation delay.",
          "elapsed_dispatch_to_seal_seconds": 1399.607514,
          "records": [
            {
              "path": "disposition.json",
              "sha256": "5650539c43739c6d9199dc11b990d53446cf071789d37d792902e551d2e28ce6"
            },
            {
              "path": "interruption.json",
              "sha256": "0a5476f0e890de967c149a2b06e18f39bf74fca449bbc762319fc353afe88f57"
            }
          ]
        },
        "harness": {
          "candidate": "Complete sealed candidate snapshot. Fresh scratch copy per frozen case or exploratory control.",
          "script": "preparation/keyboardia/postcandidate.py",
          "container": "node:24.22.3-bookworm; --pull=never; --network=none; read-only root and dependency mounts; scratch worktree writable; 2 CPUs, 2 GiB, capability drop, no-new-privileges, non-root.",
          "serialization": "All candidate executions passed through flock /tmp/test-audit-v2-docker.lock and the bounded frozen runner (180 seconds per invocation).",
          "original_reuse": "Unchanged reference observations from preparation/keyboardia/evidence/seed-controls/ are reused, with per-log SHA-256 in the frozen matrix.",
          "first_attempts": "Every post-candidate check completed on its first invocation. Intended failures and complete original logs are retained. The exploratory clean transport labels its arbitrary stimulus original; the stimulus, assertions and expected outcomes appear here."
        },
        "frozen_seed_matrix": [
          {
            "case": "default_model",
            "stimulus": "Healthy DO, default seed set.",
            "expected": "accept",
            "selector": "model: read-your-writes",
            "original": {
              "exit": 0,
              "assertion": "Existing model passes.",
              "frozen_log": "evidence/seed-controls/default_model.log",
              "sha256": "7f503e807e5ff821c8720f8182c0553268609c52e7b4dcbe0c51545096fc3ddb"
            },
            "candidate": {
              "exit": 0,
              "assertion": "Changed model passes after three schedules per seed, 33 schedules overall, all nine kinds, four dirty disconnects and 147 executed commands.",
              "coverage": [
                {
                  "seeds": "24301,1,7,42,1337,90210,12648430,2024,555,31337,4096",
                  "runs_per_seed": 3,
                  "accepted": 147,
                  "dirtyDisconnects": 4,
                  "byKind": {
                    "ws_tempo": 9,
                    "ws_swing": 15,
                    "rest_put": 14,
                    "rest_patch_state": 21,
                    "rest_patch_name": 20,
                    "hibernate": 27,
                    "hard_evict": 28,
                    "disconnect": 11,
                    "connect": 2
                  }
                }
              ],
              "log": {
                "path": "registered-seed/default_model.log",
                "sha256": "7a53f8b979ba1b0792d4717dd27e7420a989be9c9b0b679cc2d4be7e6edae8da"
              }
            },
            "attribution": "Retained legal default."
          },
          {
            "case": "valid_schedule",
            "stimulus": "Healthy DO, recorded rotating seed 45182094013.",
            "expected": "accept",
            "selector": "model: read-your-writes",
            "original": {
              "exit": 1,
              "assertion": "Model failed only at the aggregate 100-command floor after 99 commands, all nine kinds and three dirty disconnects.",
              "frozen_log": "evidence/seed-controls/valid_schedule.log",
              "sha256": "7fc3f9a75647f426bd38020366b313a60846a4d798075780ecb0aac179448e83"
            },
            "candidate": {
              "exit": 0,
              "assertion": "First 30 schedules produce the same 99 commands. After the next 30 schedules, totals are 234 commands, all nine kinds and six dirty disconnects.",
              "coverage": [
                {
                  "seeds": "45182094013",
                  "runs_per_seed": 30,
                  "accepted": 99,
                  "dirtyDisconnects": 3,
                  "byKind": {
                    "ws_tempo": 10,
                    "ws_swing": 13,
                    "rest_put": 9,
                    "rest_patch_state": 11,
                    "rest_patch_name": 14,
                    "hibernate": 17,
                    "hard_evict": 11,
                    "disconnect": 8,
                    "connect": 6
                  }
                },
                {
                  "seeds": "45182094013",
                  "runs_per_seed": 60,
                  "accepted": 234,
                  "dirtyDisconnects": 6,
                  "byKind": {
                    "ws_tempo": 22,
                    "ws_swing": 25,
                    "rest_put": 28,
                    "rest_patch_state": 36,
                    "rest_patch_name": 30,
                    "hibernate": 36,
                    "hard_evict": 31,
                    "disconnect": 16,
                    "connect": 10
                  }
                }
              ],
              "log": {
                "path": "registered-seed/valid_schedule.log",
                "sha256": "29c45b18f87f5879ee6deb0518b334e24f55de597bc884a9437388d4c80d3292"
              }
            },
            "attribution": "Changed response to a valid short first batch; existing state assertions still execute."
          },
          {
            "case": "persistence_original",
            "stimulus": "Healthy DO, fixed WS-to-KV test.",
            "expected": "accept",
            "selector": "WS mutation makes KV lag",
            "original": {
              "exit": 0,
              "assertion": "Fixed test passes.",
              "frozen_log": "evidence/seed-controls/persistence_original.log",
              "sha256": "8410a8b917bad1a5b9f37dce2c4eba36b4ddca55a37057564bb141347efff935"
            },
            "candidate": {
              "exit": 0,
              "assertion": "Fixed test passes. It observes GET tempo 150 and KV 120 after a WS write, then KV 150 after last-client close.",
              "coverage": [],
              "log": {
                "path": "registered-seed/persistence_original.log",
                "sha256": "0ff42e4f82a2c720af66cdbc932ab0e5c980cf538e3fffa74c8684aed31f83c7"
              }
            },
            "attribution": "Pre-existing fixed keeper; code is identical."
          },
          {
            "case": "persistence_fault",
            "stimulus": "Skip only the final save in flushPendingKVSave.",
            "expected": "reject",
            "selector": "WS mutation makes KV lag",
            "original": {
              "exit": 1,
              "assertion": "Fixed test fails, expected KV tempo 150 and observed 120.",
              "frozen_log": "evidence/seed-controls/persistence_fault.log",
              "sha256": "a3880f3416342fd47b44a076e481c3c3cadc3dd9cbea1981aa8e6c1d115cdd57"
            },
            "candidate": {
              "exit": 1,
              "assertion": "The same fixed test fails at the post-disconnect KV read, expected 150 and observed 120.",
              "coverage": [],
              "log": {
                "path": "registered-seed/persistence_fault.log",
                "sha256": "89b54d43b9eacb11523950af1546fdaa4a1c00a8961ba96c5af661dd7661cdd6"
              }
            },
            "attribution": "Pre-existing fixed keeper. The changed model is separately executed against this fault below."
          }
        ],
        "frozen_reference_results": {
          "path": "preparation/keyboardia/evidence/seed-controls/results.json",
          "sha256": "feb155ec71255f327035603b9a941502a1dcdcd8eb39a0ec3449e94cbe91d978"
        },
        "candidate_registered_results": {
          "path": "registered-seed/results.json",
          "sha256": "d68724a989269f500727239cf86e54ba43c05570df4eeb60c0dcb29ed74c3fd8"
        },
        "exploratory_controls": [
          {
            "id": "model-final-flush",
            "class": "EXPLORATORY",
            "stimulus": "Frozen missing-final-save mutation, changing only the selector to the actually submitted model.",
            "original": "Fixed keeper sensitivity is established separately. The model state oracle and shrink/serialization path predate this patch.",
            "candidate": {
              "container_exit": 1,
              "log": {
                "path": "exploratory-model-final-flush/persistence_fault.log",
                "sha256": "dacd3dfad68cc46d5fd64cf3c3fd3415bc11ac6b96ebc05177dee5f70e01a733"
              },
              "selected_tests": 1,
              "assertion": "Model read stale KV swing 0, expected 1 after a WS edit and a disconnect. Failure went through shrinking before any successful batch summary.",
              "counterexample": {
                "lane": "stateMachine",
                "example": [
                  {
                    "kind": "ws_swing",
                    "swing": 1
                  },
                  {
                    "kind": "disconnect"
                  }
                ],
                "seed": 1,
                "path": "0:3:1:1:1:1:1:1",
                "shrinks": 7
              }
            },
            "meaning": "Confirms genuine persistence failure propagation in the executed candidate model."
          },
          {
            "id": "continuous-stream",
            "class": "EXPLORATORY",
            "stimulus": "Emit replayable executed actions for every real model schedule. Compare candidate batch offsets 0 and 30 with one ordinary 60-example fast-check call from the same seed without a path option.",
            "candidate": {
              "container_exit": 0,
              "log": {
                "path": "exploratory-stream/original.log",
                "sha256": "d4e2b8b2615340de33cd76535acdae463250d20a41f0bea6df78cb862fa7374a"
              },
              "peer": "single ordinary fast-check invocation, same seed, 60 schedules, no path option",
              "matched": 60,
              "commands": [
                99,
                135
              ],
              "schedule_sha256": [
                "7754fcd08268bb6e570c2eba1962459923b7bf9f76de6b371842dccf795af24f",
                "4d999bfabeeec921b87bbe7e275272e8548609c59a97d5ae26ebde8451158031",
                "d266b90d0d39febf9c342d0925aecf56a79f406f9bfb7817e9ca203c65820989"
              ]
            },
            "assertion": "Exact ordered action arrays, parameters and empty arrays matched for all 60 schedules. The halves differed and executed 99 and 135 commands. This comparison covers the reported historical seed and locked Worker fast-check version."
          },
          {
            "id": "second-batch-fault-and-promotion",
            "class": "EXPLORATORY",
            "stimulus": "Cap the Worker REST PATCH swing field at 99 before storing it. Use the actual deposited model and project promotion CLI.",
            "candidate": {
              "container_exit": 0,
              "log": {
                "path": "exploratory-promotion/original.log",
                "sha256": "392822151d5be81bcae0b6adbbcf520bae421260d2040ffc0b54310ef0e5a6b2"
              },
              "historical_seed_worker_exit": 1,
              "first_stimulus": {
                "lane": "stateMachine",
                "example": [
                  {
                    "kind": "rest_patch_state",
                    "tempo": 60,
                    "swing": 100
                  }
                ],
                "seed": -2062546243,
                "path": "51:1",
                "shrinks": 1
              },
              "stored": [
                [
                  {
                    "kind": "rest_patch_state",
                    "tempo": 60,
                    "swing": 100
                  }
                ]
              ],
              "replay_seed": 42,
              "faulted_replay_exit": 1,
              "restored_replay_exit": 0
            },
            "assertion": "Only batch 1 reported success before the second batch hit actual swing 99 vs expected 100. The one-shrink counterexample was a single PATCH(60,100). The real CLI wrote that sole example to the scratch known-failures database. With seed 42 the model failed at known-failure #0 before random exploration. Restoring the Worker while keeping the example let seed 42 pass.",
            "attribution": "Additional exploration reaches this specific regression; shrinking, the marker/codec, the real promotion CLI and replay-before-exploration were inherited."
          },
          {
            "id": "mandatory-hibernate-and-bound",
            "class": "EXPLORATORY",
            "stimulus": "Delete only the hibernate command factory from default generation in independent clean scratch copies of original and candidate.",
            "original": {
              "container_exit": 0,
              "log": {
                "path": "exploratory-hibernate-original/original.log",
                "sha256": "bb0c6f7aa405a480bd694bf1fd54a7543966fb471ec8a71856f7b2a45db7c1c3"
              }
            },
            "candidate": {
              "container_exit": 1,
              "log": {
                "path": "exploratory-hibernate-candidate/original.log",
                "sha256": "b20a40a0770e7d8991ba5e32fea24132d241b243ad9acd496f4db3b1eea03423"
              },
              "coverage": [
                {
                  "seeds": "24301,1,7,42,1337,90210,12648430,2024,555,31337,4096",
                  "runs_per_seed": 3,
                  "accepted": 143,
                  "dirtyDisconnects": 3,
                  "byKind": {
                    "ws_tempo": 18,
                    "ws_swing": 12,
                    "rest_put": 21,
                    "rest_patch_state": 17,
                    "rest_patch_name": 24,
                    "hibernate": 0,
                    "hard_evict": 27,
                    "disconnect": 13,
                    "connect": 11
                  }
                },
                {
                  "seeds": "24301,1,7,42,1337,90210,12648430,2024,555,31337,4096",
                  "runs_per_seed": 6,
                  "accepted": 251,
                  "dirtyDisconnects": 4,
                  "byKind": {
                    "ws_tempo": 28,
                    "ws_swing": 28,
                    "rest_put": 37,
                    "rest_patch_state": 35,
                    "rest_patch_name": 37,
                    "hibernate": 0,
                    "hard_evict": 49,
                    "disconnect": 21,
                    "connect": 16
                  }
                },
                {
                  "seeds": "24301,1,7,42,1337,90210,12648430,2024,555,31337,4096",
                  "runs_per_seed": 9,
                  "accepted": 393,
                  "dirtyDisconnects": 6,
                  "byKind": {
                    "ws_tempo": 40,
                    "ws_swing": 35,
                    "rest_put": 62,
                    "rest_patch_state": 63,
                    "rest_patch_name": 62,
                    "hibernate": 0,
                    "hard_evict": 72,
                    "disconnect": 36,
                    "connect": 23
                  }
                }
              ]
            },
            "assertion": "Original fixed-seed model remains green. The candidate exhausts three batches, 9 schedules per seed across 11 seeds (99 total schedules). The final 393 operations include six dirty disconnects, every other kind and zero hibernations. The coverage assertion fails."
          },
          {
            "id": "independent-dirty-disconnect-and-bound",
            "class": "EXPLORATORY",
            "stimulus": "Historical seed with graceful disconnect allowed only when the model already equals its KV mirror. Other commands and all bookkeeping are unchanged.",
            "candidate": {
              "container_exit": 1,
              "log": {
                "path": "exploratory-dirty-candidate/original.log",
                "sha256": "542ed932a826118251a02e0f7c402b7c14cb881b1bc5d4d3536aa0c149d6e9ca"
              },
              "coverage": [
                {
                  "seeds": "45182094013",
                  "runs_per_seed": 30,
                  "accepted": 97,
                  "dirtyDisconnects": 0,
                  "byKind": {
                    "ws_tempo": 10,
                    "ws_swing": 14,
                    "rest_put": 9,
                    "rest_patch_state": 11,
                    "rest_patch_name": 14,
                    "hibernate": 17,
                    "hard_evict": 11,
                    "disconnect": 5,
                    "connect": 6
                  }
                },
                {
                  "seeds": "45182094013",
                  "runs_per_seed": 60,
                  "accepted": 230,
                  "dirtyDisconnects": 0,
                  "byKind": {
                    "ws_tempo": 24,
                    "ws_swing": 26,
                    "rest_put": 28,
                    "rest_patch_state": 36,
                    "rest_patch_name": 30,
                    "hibernate": 36,
                    "hard_evict": 31,
                    "disconnect": 10,
                    "connect": 9
                  }
                },
                {
                  "seeds": "45182094013",
                  "runs_per_seed": 90,
                  "accepted": 359,
                  "dirtyDisconnects": 0,
                  "byKind": {
                    "ws_tempo": 33,
                    "ws_swing": 49,
                    "rest_put": 49,
                    "rest_patch_state": 53,
                    "rest_patch_name": 43,
                    "hibernate": 58,
                    "hard_evict": 47,
                    "disconnect": 16,
                    "connect": 11
                  }
                }
              ]
            },
            "assertion": "Three batches reach 90 schedules, 359 executed commands, all nine kinds and 16 clean disconnects. Zero dirty disconnects triggers the coverage failure. This isolates the independent lifecycle requirement from total command count and the generic disconnect count.",
            "attribution": "The dirty-disconnect guard was present in the pinned model."
          }
        ],
        "legitimate_inputs": [
          {
            "input": "Default and historical short-first-batch schedule",
            "source": "Independent registered matrix; deterministic legal historical input accepted without lowering threshold, dropping classes, changing seed or bypassing Worker reads."
          },
          {
            "input": "Override 1,7,42; zero; signed -1",
            "source": "Retained subject logs, one selected model test green each.",
            "observations": [
              {
                "log": "submitted-artifacts/final-multi.log",
                "counts": [
                  {
                    "seeds": "1,7,42",
                    "runs_per_seed": 10,
                    "accepted": 109,
                    "dirtyDisconnects": 3,
                    "byKind": {
                      "ws_tempo": 7,
                      "ws_swing": 12,
                      "rest_put": 11,
                      "rest_patch_state": 14,
                      "rest_patch_name": 18,
                      "hibernate": 16,
                      "hard_evict": 19,
                      "disconnect": 7,
                      "connect": 5
                    }
                  }
                ]
              },
              {
                "log": "submitted-artifacts/final-zero.log",
                "counts": [
                  {
                    "seeds": "0",
                    "runs_per_seed": 30,
                    "accepted": 134,
                    "dirtyDisconnects": 5,
                    "byKind": {
                      "ws_tempo": 7,
                      "ws_swing": 9,
                      "rest_put": 16,
                      "rest_patch_state": 24,
                      "rest_patch_name": 18,
                      "hibernate": 25,
                      "hard_evict": 17,
                      "disconnect": 14,
                      "connect": 4
                    }
                  }
                ]
              },
              {
                "log": "submitted-artifacts/final-negative.log",
                "counts": [
                  {
                    "seeds": "-1",
                    "runs_per_seed": 30,
                    "accepted": 117,
                    "dirtyDisconnects": 1,
                    "byKind": {
                      "ws_tempo": 7,
                      "ws_swing": 11,
                      "rest_put": 11,
                      "rest_patch_state": 14,
                      "rest_patch_name": 15,
                      "hibernate": 21,
                      "hard_evict": 17,
                      "disconnect": 12,
                      "connect": 9
                    }
                  }
                ]
              }
            ]
          },
          {
            "input": "Healthy owner with promoted single PATCH and different seed 42",
            "source": "Independent promotion/replay pair; the same database accepted the restored implementation."
          }
        ],
        "keepers": {
          "model_observations": "Existing action-specific socket acknowledgments, REST status/authoritative GET (tempo, swing, name), independent KV state, and actual WebSocket readyState are maintained after accepted operations. Fixed last-client save and the new model both detect a removed last save. The hibernate action witnesses occurrence; the separate WS-only recovery case covers wake without an intervening REST GET.",
          "model_replay": "Real fast-check shrink, machine-readable failure and promotion/replay logic predate the repair. The patch preserves them and reaches a real second-batch mutant.",
          "other_sampled_examples": [
            {
              "path": "app/test/integration/collaboration-contract.test.ts:224",
              "observation": "Two sockets receive matching acknowledgments and ordered sequence values. The test reads three touched cells through REST. Retained focused Worker log."
            },
            {
              "path": "app/test/integration/eviction-recovery.test.ts:727",
              "observation": "WS-only wake, acknowledgments, then second eviction and reads of both tempo 166 and swing 33. The rotating lane was independently rechecked."
            },
            {
              "path": "app/src/sync/session.persistence.test.ts:109",
              "observation": "Controlled fetch is held open to check client save ordering. This covers the client HTTP boundary."
            },
            {
              "path": "app/src/audio/session-render-conservation.render.test.ts:89",
              "observation": "Source checks measured onset count and timing against 0.125 seconds/step at 120 BPM. Native render execution remains unavailable."
            }
          ]
        },
        "other_findings": {
          "sequence_rewind": {
            "evidence": "The unchanged real Worker test drives three mutations and an eviction on a surviving socket, then sees sequence 1 again while GET still reads tempo 140. A separate unchanged production-client test uses controlled sockets and fake time. It applies a regressed edit and opens a third socket after the second group of eleven regressed frames. The existing test also recovers after the counter exceeds the earlier high-water mark.",
            "contract": "Worker periodically persists its sequence counter. Client SyncHealth records older frames without lowering its high-water mark, recovers after excessive out-of-order frames, and its receive path still dispatches those frames. The supplied characterization checks explicitly describe the churn. These observations establish this bounded behavior. Production frequency, data loss, a mandatory alternative epoch/reset policy and an impact ranking are unestablished.",
            "sources": [
              "app/test/integration/seq-regression.test.ts:119",
              "app/src/sync/seq-regression.test.ts:168",
              "app/src/sync/sync-health.ts:171",
              "app/src/sync/multiplayer.ts:1274",
              "app/src/worker/live-session.ts:3036",
              "submitted-artifacts/final-focus-worker.log",
              "focused-recheck/original.log"
            ]
          },
          "waveform": {
            "evidence": "All four tests call their local computePeaks, while the canvas calls its separate private function. The retained subject mutant run reports all four tests green with the production function made to throw. The clean unit selection independently passes the four tests. The submitted mutation was temporary; the output log alone does not preserve the exact uncommitted edit.",
            "attribution": "Existing documented test-local implementation gap. The submitted repair changes the Worker model only.",
            "sources": [
              "app/src/components/waveform-peaks.test.ts:11",
              "app/src/components/Waveform.tsx:100",
              "submitted-artifacts/control-waveform.log",
              "focused-recheck/original.log"
            ]
          }
        },
        "availability": {
          "assignment": {
            "survey": 58,
            "strata": 9,
            "inventory": 370,
            "sampled_paths_run_from_selections": 42,
            "evidence": "42 distinct sampled files from 23 default unit, 11 additional unit and 8 sampled Worker files. All 58 frozen base blob IDs were checked independently. Depth of the claimed source survey is self-reported."
          },
          "independent_focused_recheck": {
            "container_exit": 0,
            "log": {
              "path": "focused-recheck/original.log",
              "sha256": "20ea4cf0c6363afc94810460852d69e9e64b8296295714000b69adaaeff538c2"
            },
            "three_rotating_worker_files": "28/28 passed at 45182094013",
            "three_unit_files": "10/10 passed: three existing promote-pbt-counterexamples unit cases, three existing client sequence cases and four existing waveform-local cases."
          },
          "retained_subject_results": {
            "baseline_unit": "343/343, 23 files (baseline-unit.log)",
            "additional_unit": "120/120, 11 files (additional-unit.log)",
            "neighbor_client_sequence": "3/3 (client-seq.log)",
            "baseline_and_final_focused_worker": "84/84 in 8 files (baseline-worker.log, final-focus-worker.log)",
            "complete_worker": "131/131 in 11 files (final-all.log), retained subject run; whole Worker suite was not repeated for this record. The sample overlaps this suite.",
            "rotating_three_files_before_after": "27 pass + 1 quota failure to 28 pass (ci-seed-before.log, final-ci.log), final independently reproduced.",
            "gates": "After access to the provisioned Worker compiler, subject logs record a passing test-antipattern scan (365 files), test-links and dead-export checks. The original missing-TypeScript attempt is retained."
          },
          "hosted_history": "Pinned main CI receipt contains 15 successes, 1 macOS visual cancellation before steps (unsupported configuration), and 1 skipped Stack A Identity. Rotating unit succeeded; integration preserved the job failure after counterexample handling. This is hosted history, with no new hosted execution.",
          "tooling_limits": "Subject logs report ESLint unavailable, Playwright collection ENOTCACHED, app tsc initially unavailable, then missing Node/React declarations with the Worker compiler. Integration before/after typecheck logs match byte for byte with six pre-existing vitest.config.ts diagnostics. A clean app or integration typecheck was not demonstrated.",
          "untested": "Local browser/Darwin/native audio and full application Vitest matrix. Independent reruns covered specified commands and a bounded set of seeds/controls; no assertion of exhaustive seed acceptance, suite-wide mutation sensitivity, CI rerun, or novel discovery."
        },
        "runtime_protocol_deviation": {
          "observed": "The subject disclosed creating/removing a temporary compiler link that resolved through a shared .bin directory during setup. The supplied attach.py symlinks each package and the .bin directory into the writable checkout. Shared-host participants were expected to treat provisioned dependencies as read-only under a procedural path protocol. This is a reported write outside the assigned checkout.",
          "current_observation": "App .bin has 12 links, all declared and resolving, and no tsc. The projected app lock omits TypeScript. Worker .bin has 8 declared resolving links, including tsc to ../typescript/bin/tsc from TypeScript 5.9.3. Both top-level .bin inventories exactly match their corresponding installed lock bin metadata at inspection.",
          "limits": "No pre-event directory image or independent audit of the transient write, its window or cross-subject effect. The present match cannot establish the absence of earlier interference. The verifier made no changes to shared dependencies. Offline read-only Docker mounts apply to evaluator executions; subject isolation was procedural.",
          "evidence": {
            "path": "runtime-bin-observation.json",
            "sha256": "35bcb66eb1aed157c71a08e039e7ac22e58039036048bfba5fcd2363e4a41873"
          }
        },
        "limits_and_attribution": [
          "Coverage is accumulated across the configured seeds, with every seed visited once in each attempted batch. The code does not promise that any individual seed covers every class.",
          "The three-batch cap bounds examples. A legal seed can still fail on genuinely insufficient sampled coverage after that cap. This is not a proof of green behavior for every seed or under every runtime/time budget. Existing per-check interrupts and the overall Vitest title timeout still apply.",
          "Adding coverage for all enumerated kinds detects a missing hibernate generator. A recorder count for an action is not by itself a proof of every effect of that action. State and lifecycle evidence comes from the retained read/acknowledgment/transport assertions and the fixed specific keepers.",
          "Specific faults and legal runs were exercised. Other frozen sync/discovery candidates were outside the submitted repair. The overall impact ranking in the subject response was not independently established."
        ],
        "artifact_provenance": {
          "sealed_report": {
            "path": "response.md",
            "sha256": "b47d6084bac3e5bbebbed975d8fcd99269973c6933d2c771fc724e02c4298b1b"
          },
          "sealed_patch": {
            "path": "patch.diff",
            "sha256": "f8b27ed2da5a9b82aabc92102b7ef29923145bc5935020cbd9360aaee396d0b7"
          },
          "sealed_tree_manifest": {
            "path": "candidate-snapshot.json",
            "sha256": "35939ef42941883a682a1e856e1e557a015ab021de186fc8c878f282e32627ed"
          },
          "submitted_collection_manifest": {
            "path": "submitted-artifacts/collection.json",
            "sha256": "40e708bde76df27bb072c122c5d37dc9e8c7911ee18fa043bef3e5963190f4ae"
          },
          "integrity_record": {
            "path": "artifact-verification.json",
            "sha256": "926dea0e9d54b9d091a26f99f3a70fecb6ee617b54295f7e6394faac94c5ea04"
          },
          "checked_snapshot_paths": 985,
          "differences_from_pinned_export": {
            "app/test/integration/state-machine-fuzz.test.ts": {
              "base_sha256": "2e94b53a32fa518d9157611bc7133c020dd1d1091dddbd028ffef2bf7edb8516",
              "candidate_sha256": "5ebbcacaefd6c8d955a4295238e5f044b8853e5807559e60c19275593717861c"
            }
          },
          "all_retained_inputs_rehashed": 32,
          "retained_file_types": {
            ".log": 30,
            ".txt": 1,
            ".tsv": 1
          },
          "baseline_archive_sha256": "c1b763f7f1f5f7beacb1e52a0fdfff53a49a0ad85f7749ef7edb472ffdfb9a34",
          "exploratory_driver": {
            "path": "exploratory-control.py",
            "sha256": "7f280a0ec778016124fd79a4147e209cedc11bf2cc710735bf7c3165c2502275"
          },
          "paths": "Local evidence paths are relative to the sealed output directory unless prefixed preparation/ or app/. Per-log hashes for all 32 original submitted files are in the collection manifest."
        }
      }
    }
  ]
}
