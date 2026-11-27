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
  "case": "B03",
  "task": "# Audit PDA's test suite\n\nYou have 25 minutes to audit this pinned PDA source snapshot and deliver one focused improvement to its tests. Decide where additional or more precise evidence would matter to a maintainer. You may change an existing test or add a test at a suitable project boundary. Keep the patch focused on tests and their fixtures.\n\nLeave your test changes in `repo/`. Write a short `report.md` beside this task with the following:\n\n- State which checks, areas and callers you examined. Explain which behavior matters and where its expected result comes from.\n- Prioritize up to three findings. Give file and line references and identify existing coverage worth preserving.\n- For the change you selected, record the commands actually run, their results and the limits of your conclusion. Account for any temporary experiment in your report.\n\n`inventory.json` lists all first-party named test modules at `adewale/pda@c0a9a85c8f690eb77313b9627e3ea39cadc58968`. The source directory includes 56 complete modules and their project configurations, application sources, support code and selected protocol references. The three GitHub job responses under `ci/` describe CI on the full repository at the pin. A hosted status describes the command on that commit. Each local run selects the files supplied to it.\n\n## Running focused tests\n\nUse Node 24. Dependency preparation is outside the 25-minute audit budget. From `repo/`, use an existing locked dependency installation or run `npm ci --legacy-peer-deps`. For a source directory without Git metadata, `git init -q` enables the repository inventory used by the Workers test configuration. No commit is needed. Use the native commands that suit your chosen files.\n\n| Project | From the source directory |\n| --- | --- |\n| Workers | `node node_modules/vitest/vitest.mjs run --config test/vitest.config.ts <path>` |\n| Durability | `node node_modules/vitest/vitest.mjs run --config test/durability/vitest.config.ts <path>` |\n| Page | `node node_modules/vitest/vitest.mjs run --config test/ui/vitest.config.ts <path>` |\n| Interop harness | `node node_modules/vitest/vitest.mjs run --config interop/vitest.config.ts <path>` |\n| Properties | `node node_modules/vitest/vitest.mjs run --config test/properties/vitest.config.ts <path>` |\n| Node tooling | `node --test <path>` |\n\nThe source package samples tests and protocol materials. Some checks that inventory the full repository, read historical snapshots or need separate dependencies require a full checkout. Name the actual local selection and any such dependency in your report.\n",
  "case_criteria": "# Evaluator instructions\n\nThis is a reconstruction of the 2026-11-26 PDA audit. The primary behavior comes from finding pda-02. The prior report read nine complete test modules and sections of other files. This packet contains 56 complete test modules across nine native test groups. Prior knowledge influenced eight inclusions and the choice of comparator. Treat the result as a replay on a larger suite sample. An auditor can reasonably identify a different consequential issue.\n\n## Prespecified evidence\n\nThe export promises personal data and the original photos. See `pda-spec.md:344`, `docs/using.md:79` and the download's instructions in `src/agent-data-export.ts`. The input fixture exists before serialization. `src/agent.ts` passes attachment bytes to `saveAttachment`, which writes file chunks to real SQLite using its migration and sequence key. The authenticated GET in `src/agent-data-routes.ts` calls this agent's export. The comparison point is the downloaded file as consumed using the documented attachment ID, part and sequence. A test at a narrower boundary can earn corresponding evidence when it exercises an actual producer and independently reconstructs the payload. Name the boundary precisely.\n\nThe two photo assertions at `test/agent-data.test.ts:97` check row count and the first encoding label. Other assertions in the same test separately establish the caller's memory, absence of a second person's memory, omission of credentials, anonymous 401 and no-store response. The renderer-to-upload test at `test/ui/attachments.test.tsx:111` verifies the exact bytes of a selected file on the client side. It covers another boundary. Inspect all modified or removed assertions.\n\n| Challenge | Behavior | Expected original | Expected repaired photo proof |\n| --- | --- | --- | --- |\n| clean | Pinned production and test fixtures | Pass | Pass |\n| empty-data | The serializer emits empty strings for SQL BLOBs, retaining the rows and base64 labels | Pass full original 31-owner-test file | Fail on missing restored bytes |\n| tail-bit | One trailing bit changes in each original-file chunk after sequence zero; lengths, identifiers and base64 remain valid | Pass full original 31-owner-test file | Fail on changed content |\n| physical-order | The private writer inserts chunks in descending sequence order while each serialized key and payload stays correct | Pass | Pass |\n| member-order | The serialized byte object's keys are emitted data-first | Pass | Pass |\n| auth-keeper | The test harness alone substitutes an empty 200 at the unauthenticated GET response after exercising the route | Original combined test fails on expected 401 | Retain this sensitivity |\n| isolation-keeper | The test harness adds a synthetic second-person sentinel to the exported JSON after the route returns | Original combined test fails on forbidden sentinel | Retain this sensitivity |\n| upload-byte-keeper | The page sends a same-name/type/size file with zeroed bytes to its existing stubbed fetch | Original page test fails on uploaded byte content | Retain this sensitivity |\n\nThe complete owner module runs on the five main challenges. The clean case also runs all 14 page attachment tests. The three keeper probes select their original affected case by name. If a subject splits or renames a check, select all changed tests against the same test-harness fault and adjudicate the equivalent observation independently. A renamed/filtered case that selected zero is unverified. An added case in another native test file runs on the main challenges if supplied as part of the full candidate or with `--extra-test`. A failing entry must be the relevant test and assertion. Startup or unrelated failures, an unconditional failure, disabled assertions, timeouts and empty selections provide no fault-detection credit.\n\nRecord each dimension independently:\n\n- **Detected byte loss:** clean passes and the candidate's own relevant assertion fails for `empty-data`, while the complete original owner file accepts that same change.\n- **Detected content corruption:** the candidate detects `tail-bit` with the clean case passing. Checking length, base64 syntax or file magic alone gives no content-equality credit.\n- **Accepted permitted changes:** run both representation variants. Note row-order assumptions, serialized-object snapshots or internals that make a clean reconstruction turn red.\n- **Preserved evidence:** record which of the existing auth, isolation, redaction and upload-byte checks survive. Inspect source and record all three controlled keeper outcomes. Missing probes are unresolved until rerun or adjudicated with equivalent fixtures.\n- **Strength of the proof:** describe independent expected bytes and actual seams. Distinctive data on both sides of a real boundary avoids masked duplicates or transpositions. Length plus high-quality digest or full byte equality is acceptable. An invented copy of the production algorithm, mocks that decide both sides, or claims about unexecuted tiers lose the corresponding evidence.\n- **Alternate valid repair:** record discovery of this target separately from a different demonstrated improvement. For a different finding, preserve its actual changed test, run baseline and candidate on the same credible behavioral fault or allowed implementation change, and check the opposite-direction control. Record its independent expected value, original failure mode and relevant keepers. Static leads, coverage counts, or a self-reported run stay labelled as such. Judge the proof's value on that contract separately. An unrelated improvement does not earn a photo result.\n\nThe optional, preregistered pda-05 alternative is a page assertion on waiver membership versus order. `src/agent-data.ts:53` stores a set and `src/agent.ts:753` checks membership. The `waiver-order` control reverses the same IDs. `waiver-missing` and `waiver-extra` omit one shown ID or add one unshown fixture ID. The original page should pass on clean, fail on all three, and a test that proves exactly the permitted membership should accept the permutation and reject both membership errors. Run the complete `test/ui/agent-data.test.tsx` for all four variants. The public task names neither this case nor the photo case.\n\n## Scope of evidence\n\nThe native Workers project uses Miniflare/workerd, the repository's faked external services and generated test credentials, the real Durable Object storage API, production attachment migration/write and structured HTTP export. The page project uses happy-dom and its preexisting fetch stub. The primary execution does not establish that the complete 70-file Workers project or every other CI tier accepts a fault. A separate literal scan of all 155 named modules found only the route owner, the page controls and the dependency-free live preflight naming this surface. That search cannot establish absence of dynamic or indirect coverage.\n\nThe original report's earlier Node-SQLite bridge was a focused exploration. This replay independently reruns the complete owner file natively. Hosted success and historical owner reviews are complementary evidence only.\n",
  "candidates": [
    {
      "id": "b08defec2ed06e50",
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
      "id": "4db08cd82e771644",
      "disposition": "returned",
      "response_source": "submitted file",
      "raw_response": "# PDA test audit\n\n1. **The export test accepted a corrupted photo.** At the pin, `test/agent-data.test.ts:97` counted two chunks and checked one encoding label. A person could rely on that download before erasing the agent. The revised test reconstructs the 2 MiB original and its distinct preview from the authenticated response, grouping by attachment ID and part, sorting by sequence, and comparing every decoded byte with the upload. The expected bytes come from the inputs. The format comes from `pda-spec.md:230`, `pda-spec.md:344` and the download instructions at `src/agent-data-export.ts:130`. The same test also checks owner isolation, credential omission, download headers and unauthenticated access. [Changed test](/workspace/test-audit-replay-v2/subjects/d3dfc73ed6d4ddba/work/repo/test/agent-data.test.ts:101)\n2. **The cancellation test can miss a locked table.** `test/agent-data.test.ts:365` reads once from each stream. The exporter emits a header before any data row. Temporarily yielding directly from the SQLite cursor at `src/agent-data-export.ts:139` still let the HTTP cancellation check pass. A temporary workerd probe paused after the first of five memory rows. Erasure then failed with `SQLITE_LOCKED` at `src/agent-data.ts:78` and passed with the original batched reader. Keep the HTTP cancellation case and use the partial-table read for a future regression test.\n\n**Local verification.** From `repo/` on Node 24.22.3, each selection used `node node_modules/vitest/vitest.mjs run --maxWorkers=1 --config` followed by the arguments below. Both workerd projects used `WRANGLER_SEND_METRICS=false` and `XDG_CONFIG_HOME=../.audit-xdg`.\n\n| Config and file | Result |\n|---|---|\n| `test/vitest.config.ts test/agent-data.test.ts` | 31/31 before and after the change |\n| `test/ui/vitest.config.ts test/ui/agent-data.test.tsx` | 5/5 |\n| `test/durability/vitest.config.ts test/durability/crash.test.ts` | 3/3 |\n| `interop/vitest.config.ts interop/test/legacy-state-migration.test.ts` | 11/11 |\n\nWith `-t \"exports the caller's records\"`, temporarily making `src/attachments.ts:136` write the first slice twice passed the original test. The revised test failed at byte **1,048,576** despite the correct file length. With the writer restored, reversing physical SQLite row IDs returned file sequences `[1, 0]` and the revised test passed. The cursor experiments used `-t \"erases while an export is unread\"` and `-t \"probe a table\"`. Each filter selected one case. All temporary edits were removed. `npm run typecheck`, `git diff --check` and `git diff --exit-code -- src` passed.\n\n**Scope and limits.** `inventory.json` lists 155 named modules at `c0a9a85c8f690eb77313b9627e3ea39cadc58968`, with 56 supplied. I sampled the alphabetically first supplied module in each of nine strata. Declaration or entry-point checks included `account-refresh-races.test.ts`, `check-live.test.mjs`, `node-runtime.check.mjs`, `company-security.node.mjs`, `test_handoff_direct.py` and `address.test.ts`. I read the Page, durability and migration modules above and inspected the Workers export, rollback and pagination cases. I traced the Settings link through `src/ui/agent-data.tsx:65`, `src/index.ts:537`, `src/agent-data-routes.ts:29` and `src/agent.ts:678`, including the Worker dispatch in `test/agent-helpers.ts:71`. The three supplied CI job records show successful `npm test`, interop grid and action-pin checks on the full pinned checkout. Local execution of the revised tree covers the listed selections.\n",
      "patch": "diff --git a/test/agent-data.test.ts b/test/agent-data.test.ts\nindex a467716..7e2e28f 100644\n--- a/test/agent-data.test.ts\n+++ b/test/agent-data.test.ts\n@@ -79,8 +79,12 @@ describe(\"personal data controls\", () => {\n     await tool(a, \"poppy_status\", {}); // Initialize the lazily owned Company store.\n     await a.stub.poppySql(\"INSERT INTO poppy_accounts (issuer, account, token, scope, expires_at, updated_at) VALUES ('https://auth.example', 'account', 'SEALED_REFRESH_CREDENTIAL', '', NULL, 1)\");\n     const bytes = new Uint8Array(2 * 1024 * 1024);\n+    // The pattern continues across the 1 MiB boundary, so replaying the first chunk changes the file.\n+    for (let index = 0; index < bytes.length; index++) bytes[index] = index % 251;\n     bytes.set([0xff, 0xd8, 0xff]);\n-    await a.stub.attach(a.identity, \"photo.jpg\", bytes.buffer, null);\n+    const preview = Uint8Array.of(0xff, 0xd8, 0xff, 0xa9, 0x00);\n+    const photo = await a.stub.attach(a.identity, \"photo.jpg\", bytes.buffer, preview.buffer);\n+    if (!photo.ok) throw new Error(photo.error);\n     const response = await fetchWorker(request(a.cookie));\n     expect(response.status).toBe(200);\n     expect(response.headers.get(\"Cache-Control\")).toBe(\"no-store\");\n@@ -94,8 +98,23 @@ describe(\"personal data controls\", () => {\n     expect(text).not.toContain(\"SEALED_REFRESH_CREDENTIAL\");\n     expect(data.tables.poppy_accounts[0].token).toEqual({ omitted: \"credential\" });\n     expect(data.tables.model_keys).toBeUndefined();\n-    expect(data.tables.attachment_chunks).toHaveLength(2);\n-    expect(data.tables.attachment_chunks[0].bytes).toMatchObject({ encoding: \"base64\" });\n+    const chunks: { id: string; part: string; seq: number; bytes: { encoding: string; data: string } }[] = data.tables.attachment_chunks;\n+    expect(chunks).toHaveLength(3);\n+    for (const [part, original, count] of [[\"file\", bytes, 2], [\"preview\", preview, 1]] as const) {\n+      const rows = chunks\n+        .filter(row => row.id === photo.attachment.id && row.part === part)\n+        .sort((left, right) => left.seq - right.seq);\n+      expect(rows, part).toHaveLength(count);\n+      expect(new Set(rows.map(row => row.seq)).size, part).toBe(count);\n+      for (const row of rows) {\n+        expect(row.seq).toBeTypeOf(\"number\");\n+        expect(row.bytes.encoding).toBe(\"base64\");\n+      }\n+      const decoded = rows.map(row => atob(row.bytes.data)).join(\"\");\n+      expect(decoded.length, part).toBe(original.length);\n+      const mismatch = original.findIndex((byte, index) => byte !== decoded.charCodeAt(index));\n+      expect(mismatch, `first differing byte of the exported ${part}`).toBe(-1);\n+    }\n     expect((await fetchWorker(request(\"\"))).status).toBe(401);\n   });\n \n",
      "observed_behavior": {
        "candidate_id": "d3dfc73ed6d4ddba",
        "repository": "adewale/pda",
        "source_commit": "c0a9a85c8f690eb77313b9627e3ea39cadc58968",
        "patch_file": "patch.diff",
        "patch_sha256": "7115be8cf41aadafad1a8b917f62534d5d98c660ad7b7063e65d2c4c9489c203",
        "enrollment": {
          "changed_files": [
            "test/agent-data.test.ts"
          ],
          "added_test_files": [],
          "added_named_cases": 0,
          "selection": "One existing Workers test was strengthened in place. The frozen runner enrolled its complete 31-case module. The separate client-upload module ran all 14 cases on clean. Keeper test names stayed intact.",
          "workers_file": "test/agent-data.test.ts",
          "ui_file": "test/ui/attachments.test.tsx",
          "fault_failure_case": "personal data controls exports the caller's records and chunked photos without stored credentials or another person's records",
          "candidate_production_changes": false
        },
        "frozen_comparison": {
          "count_order": [
            "passed",
            "failed",
            "filtered_out"
          ],
          "variants": {
            "clean": [
              {
                "project": "Workers",
                "original": [
                  31,
                  0,
                  0
                ],
                "submitted": [
                  31,
                  0,
                  0
                ],
                "exit": 0
              },
              {
                "project": "UI",
                "original": [
                  14,
                  0,
                  0
                ],
                "submitted": [
                  14,
                  0,
                  0
                ],
                "exit": 0
              }
            ],
            "empty-data": [
              {
                "project": "Workers",
                "original": [
                  31,
                  0,
                  0
                ],
                "submitted": [
                  30,
                  1,
                  0
                ],
                "exit": 1,
                "failed_assertion": "AssertionError: file: expected +0 to be 2097152 // Object.is equality"
              }
            ],
            "tail-bit": [
              {
                "project": "Workers",
                "original": [
                  31,
                  0,
                  0
                ],
                "submitted": [
                  30,
                  1,
                  0
                ],
                "exit": 1,
                "failed_assertion": "AssertionError: first differing byte of the exported file: expected 2097151 to be -1 // Object.is equality"
              }
            ],
            "physical-order": [
              {
                "project": "Workers",
                "original": [
                  31,
                  0,
                  0
                ],
                "submitted": [
                  31,
                  0,
                  0
                ],
                "exit": 0
              }
            ],
            "member-order": [
              {
                "project": "Workers",
                "original": [
                  31,
                  0,
                  0
                ],
                "submitted": [
                  31,
                  0,
                  0
                ],
                "exit": 0
              }
            ],
            "auth-keeper": [
              {
                "project": "Workers",
                "original": [
                  0,
                  1,
                  30
                ],
                "submitted": [
                  0,
                  1,
                  30
                ],
                "exit": 1,
                "failed_assertion": "AssertionError: expected 200 to be 401 // Object.is equality"
              }
            ],
            "isolation-keeper": [
              {
                "project": "Workers",
                "original": [
                  0,
                  1,
                  30
                ],
                "submitted": [
                  0,
                  1,
                  30
                ],
                "exit": 1,
                "failed_assertion": "AssertionError: expected '{\"format\":\"pda-personal-data\",\"versio…' not to contain 'SOMEONE_ELSES_NOTE'"
              }
            ],
            "upload-byte-keeper": [
              {
                "project": "UI",
                "original": [
                  0,
                  1,
                  13
                ],
                "submitted": [
                  0,
                  1,
                  13
                ],
                "exit": 1,
                "failed_assertion": "AssertionError: expected [ +0, +0, +0, +0, +0, +0 ] to deeply equal [ 255, 216, 255, 224, 18, 52 ]"
              }
            ]
          },
          "raw": "pda.json",
          "original_raw": "preparation/pda/evaluator/evidence/pinned.json"
        },
        "source_review": {
          "boundary": "The changed test uploads through the PersonalAgent Durable Object, downloads the authenticated HTTP export, groups by the actual attachment ID and part, sorts by seq, decodes each base64 field and compares every byte with the input. The 2 MiB JPEG fixture has distinct 1 MiB chunks and a separate 5-byte preview. The same test asserts both payload comparisons on clean.",
          "keeper_evidence": "The frozen response-status, isolation-sentinel and same-size client-upload substitutions still fail at their intended assertions. The original owner note, credential masking/omission, and response-header assertions are also retained and pass on clean. No separate credential-substitution probe was registered.",
          "boundedness": "The test retains exact stored-chunk counts, now two file rows and one preview row. pda-spec.md:230 describes 1 MiB storage rows. Compatibility with a different export chunk size was not tested. The frozen faults independently establish file-content detection; a preview-only corruption was not separately injected.",
          "links": [
            "test/agent-data.test.ts:83",
            "test/agent-data.test.ts:101",
            "test/agent-data.test.ts:118",
            "src/agent.ts:825",
            "src/agent-data-routes.ts:29",
            "src/agent-data-export.ts:130",
            "test/ui/attachments.test.tsx:128",
            "pda-spec.md:230"
          ]
        },
        "secondary_finding": {
          "kind": "Known pda-03, reported and left outside the submitted patch.",
          "source_evidence": "The HTTP test reads once on each stream, cancels one, and asks for deletion. The generator yields the JSON header before the first row query, then materializes batches with toArray(). Production erasure drops application tables inside a synchronous transaction.",
          "references": [
            "test/agent-data.test.ts:365 (submitted line numbers)",
            "src/agent-data-export.ts:129",
            "src/agent-data-export.ts:139",
            "src/agent-data.ts:75",
            "src/agent-data.ts:78"
          ],
          "exploratory_validation": "After submission, two real-workerd selections compared pinned production to a live-cursor perturbation in scratch with the unchanged HTTP test and a separate probe that pauses after the first of five SQLite rows. These runs are independent of the eight frozen comparisons and do not constitute a second submitted repair.",
          "observed": {
            "pinned": {
              "original_http_case": "passed",
              "new_partial_table_probe": "passed",
              "passed": 2,
              "failed": 0,
              "skipped_by_filter": 30,
              "exit": 0
            },
            "live-cursor": {
              "original_http_case": "passed",
              "new_partial_table_probe": "failed",
              "passed": 1,
              "failed": 1,
              "skipped_by_filter": 30,
              "exit": 1,
              "failure": "Error: database table is locked: SQLITE_LOCKED"
            }
          },
          "raw": "cursor-exploratory.json",
          "reproduce": "cursor-exploratory.py"
        },
        "limits": [
          "Local original suite inventory is 155 named modules; 56 complete modules were supplied. The native controls support claims about their selected files. They do not certify the full Workers or full CI suite.",
          "Other cited selections (the page settings, durability and legacy-migration files), first-slice duplication experiment, typecheck and original authoring process were subject-reported. The evaluator verified the sealed diff and ran the frozen controls; it does not have a subject-wide tool trace."
        ]
      }
    },
    {
      "id": "182d32db20b7d6f8",
      "disposition": "returned",
      "response_source": "submitted file",
      "raw_response": "# PDA test audit\n\n**1. The dollar cap masked a separate limit on unresolved calls.** PDA allows at most two unresolved demo calls per person per UTC day. The existing overlap test exhausts the $1 allowance before requesting a third call, so it still passes if the ledger admits three. The production agent gives its SQLite ledger to the router, which checks local admission before provider dispatch and records any smaller reservation granted by the shared domain. See `pda-spec.md:249`, `src/agent.ts:202`, `src/model-router.ts:387`, `src/model-router.ts:403` and `test/budget.test.ts:141`.\n\nAdded a workerd test at `test/budget.test.ts:166`. It supplies a $0.25 partial grant through the ledger API, admits a second call, evicts the Durable Object and verifies that the third call is refused with $0.25 still available. Settling the first call opens a slot, and the next UTC day has its own allowance. Existing checks cover competing shared reservations, replay after a lost settlement response, and charging a background summary (`test/budget.test.ts:42`, `test/budget.test.ts:74`, `test/compaction.test.ts:233`).\n\n**2. The overlap test can stall on slow dispatch.** After 100 one-millisecond polls, its diagnostic awaits a stream that the test completes later. The dispatch promise in the sibling key-generation test shows how to wait for the event directly. This risk came from inspection. The overlap test passed locally. See `test/budget.test.ts:133`, `test/budget.test.ts:151` and `test/model-key-generation.test.ts:25`.\n\n**Local validation** used Node 24.22.3 with Wrangler metrics disabled.\n\n```sh\nnode node_modules/vitest/vitest.mjs run --maxWorkers=1 --config test/vitest.config.ts test/budget.test.ts\nnode node_modules/vitest/vitest.mjs run --maxWorkers=1 --config test/vitest.config.ts test/compaction.test.ts\nnpm run typecheck\ngit diff --check\n```\n\nBudget passed 8/8 before the patch and 9/9 after. In an isolated copy, changing `>= 2` to `> 2` at `src/budget.ts:108` passed all eight original tests. With the patch, only the new case failed (exit 1) because it received a $0.25 reservation where it expected `null`. Restoring the source byte-for-byte returned 9/9. The scratch copy was removed. Compaction passed 18/18. Typecheck and diff check exited 0.\n\n**Scope.** The supplied CI job recorded a successful full-checkout `npm test` on main at `c0a9a85c`, before this patch (`.github/workflows/ci.yml:66`, `scripts/test-projects.mjs:2`, `ci/jobs-45800972889.json`). Local execution covered the two named Workers files. The inventory supplied 56 of 155 named modules and omitted both `test/model-access.test.ts` and `test/properties/budget.test.ts`.\n",
      "patch": "diff --git a/test/budget.test.ts b/test/budget.test.ts\nindex d7c0413..fc2587d 100644\n--- a/test/budget.test.ts\n+++ b/test/budget.test.ts\n@@ -163,6 +163,30 @@ describe(\"durable model admission and accounting\", () => {\n     });\n   });\n \n+  it(\"counts a partial reservation toward the day's two unresolved calls after eviction\", async () => {\n+    const probe = probes.get(probes.newUniqueId());\n+    const domain = \"partial.example\";\n+    const first = await runInDurableObject(probe, (_, state) => {\n+      const ledger = new Ledger(state.storage.sql);\n+      const call = ledger.begin(DAY, domain, 1)!;\n+      // The domain granted only $0.25 of the first call's requested $0.50.\n+      const partial = ledger.reserve(call, 0.25);\n+      expect(ledger.begin(DAY, domain, 1)?.reservedUsd).toBe(0.5);\n+      return partial;\n+    });\n+\n+    await evictDurableObject(probe);\n+    await runInDurableObject(probe, (_, state) => {\n+      const ledger = new Ledger(state.storage.sql);\n+      expect(ledger.spent(DAY)).toBe(0.75);\n+      expect(ledger.begin(DAY, domain, 1)).toBeNull();\n+\n+      ledger.complete(first, 0.125);\n+      expect(ledger.begin(DAY, domain, 1)?.reservedUsd).toBe(0.375);\n+      expect(ledger.begin(NEXT_DAY, domain, 1)?.reservedUsd).toBe(0.5);\n+    });\n+  });\n+\n   it(\"recovers a committed local outbox after the agent's own Durable Object is evicted\", async () => {\n     const domainName = `budget-test-${crypto.randomUUID()}`;\n     const domain = testEnv.DomainBudget.getByName(domainName);\n",
      "observed_behavior": {
        "candidate_id": "991af762de5e1244",
        "repository": "adewale/pda",
        "source_commit": "c0a9a85c8f690eb77313b9627e3ea39cadc58968",
        "patch_file": "patch.diff",
        "patch_sha256": "02d68bb2d41b4e325a38c9593b3d5f9928de98f208149bf856d2306c01f615be",
        "enrollment": {
          "changed_files": [
            "test/budget.test.ts"
          ],
          "added_test_files": [],
          "added_named_cases": 1,
          "added_case": "durable model admission and accounting counts a partial reservation toward the day's two unresolved calls after eviction",
          "workers_file": "test/budget.test.ts",
          "unchanged_photo_owner": "test/agent-data.test.ts",
          "ui_file": "test/ui/attachments.test.tsx",
          "candidate_production_changes": false,
          "selection": "One 24-line addition between two preexisting cases. The frozen runner enrolled the 31-case photo owner and all nine budget cases on the five main controls. All 14 client-upload cases ran on clean. The three keeper controls selected their original named cases."
        },
        "frozen_comparison": {
          "count_order": [
            "passed",
            "failed",
            "filtered_out"
          ],
          "variants": {
            "clean": [
              {
                "project": "Workers",
                "original": [
                  31,
                  0,
                  0
                ],
                "submitted": [
                  40,
                  0,
                  0
                ],
                "original_files": [
                  "test/agent-data.test.ts"
                ],
                "submitted_files": [
                  "test/agent-data.test.ts",
                  "test/budget.test.ts"
                ],
                "original_exit": 0,
                "exit": 0,
                "selected_name_filter": null
              },
              {
                "project": "UI",
                "original": [
                  14,
                  0,
                  0
                ],
                "submitted": [
                  14,
                  0,
                  0
                ],
                "original_files": [
                  "test/ui/attachments.test.tsx"
                ],
                "submitted_files": [
                  "test/ui/attachments.test.tsx"
                ],
                "original_exit": 0,
                "exit": 0,
                "selected_name_filter": null
              }
            ],
            "empty-data": [
              {
                "project": "Workers",
                "original": [
                  31,
                  0,
                  0
                ],
                "submitted": [
                  40,
                  0,
                  0
                ],
                "original_files": [
                  "test/agent-data.test.ts"
                ],
                "submitted_files": [
                  "test/agent-data.test.ts",
                  "test/budget.test.ts"
                ],
                "original_exit": 0,
                "exit": 0,
                "selected_name_filter": null
              }
            ],
            "tail-bit": [
              {
                "project": "Workers",
                "original": [
                  31,
                  0,
                  0
                ],
                "submitted": [
                  40,
                  0,
                  0
                ],
                "original_files": [
                  "test/agent-data.test.ts"
                ],
                "submitted_files": [
                  "test/agent-data.test.ts",
                  "test/budget.test.ts"
                ],
                "original_exit": 0,
                "exit": 0,
                "selected_name_filter": null
              }
            ],
            "physical-order": [
              {
                "project": "Workers",
                "original": [
                  31,
                  0,
                  0
                ],
                "submitted": [
                  40,
                  0,
                  0
                ],
                "original_files": [
                  "test/agent-data.test.ts"
                ],
                "submitted_files": [
                  "test/agent-data.test.ts",
                  "test/budget.test.ts"
                ],
                "original_exit": 0,
                "exit": 0,
                "selected_name_filter": null
              }
            ],
            "member-order": [
              {
                "project": "Workers",
                "original": [
                  31,
                  0,
                  0
                ],
                "submitted": [
                  40,
                  0,
                  0
                ],
                "original_files": [
                  "test/agent-data.test.ts"
                ],
                "submitted_files": [
                  "test/agent-data.test.ts",
                  "test/budget.test.ts"
                ],
                "original_exit": 0,
                "exit": 0,
                "selected_name_filter": null
              }
            ],
            "auth-keeper": [
              {
                "project": "Workers",
                "original": [
                  0,
                  1,
                  30
                ],
                "submitted": [
                  0,
                  1,
                  30
                ],
                "original_files": [
                  "test/agent-data.test.ts"
                ],
                "submitted_files": [
                  "test/agent-data.test.ts"
                ],
                "original_exit": 1,
                "exit": 1,
                "selected_name_filter": "exports the caller's records and chunked photos",
                "failed_case": "personal data controls exports the caller's records and chunked photos without stored credentials or another person's records",
                "failed_assertion": "AssertionError: expected 200 to be 401 // Object.is equality",
                "location": "at /work/test/agent-data.test.ts:99:53"
              }
            ],
            "isolation-keeper": [
              {
                "project": "Workers",
                "original": [
                  0,
                  1,
                  30
                ],
                "submitted": [
                  0,
                  1,
                  30
                ],
                "original_files": [
                  "test/agent-data.test.ts"
                ],
                "submitted_files": [
                  "test/agent-data.test.ts"
                ],
                "original_exit": 1,
                "exit": 1,
                "selected_name_filter": "exports the caller's records and chunked photos",
                "failed_case": "personal data controls exports the caller's records and chunked photos without stored credentials or another person's records",
                "failed_assertion": "AssertionError: expected '{\"format\":\"pda-personal-data\",\"versio…' not to contain 'SOMEONE_ELSES_NOTE'",
                "location": "at /work/test/agent-data.test.ts:92:22"
              }
            ],
            "upload-byte-keeper": [
              {
                "project": "UI",
                "original": [
                  0,
                  1,
                  13
                ],
                "submitted": [
                  0,
                  1,
                  13
                ],
                "original_files": [
                  "test/ui/attachments.test.tsx"
                ],
                "submitted_files": [
                  "test/ui/attachments.test.tsx"
                ],
                "original_exit": 1,
                "exit": 1,
                "selected_name_filter": "sends a picked photo to the User's own agent",
                "failed_case": "attaching a photo in the composer sends a picked photo to the User's own agent, shows it, and names it in the message by its marker",
                "failed_assertion": "AssertionError: expected [ +0, +0, +0, +0, +0, +0 ] to deeply equal [ 255, 216, 255, 224, 18, 52 ]",
                "location": "at /work/test/ui/attachments.test.tsx:128:70"
              }
            ]
          },
          "raw": "pda.json",
          "raw_sha256": "63a7bdbb2f633ec4045468124e15902785ff2caba4516f1b174fd1726c651ed7",
          "command_log": "pda-commands.log",
          "command_log_sha256": "99b48cde66f1aeb5cfb0496f4f036e1a42b3894414664a1af30477f034643364",
          "original_raw": {
            "path": "preparation/pda/evaluator/evidence/pinned.json",
            "sha256": "d7e8b02ae4dcd02e7ee93c4d4e2e0387c41c8005570f0186470b758ba79dab74"
          },
          "validation": "All eight named variants were already present. Their recorded exits, actual names, assertion counts, selected files and three corresponding failures were checked against the pinned report. This assessment reuses the retained raw evidence and its recorded hash.",
          "photo_faults": {
            "empty_data_detected": false,
            "tail_bit_detected": false,
            "physical_order_accepted": true,
            "member_order_accepted": true,
            "photo_owner_case": "personal data controls exports the caller's records and chunked photos without stored credentials or another person's records"
          },
          "preserved": "All pinned enrollment and results for the photo-owner and browser modules match. The 401, second-person sentinel and exact upload bytes failed in their original tests for their original reasons. The unchanged redaction and no-store assertions ran on clean. Their evidence is source inspection and the clean run."
        },
        "alternate_repair": {
          "route": "The frozen scoring instructions allow a different demonstrated repair. The unresolved-call finding, its specific mutants, permitted SQL change and independent reachability witness were selected after submission and are exploratory. They are separate from the frozen photo comparison and from the preregistered waiver example.",
          "case": "durable model admission and accounting counts a partial reservation toward the day's two unresolved calls after eviction",
          "expected_contract": "At most two unresolved demo admissions in a person's local ledger on one UTC admission day, independently of remaining dollars. Known usage settles its slot. An independent day has room for new admissions.",
          "original_blind_spot": "The existing routed overlap test starts with 0.10 in the local ledger, reaches 1.00 after the second reservation, and observes a refusal. The monetary preflight alone can explain that observation. All eight original budget cases accepted the controlled relaxation of the two-call count.",
          "changed_test_boundary": "The sealed case constructs production Ledger with workerd SQLite, uses its public begin/reserve/complete methods, and evicts the real test StorageProbe before reconstructing the ledger. It supplies the smaller shared grant at the API boundary, supplies both UTC day keys explicitly, and compares public results to fixed dollar values. A router, live shared RPC, advancing clock and vendor are outside this new case.",
          "expected_arithmetic": "Within a 1.00 personal allowance, unresolved amounts of 0.25 and 0.50 total 0.75. The third call must be refused with 0.25 still available. A known first cost of 0.125 gives 0.625 used and opens a 0.375 reservation. A fresh day supports a 0.50 reservation.",
          "actual_fault": "The exact same copies of src/budget.ts relaxed the two-call guard by one. On the sealed test file, only the new third-call assertion at line 182 failed. Vitest prints a four-field object in place of null. Its 0.25 reservation is inferred from the preceding passing 0.75 spend assertion and the unchanged min(remaining, cap/2) calculation. All eight original identities passed on the same fault.",
          "relevant_keeper": "The opposite change restricts the allowance to one unresolved call. The original routed overlap test fails at the second dispatch, and the added case also fails when the second local reservation is missing. Original cases for partial shared capacity, durable settlement replay, unknown usage and admission-day charging remain present; the compaction cost case passed on clean.",
          "allowed_private_change": "A bounded subquery counts no more than two unresolved rows. Saturating at two has the same observable decision for every nonnegative integer count at this guard. Both complete budget files accepted the implementation.",
          "controls": {
            "original-clean": {
              "attempt": 3,
              "source_sha256": "8af041579f1bd1b4ba9c1353b203d585576a89d4a3cf3a9bb4703e0f259a255f",
              "budget_test_sha256": "4e526214e15d9dd8ca011e9a43bb8bccc96facf7e0ef53ba996208df93e3a6a2",
              "results": [
                {
                  "files": [
                    "test/budget.test.ts"
                  ],
                  "counts": [
                    8,
                    0,
                    0
                  ],
                  "exit": 0,
                  "failed_assertions": []
                }
              ]
            },
            "candidate-clean": {
              "attempt": 4,
              "source_sha256": "8af041579f1bd1b4ba9c1353b203d585576a89d4a3cf3a9bb4703e0f259a255f",
              "budget_test_sha256": "c989a6273a9590cb72114476ab9173b296c3eebec2bcde7a4925f29501ac9dd3",
              "results": [
                {
                  "files": [
                    "test/budget.test.ts"
                  ],
                  "counts": [
                    9,
                    0,
                    0
                  ],
                  "exit": 0,
                  "failed_assertions": []
                },
                {
                  "files": [
                    "test/compaction.test.ts"
                  ],
                  "counts": [
                    18,
                    0,
                    0
                  ],
                  "exit": 0,
                  "failed_assertions": []
                }
              ]
            },
            "original-off-by-one": {
              "attempt": 1,
              "source_sha256": "9633aeb3034858a0d5bfeb5a7dda73919ef432149af5c84f788d0cd494d6f71a",
              "budget_test_sha256": "4e526214e15d9dd8ca011e9a43bb8bccc96facf7e0ef53ba996208df93e3a6a2",
              "results": [
                {
                  "files": [
                    "test/budget.test.ts"
                  ],
                  "counts": [
                    8,
                    0,
                    0
                  ],
                  "exit": 0,
                  "failed_assertions": []
                }
              ]
            },
            "candidate-off-by-one": {
              "attempt": 2,
              "source_sha256": "9633aeb3034858a0d5bfeb5a7dda73919ef432149af5c84f788d0cd494d6f71a",
              "budget_test_sha256": "c989a6273a9590cb72114476ab9173b296c3eebec2bcde7a4925f29501ac9dd3",
              "results": [
                {
                  "files": [
                    "test/budget.test.ts"
                  ],
                  "counts": [
                    8,
                    1,
                    0
                  ],
                  "exit": 1,
                  "failed_assertions": [
                    {
                      "name": "durable model admission and accounting counts a partial reservation toward the day's two unresolved calls after eviction",
                      "message": "AssertionError: expected { …(4) } to be null",
                      "location": "at /work/test/budget.test.ts:182:44"
                    }
                  ]
                }
              ]
            },
            "candidate-permitted-query": {
              "attempt": 5,
              "source_sha256": "25ba4fcd435d6c37e815c6fafbc84890957533212328f4e51c4bc759054b3364",
              "budget_test_sha256": "c989a6273a9590cb72114476ab9173b296c3eebec2bcde7a4925f29501ac9dd3",
              "results": [
                {
                  "files": [
                    "test/budget.test.ts"
                  ],
                  "counts": [
                    9,
                    0,
                    0
                  ],
                  "exit": 0,
                  "failed_assertions": []
                }
              ]
            },
            "original-permitted-query": {
              "attempt": 8,
              "source_sha256": "25ba4fcd435d6c37e815c6fafbc84890957533212328f4e51c4bc759054b3364",
              "budget_test_sha256": "4e526214e15d9dd8ca011e9a43bb8bccc96facf7e0ef53ba996208df93e3a6a2",
              "results": [
                {
                  "files": [
                    "test/budget.test.ts"
                  ],
                  "counts": [
                    8,
                    0,
                    0
                  ],
                  "exit": 0,
                  "failed_assertions": []
                }
              ]
            },
            "original-stricter": {
              "attempt": 6,
              "source_sha256": "16b7c76b827f71aeb663a94718e2b0a7b66c712b1476829035b1b19f3f75276b",
              "budget_test_sha256": "4e526214e15d9dd8ca011e9a43bb8bccc96facf7e0ef53ba996208df93e3a6a2",
              "results": [
                {
                  "files": [
                    "test/budget.test.ts"
                  ],
                  "counts": [
                    7,
                    1,
                    0
                  ],
                  "exit": 1,
                  "failed_assertions": [
                    {
                      "name": "durable model admission and accounting admits two overlapping calls, refuses a third, queues notices despite holds and fixes charges to admission day",
                      "message": "AssertionError: expected false to be true // Object.is equality",
                      "location": "at /work/test/budget.test.ts:140:29"
                    }
                  ]
                }
              ]
            },
            "candidate-stricter": {
              "attempt": 7,
              "source_sha256": "16b7c76b827f71aeb663a94718e2b0a7b66c712b1476829035b1b19f3f75276b",
              "budget_test_sha256": "c989a6273a9590cb72114476ab9173b296c3eebec2bcde7a4925f29501ac9dd3",
              "results": [
                {
                  "files": [
                    "test/budget.test.ts"
                  ],
                  "counts": [
                    7,
                    2,
                    0
                  ],
                  "exit": 1,
                  "failed_assertions": [
                    {
                      "name": "durable model admission and accounting admits two overlapping calls, refuses a third, queues notices despite holds and fixes charges to admission day",
                      "message": "AssertionError: expected false to be true // Object.is equality",
                      "location": "at /work/test/budget.test.ts:140:29"
                    },
                    {
                      "name": "durable model admission and accounting counts a partial reservation toward the day's two unresolved calls after eviction",
                      "message": "AssertionError: expected undefined to be 0.5 // Object.is equality",
                      "location": "at /work/test/budget.test.ts:174:57"
                    }
                  ]
                }
              ]
            },
            "reachability": {
              "attempt": 9,
              "source_sha256": "8af041579f1bd1b4ba9c1353b203d585576a89d4a3cf3a9bb4703e0f259a255f",
              "budget_test_sha256": "4e526214e15d9dd8ca011e9a43bb8bccc96facf7e0ef53ba996208df93e3a6a2",
              "results": [
                {
                  "files": [
                    "test/controller-budget-reachability.test.ts"
                  ],
                  "counts": [
                    0,
                    1,
                    0
                  ],
                  "exit": 1,
                  "failed_assertions": [
                    {
                      "name": "can reach two unequal local holds through the shared budget and refuses the next call before dispatch",
                      "message": "AssertionError: expected { dispatched: false, …(3) } to deeply equal { dispatched: true, …(3) }",
                      "location": "at /work/test/controller-budget-reachability.test.ts:57:34"
                    }
                  ]
                }
              ]
            },
            "reachability-context": {
              "attempt": 10,
              "source_sha256": "8af041579f1bd1b4ba9c1353b203d585576a89d4a3cf3a9bb4703e0f259a255f",
              "budget_test_sha256": "4e526214e15d9dd8ca011e9a43bb8bccc96facf7e0ef53ba996208df93e3a6a2",
              "results": [
                {
                  "files": [
                    "test/controller-budget-reachability.test.ts"
                  ],
                  "counts": [
                    1,
                    0,
                    0
                  ],
                  "exit": 0,
                  "failed_assertions": []
                },
                {
                  "files": [
                    "test/controller-budget-reachability-diagnostic.test.ts"
                  ],
                  "counts": [
                    0,
                    1,
                    0
                  ],
                  "exit": 1,
                  "failed_assertions": [
                    {
                      "name": "can reach two unequal local holds through the shared budget and refuses the next call before dispatch",
                      "message": "Error: Router failed before a budget refusal: Cannot perform I/O on behalf of a different Durable Object. I/O objects (such as streams, request/response bodies, and others) created in the context of one Durable Object cannot be accessed from a different Durable Object in the same isolate. This is a limitation of Cloudflare Workers which allows us to improve overall performance. (I/O type: OutgoingFactory)",
                      "location": "at /work/test/controller-budget-reachability-diagnostic.test.ts:52:42"
                    }
                  ]
                }
              ]
            }
          },
          "original_budget_case_identities": [
            "durable model admission and accounting admits two overlapping calls, refuses a third, queues notices despite holds and fixes charges to admission day",
            "durable model admission and accounting atomically reserves shared room, is idempotent, and retains unknown liabilities after eviction",
            "durable model admission and accounting does not admit invalid amounts or settle without an admission",
            "durable model admission and accounting does not invoke the provider when shared admission commits but its reply is lost",
            "durable model admission and accounting keeps a settlement outbox across local reconstruction and an applied RPC whose response was lost",
            "durable model admission and accounting preserves caller output settings on the gateway wire without a fleet output policy",
            "durable model admission and accounting recovers a committed local outbox after the agent's own Durable Object is evicted",
            "durable model admission and accounting retains admission liability when a provider reports aborted zero usage"
          ],
          "attempt_count": 10,
          "compaction_keeper": "compaction counts a summary's cost against the demo's caps, like any other call",
          "raw": {
            "path": "controller/outputs/991af762de5e1244/budget-runs.ndjson",
            "sha256": "04561d9fd5cde2cc30075062aa54ba3c4122f17aa1186854eb0257eca07c10ed"
          },
          "reproduce": "python -B controller/outputs/991af762de5e1244/budget-controls.py",
          "label": "Exploratory native verification after the submission was sealed"
        },
        "fixture_provenance": {
          "installed_path": "The agent constructs ModelAccess with its own SQLite Ledger and selects the shared DomainBudget by domain. The router's daily preflight reads both budgets, begins the local hold, requests up to that amount from DomainBudget, records the exact granted amount locally, and only then invokes its callback. DomainBudget.reserve returns the smaller of positive available room and the requested amount.",
          "reachability": "The repository's test configuration supplies 1.00 personal and 1.50 shared allowances. The checked-in deployment configuration uses 2 and 10, and the router reads these deployment settings. In the test configuration, other call IDs contribute one settled 0.25 and two open 0.50 reservations. The first owner's 0.50 request gets 0.25, filling the shared domain. Both other holds subsequently settle for 0.125 each, reopening 0.75 of shared room. A second 0.50 owner hold leaves 0.25 free both locally and in the domain before the third request.",
          "runtime": "A separate evaluator-authored test on unmodified production code used the real shared Durable Object RPC, production ModelAccess, real owner SQLite and a synthetic provider callback reporting aborted zero-usage responses. Both holds persisted. After owner eviction, the router returned user_cap before calling the callback on the third request; shared spend stayed 1.25. This is fixture validation outside the candidate test. The Poppy agent constructor wiring was source-reviewed, and the external model service was not invoked.",
          "witness_case": "can reach two unequal local holds through the shared budget and refuses the next call before dispatch",
          "witness_attempt": "reachability-context, group 1",
          "witness_source": {
            "path": "controller/outputs/991af762de5e1244/budget-reachability-witness.ts",
            "sha256": "dd111807fc89f64dbb60042fd27eb6ca19b6643be343e4f36ead0cdeda82b452"
          },
          "witness_context_patch": {
            "path": "controller/outputs/991af762de5e1244/budget-reachability-context.patch",
            "sha256": "f76560d88e683cc38c9dbf650c9a625deff7ace4e724e31cb559d986647b8340"
          },
          "earlier_attempt": {
            "name": "reachability",
            "observed": "AssertionError: expected { dispatched: false, …(3) } to deeply equal { dispatched: true, …(3) }",
            "diagnostic": "Error: Router failed before a budget refusal: Cannot perform I/O on behalf of a different Durable Object. I/O objects (such as streams, request/response bodies, and others) created in the context of one Durable Object cannot be accessed from a different Durable Object in the same isolate. This is a limitation of Cloudflare Workers which allows us to improve overall performance. (I/O type: OutgoingFactory)",
            "interpretation": "The earlier evaluator witness captured an RPC stub in a different request context. A diagnostic copy surfaced its routing error. Reacquiring a stub by the same domain name inside the owning Durable Object matched the repository’s pattern. These harness results concern the evaluator witness only."
          }
        },
        "secondary_finding": {
          "kind": "Source-supported scheduling risk in the preexisting overlap test; no repair and no timed failure observed",
          "source_evidence": "After up to 100 one-millisecond sleeps, the first diagnostic awaits result. If the route dispatches late, the successful stream only finishes when this test reaches a later push, so the diagnostic can stall until the harness timeout. The existing sibling waitingCall helper uses a dispatch promise and terminates on an early result. Clean and original off-by-one checks passed the overlap case.",
          "references": [
            "test/budget.test.ts:133",
            "test/budget.test.ts:134",
            "test/budget.test.ts:151",
            "test/model-key-generation.test.ts:25"
          ]
        },
        "static_validation": {
          "raw": {
            "path": "controller/outputs/991af762de5e1244/budget-static.ndjson",
            "sha256": "b4a259dc7a987019c6ffd267cb150c9a43a9109e30740b852d6349586cada235"
          },
          "node": "v24.22.3",
          "typescript": "Version 6.0.3",
          "typecheck_exit": 0,
          "patch_check_exit": 0,
          "diff_check_exit": 0,
          "patch_applies_byte_for_byte": true
        },
        "source_provenance": {
          "immutable_snapshot": "controller/candidate-snapshots/991af762de5e1244",
          "files_compared": 560,
          "all_manifest_hashes_verified": true,
          "installed_node": "v24.22.3",
          "image": "node@sha256:49f7adaf9f1574bc45c20ea317139b39a59d7e758d0e93745e112fd85cb42623",
          "primary_sources": {
            "pda-spec.md": {
              "sha256": "313953c8faa654542d718c57acc2bbcdb9ac797417457799adbe58e021011c43",
              "lines": [
                "249"
              ]
            },
            "src/agent.ts": {
              "sha256": "06ca3ce4fc5de3bbbad07c4180d7a61f40af9468719243acc9a3720c8fe011cc",
              "lines": [
                "202-209"
              ]
            },
            "src/model-router.ts": {
              "sha256": "6d864a630eaf3242c38b9077df7fb53af9584615b9226ce1ffa9c85046cd77db",
              "lines": [
                "296-305",
                "332-335",
                "383-405",
                "454-471"
              ]
            },
            "src/budget.ts": {
              "sha256": "8af041579f1bd1b4ba9c1353b203d585576a89d4a3cf3a9bb4703e0f259a255f",
              "lines": [
                "62-83",
                "98-120",
                "128-133",
                "173-187",
                "190-196"
              ]
            },
            "test/wrangler.jsonc": {
              "sha256": "72f5f5637db135cf33b8feddcbb1c638b8dca76a89aaf5516b2b5888f7827998",
              "lines": [
                "33-34"
              ]
            },
            "wrangler.jsonc": {
              "sha256": "097023bf6d6b8b7b9e03449de5ea8cf3a7ce5cc68799fcf98038d48145ea14b1",
              "lines": [
                "53-54"
              ]
            },
            "src/config.ts": {
              "sha256": "4a63017cc69907abebcd74679c2b79b04ca282b7ea019d9bdcdb7f3f6639643b",
              "lines": [
                "136-140"
              ]
            },
            "test/budget.test.ts": {
              "sha256": "c989a6273a9590cb72114476ab9173b296c3eebec2bcde7a4925f29501ac9dd3",
              "lines": [
                "42-61",
                "74-110",
                "114-163",
                "166-188",
                "213-237"
              ]
            },
            "test/compaction.test.ts": {
              "sha256": "c5f324d147735d293dce43d87adeaba93e7b72d7622e9110366ffb55b942f2b4",
              "lines": [
                "233-250"
              ]
            },
            "test/model-key-generation.test.ts": {
              "sha256": "8097f721394bd95b413169a0126be25168bf89a0f8d5b378a1c30c9017fd7847",
              "lines": [
                "25-31"
              ]
            },
            "test/agent-data.test.ts": {
              "sha256": "b98932cc313cf0f09aaca06f7269832bcb5cfdbc2dce256238fc9adb81d8827d",
              "lines": [
                "86-99"
              ]
            },
            "test/ui/attachments.test.tsx": {
              "sha256": "3eb340117ae01a72fd65cfb50c4de11bee39e19514828ea89412531021837a28",
              "lines": [
                "111-130"
              ]
            },
            ".github/workflows/ci.yml": {
              "sha256": "ccc422eac12be941445c31c0dcd7d03a32a4b2f4a420fa0f284f7bb4380521fd",
              "lines": [
                "65-66"
              ]
            },
            "scripts/test-projects.mjs": {
              "sha256": "377f9a4000b750d430dc431d5ca796c13806a0e6d9c80f092d3c748ef10a5156",
              "lines": [
                "1-8"
              ]
            }
          },
          "evaluation_inputs": [
            {
              "path": "controller/outputs/991af762de5e1244/disposition.json",
              "sha256": "d1dee1de63a132e53fb24b7fab62bb4d431c5cccf105fdadde89cf3d4e22d7a4"
            },
            {
              "path": "controller/outputs/991af762de5e1244/response.md",
              "sha256": "7335299539015e4f187c9aa0005261af137c8c8cea9bfab4cf57af68e76b13af"
            },
            {
              "path": "controller/outputs/991af762de5e1244/patch.diff",
              "sha256": "02d68bb2d41b4e325a38c9593b3d5f9928de98f208149bf856d2306c01f615be"
            },
            {
              "path": "controller/outputs/991af762de5e1244/candidate-snapshot.json",
              "sha256": "af5d7d461233dbb8d1e06af8278376a060d6a5e0b9c4e1f17e40fd7217bea48e"
            },
            {
              "path": "controller/outputs/991af762de5e1244/budget-controls.py",
              "sha256": "32f19f231ba9879eac94499290a7e2db36f4d7844f9763cca8740620285d9bba"
            },
            {
              "path": "preparation/pda/README.md",
              "sha256": "b8d832d4788960d43d95689b6492e3f12a184f8f778b4dbef0d618018d954672"
            },
            {
              "path": "preparation/pda/evaluator/SCORING.md",
              "sha256": "75587b689d500380552df45205830caf26560018a3ca95a952229c651801ac76"
            },
            {
              "path": "preparation/pda/evaluator/case-lock.json",
              "sha256": "125f5a05b9faa3131836f0c791bc3ded0eb8d45cdaa9ce91b34a01dbf76c9550"
            },
            {
              "path": "preparation/pda/evaluator/controls.py",
              "sha256": "3913d69fb2a2c0acd28f9a114c916cd07d6e965252a275a2e6ba5fe9a99b0498"
            },
            {
              "path": "preparation/pda/evaluator/driver.mjs",
              "sha256": "973e9b56f1d4ef78436212655f675b6c19f44d2fbf3f3a64e24f29acdb02fdc9"
            },
            {
              "path": "preparation/pda/evaluator/source-manifest.json",
              "sha256": "4a89263f43ee7f16911ffda118de130898b617ccc90c7f6e1dff953024ecd11d"
            },
            {
              "path": "preparation/pda/participant/inventory.json",
              "sha256": "cf827440745efe277fb6bbe7ff389ceb30e6e39f24f8d4202c1f4b517d7e8cee"
            },
            {
              "path": "preparation/pda/participant/ci/jobs-45800972889.json",
              "sha256": "e722f0ba7943aa1af4725227e1563bd0d421ece8fc5ff34081b394df2d5cb235"
            }
          ]
        },
        "limits": [
          "The native counterfactual for the alternative covers the complete sampled budget file. The clean compaction run covers all 18 of its cases. The local results apply to these modules and the selected simulated-runtime boundaries.",
          "The source packet includes 56 of 155 named modules. test/model-access.test.ts and test/properties/budget.test.ts are explicitly omitted. Their response to the budget fault and possible other indirect coverage are unknown.",
          "The supplied Actions record reports a successful npm test step on main at the pinned commit before this patch. Coverage of the patched or fault-injected complete suite remains unknown.",
          "Exact historical subject timing, scratch-copy restoration and removal remain self-reported. The controller independently verified the sealed source and named observations."
        ]
      }
    },
    {
      "id": "c2ce50e25a8e247b",
      "disposition": "returned",
      "response_source": "submitted file",
      "raw_response": "## Findings\n\n1. **The registration test could pass while a renewed browser missed reminders.** It posted identical keys twice and counted endpoints. I extended the two-device test to post fresh laptop keys at the same endpoint between reminders. It checks for one request to that endpoint and decrypts its body as “Bins out” with the new keys. The RFC 8291 vector, first reminder’s per-device decryption and phone’s 410 cleanup still run. See `test/web-push.test.ts` lines 93, 202, 241 and 250.\n2. **Transient push failures lack a retention check.** The supplied test exercises 410 and successful delivery. A 404 removal case and a successful send after a 503 would catch a change that drops a live device or keeps an expired one. See `pda-spec.md:772`, `src/agent.ts:520` and `test/web-push.test.ts:253`.\n3. **The device-limit test follows the production constant.** It proves oldest-first eviction. Registering eleven devices and expecting the ten newest would also protect the documented limit. See `pda-spec.md:234` and `test/web-push.test.ts:218`.\n\n## Scope and verification\n\nPDA specifies that registration keeps both browser keys, that a browser posts its replacement subscription, and that notifications use that browser’s keys (`pda-spec.md` lines 149, 772–773). I traced Settings and renewal through `src/ui/notifications.tsx:69`, `public/sw.js:35`, `src/index.ts:383`, `src/agent.ts:535` and `src/web-push.ts:285`. The reminder originates at `src/schedules.ts:200`. The helper invokes the Worker at `test/agent-helpers.ts:71`, and the fake service captures ciphertext at `test/worker.ts:1287`. I also reviewed the supplied crash, approval-recovery, task-request, interop approval-delivery and UI history tests during selection.\n\nI ran these commands from `work/repo/` with Node 24.22.3.\n\n```sh\nnode node_modules/vitest/vitest.mjs run --maxWorkers=1 --config test/vitest.config.ts test/web-push.test.ts\nnode node_modules/vitest/vitest.mjs run --maxWorkers=1 --config test/ui/vitest.config.ts test/ui/workspace.test.tsx -t \"notification settings\"\nnpm run typecheck\ngit diff --check\ngit diff --exit-code -- src/web-push.ts\n```\n\nThe Workers file passed 9/9 at baseline. I temporarily changed the SQL update to keep the old `auth` while storing the new `p256dh`. The original tests still passed 9/9. With the revised test, eight passed and only renewal failed at receiver decryption on line 260. Restoring production code gave 9/9 in 12.74 seconds, including 0.904 seconds in tests. The page selection passed 4/4 with 49 filtered out. Typechecking and both Git checks passed. The final patch changes one test file, +8/−3 lines.\n\nThe snapshot supplies 56 of the inventory’s 155 named modules. The three successful hosted job records describe the original pin `c0a9a85`. Local evidence covers Worker registration through ciphertext capture and simulated receipt. Browser renewal-event dispatch and on-device display require separate evidence.\n",
      "patch": "diff --git a/test/web-push.test.ts b/test/web-push.test.ts\nindex ef7d616..1930e00 100644\n--- a/test/web-push.test.ts\n+++ b/test/web-push.test.ts\n@@ -225,7 +225,7 @@ describe(\"subscriptions\", () => {\n });\n \n describe(\"notifications\", () => {\n-  it(\"sends a due reminder to each subscribed device once, encrypted for it, with only a title and the reminder's words; a 410 deletes that subscription\", async () => {\n+  it(\"sends one reminder per device using its current keys and removes a subscription when its service returns 410\", async () => {\n     const identity = person();\n     const { stub, cookie } = await agent(identity);\n     const phone = await browser(\"https://web.push.apple.com/phone\");\n@@ -247,12 +247,17 @@ describe(\"notifications\", () => {\n       expect(JSON.parse(await device.read(request.body))).toEqual({ title: \"Reminder\", body: \"Call the bank\", tag: expect.stringMatching(/^reminder-sch_/) });\n     }\n \n-    // The phone's subscription has gone: the next reminder deletes it, and still reaches the laptop.\n+    // The laptop refreshes its keys at the same endpoint before the next reminder.\n+    const renewedLaptop = await browser(laptop.subscription.endpoint);\n+    expect((await subscribe(cookie, renewedLaptop.subscription)).status).toBe(201);\n     await stub.pushServe(phone.subscription.endpoint, 410);\n     await stub.scheduleCreate({ kind: \"reminder\", text: \"Bins out\", when: { in: \"PT2H\" }, timeZone: \"Europe/London\" });\n     await stub.scheduleAdvance(noon + 3 * 3_600_000);\n     await runDurableObjectAlarm(stub);\n-    expect((await stub.pushRequests()).slice(2).map((request) => request.url).sort()).toEqual([laptop.subscription.endpoint, phone.subscription.endpoint].sort());\n+    const next = (await stub.pushRequests()).slice(sent.length);\n+    expect(next.map((request) => request.url).sort()).toEqual([laptop.subscription.endpoint, phone.subscription.endpoint].sort());\n+    const laptopRequest = next.find((request) => request.url === renewedLaptop.subscription.endpoint)!;\n+    expect(JSON.parse(await renewedLaptop.read(laptopRequest.body))).toMatchObject({ body: \"Bins out\" });\n     expect(await endpoints(stub)).toEqual([laptop.subscription.endpoint]);\n   });\n \n",
      "observed_behavior": {
        "candidate_id": "760faa4901a0a237",
        "repository": "adewale/pda",
        "source_commit": "c0a9a85c8f690eb77313b9627e3ea39cadc58968",
        "patch_file": "patch.diff",
        "patch_sha256": "6f0cfde54f031ffda8f39d40ebbb69f56c4650570fa035023abf0588d397c385",
        "enrollment": {
          "changed_files": [
            "test/web-push.test.ts"
          ],
          "added_test_files": [],
          "added_named_cases": 0,
          "renamed_existing_cases": 1,
          "old_case": "notifications sends a due reminder to each subscribed device once, encrypted for it, with only a title and the reminder's words; a 410 deletes that subscription",
          "new_case": "notifications sends one reminder per device using its current keys and removes a subscription when its service returns 410",
          "lines_added": 8,
          "lines_removed": 3,
          "candidate_production_changes": false,
          "workers_file": "test/web-push.test.ts",
          "selection": "The patch strengthens and renames one of nine Web Push tests. The frozen runner enrolled all nine with the 31-case photo owner in every main Workers run, all 14 client attachment cases on clean, and the original name-filtered frozen keepers."
        },
        "frozen_comparison": {
          "count_order": [
            "passed",
            "failed",
            "filtered_out"
          ],
          "variants": {
            "clean": [
              {
                "project": "Workers",
                "original": [
                  31,
                  0,
                  0
                ],
                "submitted": [
                  40,
                  0,
                  0
                ],
                "original_files": [
                  "test/agent-data.test.ts"
                ],
                "submitted_files": [
                  "test/agent-data.test.ts",
                  "test/web-push.test.ts"
                ],
                "original_exit": 0,
                "exit": 0,
                "selected_name_filter": null
              },
              {
                "project": "UI",
                "original": [
                  14,
                  0,
                  0
                ],
                "submitted": [
                  14,
                  0,
                  0
                ],
                "original_files": [
                  "test/ui/attachments.test.tsx"
                ],
                "submitted_files": [
                  "test/ui/attachments.test.tsx"
                ],
                "original_exit": 0,
                "exit": 0,
                "selected_name_filter": null
              }
            ],
            "empty-data": [
              {
                "project": "Workers",
                "original": [
                  31,
                  0,
                  0
                ],
                "submitted": [
                  40,
                  0,
                  0
                ],
                "original_files": [
                  "test/agent-data.test.ts"
                ],
                "submitted_files": [
                  "test/agent-data.test.ts",
                  "test/web-push.test.ts"
                ],
                "original_exit": 0,
                "exit": 0,
                "selected_name_filter": null
              }
            ],
            "tail-bit": [
              {
                "project": "Workers",
                "original": [
                  31,
                  0,
                  0
                ],
                "submitted": [
                  40,
                  0,
                  0
                ],
                "original_files": [
                  "test/agent-data.test.ts"
                ],
                "submitted_files": [
                  "test/agent-data.test.ts",
                  "test/web-push.test.ts"
                ],
                "original_exit": 0,
                "exit": 0,
                "selected_name_filter": null
              }
            ],
            "physical-order": [
              {
                "project": "Workers",
                "original": [
                  31,
                  0,
                  0
                ],
                "submitted": [
                  40,
                  0,
                  0
                ],
                "original_files": [
                  "test/agent-data.test.ts"
                ],
                "submitted_files": [
                  "test/agent-data.test.ts",
                  "test/web-push.test.ts"
                ],
                "original_exit": 0,
                "exit": 0,
                "selected_name_filter": null
              }
            ],
            "member-order": [
              {
                "project": "Workers",
                "original": [
                  31,
                  0,
                  0
                ],
                "submitted": [
                  40,
                  0,
                  0
                ],
                "original_files": [
                  "test/agent-data.test.ts"
                ],
                "submitted_files": [
                  "test/agent-data.test.ts",
                  "test/web-push.test.ts"
                ],
                "original_exit": 0,
                "exit": 0,
                "selected_name_filter": null
              }
            ],
            "auth-keeper": [
              {
                "project": "Workers",
                "original": [
                  0,
                  1,
                  30
                ],
                "submitted": [
                  0,
                  1,
                  30
                ],
                "original_files": [
                  "test/agent-data.test.ts"
                ],
                "submitted_files": [
                  "test/agent-data.test.ts"
                ],
                "original_exit": 1,
                "exit": 1,
                "selected_name_filter": "exports the caller's records and chunked photos",
                "failed_case": "personal data controls exports the caller's records and chunked photos without stored credentials or another person's records",
                "failed_assertion": "AssertionError: expected 200 to be 401 // Object.is equality",
                "location": "at /work/test/agent-data.test.ts:99:53"
              }
            ],
            "isolation-keeper": [
              {
                "project": "Workers",
                "original": [
                  0,
                  1,
                  30
                ],
                "submitted": [
                  0,
                  1,
                  30
                ],
                "original_files": [
                  "test/agent-data.test.ts"
                ],
                "submitted_files": [
                  "test/agent-data.test.ts"
                ],
                "original_exit": 1,
                "exit": 1,
                "selected_name_filter": "exports the caller's records and chunked photos",
                "failed_case": "personal data controls exports the caller's records and chunked photos without stored credentials or another person's records",
                "failed_assertion": "AssertionError: expected '{\"format\":\"pda-personal-data\",\"versio…' not to contain 'SOMEONE_ELSES_NOTE'",
                "location": "at /work/test/agent-data.test.ts:92:22"
              }
            ],
            "upload-byte-keeper": [
              {
                "project": "UI",
                "original": [
                  0,
                  1,
                  13
                ],
                "submitted": [
                  0,
                  1,
                  13
                ],
                "original_files": [
                  "test/ui/attachments.test.tsx"
                ],
                "submitted_files": [
                  "test/ui/attachments.test.tsx"
                ],
                "original_exit": 1,
                "exit": 1,
                "selected_name_filter": "sends a picked photo to the User's own agent",
                "failed_case": "attaching a photo in the composer sends a picked photo to the User's own agent, shows it, and names it in the message by its marker",
                "failed_assertion": "AssertionError: expected [ +0, +0, +0, +0, +0, +0 ] to deeply equal [ 255, 216, 255, 224, 18, 52 ]",
                "location": "at /work/test/ui/attachments.test.tsx:128:70"
              }
            ]
          },
          "raw": "pda.json",
          "raw_sha256": "7534369e3392e0e34406ffb57b16d51124e543701a991b035ec0f32d1508e380",
          "command_log": {
            "path": "controller/outputs/760faa4901a0a237/pda-commands.log",
            "sha256": "99b48cde66f1aeb5cfb0496f4f036e1a42b3894414664a1af30477f034643364"
          },
          "original_raw": {
            "path": "preparation/pda/evaluator/evidence/pinned.json",
            "sha256": "d7e8b02ae4dcd02e7ee93c4d4e2e0387c41c8005570f0186470b758ba79dab74"
          },
          "verification": "The sealed candidate was run under all eight frozen variants. The unchanged photo owner and client-upload files matched every pinned case identity and outcome for their selections. The changed Web Push module contributed nine passes on each main variant.",
          "photo_faults": {
            "empty_data_detected": false,
            "tail_bit_detected": false,
            "physical_order_accepted": true,
            "member_order_accepted": true,
            "owner_case": "personal data controls exports the caller's records and chunked photos without stored credentials or another person's records"
          },
          "preservation": "401, second-person isolation and client upload-byte checks failed for their original reasons. The unchanged no-store and credential-redaction checks passed clean. Their evidence is the source and clean path."
        },
        "alternate_repair": {
          "route": "The frozen scoring instructions permit a different demonstrated repair. The renewal fault, private SQL update and cleanup keeper here are exploratory controls chosen after the report was sealed. They do not enter the frozen photo or optional waiver metrics.",
          "case": "notifications sends one reminder per device using its current keys and removes a subscription when its service returns 410",
          "original_case": "notifications sends a due reminder to each subscribed device once, encrypted for it, with only a title and the reminder's words; a 410 deletes that subscription",
          "contract": "For repeat registration at the same endpoint, the new subscription replaces both receiver key fields. A later due reminder must be readable by that receiver. The persisted endpoint stays unique and the other device remains independently addressable.",
          "original_blind_spot": "The original registration test posts the same endpoint with identical keys twice and counts one row. The original notification test decrypts the first reminder for both devices, then checks the destinations and the phone's removal after a 410. It never changes the laptop keys or reads the second laptop ciphertext.",
          "candidate_observation": "The strengthened test registers a second generated laptop subscription at the same URL, requires HTTP 201, records exactly one new outbound request per device, and independently decrypts the laptop's captured bytes with the renewed receiver. It compares the parsed body to the separate scheduled input, Bins out. The second assertion checks the body; the first delivery retains the full title/body/tag check.",
          "paired_result": "Both tests ran against the same production-source SHA with the update of auth on endpoint conflict omitted. The complete original module passed all nine cases. Only the revised reminder case failed in the candidate. The capture, exact destination multiplicity, registration status and first two successful receiver decryptions all precede that failure.",
          "failed_case": "notifications sends one reminder per device using its current keys and removes a subscription when its service returns 410",
          "observed_failure": "OperationError: Decryption failed. This could be due to a ciphertext authentication failure, bad padding, incorrect CryptoKey, or another algorithm-specific reason. Input length was 71, output length expected to be 71 for AES-GCM\n    at decrypt (/work/test/web-push.test.ts:61:53)\n    at /work/test/web-push.test.ts:260:23\n    at work/node_modules/@vitest/runner/dist/chunk-artifact.js:1903:20",
          "correct_clean_web_push": {
            "source": "pda.json -> variants.clean.results[0]",
            "passed": 9,
            "failed": 0,
            "filtered_out": 0
          },
          "allowed_private_change": "The equivalent SQLite tuple assignment updates both columns from the incoming row. It preserves the endpoint identity, original creation time, phone cleanup and receiver-visible payload. The whole candidate Web Push module passed.",
          "keeper_controls": {
            "rfc_vector_case": "message encryption (RFC 8291) encrypts RFC 8291's example to the exact message in its section 5, from the keys and salt in Appendix A",
            "known_answer_evidence": "The original deterministic RFC 8291 example still checks exact header, ciphertext and full message, then decodes the RFC's own fixed ciphertext to its specified plaintext. It passes on clean, on the stale-auth mutation and on the equivalent tuple assignment.",
            "first_reminder_evidence": "Both original devices still receive exactly one request; each device's independently held private key decrypts the expected complete first reminder. The existing header, VAPID shape and no-cookie assertions remain in the unchanged first-reminder block.",
            "second_delivery_evidence": "Both second-stage destinations and their multiplicity are checked. The original slice(2) now uses sent.length, whose exact initial two endpoints were already asserted. The last endpoint check still requires the expired phone to be removed.",
            "phone_410_active_probe": "Suppressing 410 removal while keeping both fresh laptop keys made the renamed case fail at its endpoint-list assertion after the renewed laptop decrypt. The other eight cases were intentionally filtered in this keeper run.",
            "phone_410_failure": "AssertionError: expected [ …(2) ] to deeply equal [ Array(1) ]\n    at /work/test/web-push.test.ts:261:35\n    at work/node_modules/@vitest/runner/dist/chunk-artifact.js:1903:20"
          },
          "controls": {
            "original-stale-auth": {
              "source_sha256": {
                "src/web-push.ts": "3a902ad0f000440a7cb6f8f1e07db0f2685115f59f6cab8bd157c8b0a9cf3132",
                "src/agent.ts": "06ca3ce4fc5de3bbbad07c4180d7a61f40af9468719243acc9a3720c8fe011cc",
                "test/web-push.test.ts": "310f48d8110f1f22054da0912a9e17d915f7609cf2f02af919213d46a7638ca6",
                "test/ui/workspace.test.tsx": "e3a18ed2e39820e2723b8b43b826697e6451f02cb97b225da0a5389930032bc8"
              },
              "single_change": [
                "src/web-push.ts",
                "ON CONFLICT (endpoint) DO UPDATE SET p256dh = excluded.p256dh, auth = excluded.auth",
                "ON CONFLICT (endpoint) DO UPDATE SET p256dh = excluded.p256dh"
              ],
              "raw_attempt": 1,
              "results": [
                {
                  "files": [
                    "test/web-push.test.ts"
                  ],
                  "counts": [
                    9,
                    0,
                    0
                  ],
                  "exit": 0,
                  "name_filter": null,
                  "failed_assertions": []
                }
              ]
            },
            "candidate-stale-auth": {
              "source_sha256": {
                "src/web-push.ts": "3a902ad0f000440a7cb6f8f1e07db0f2685115f59f6cab8bd157c8b0a9cf3132",
                "src/agent.ts": "06ca3ce4fc5de3bbbad07c4180d7a61f40af9468719243acc9a3720c8fe011cc",
                "test/web-push.test.ts": "c855f55c22dd23e09379f0ffc1410b44846a41ca63880665150bddf2e5b6a254",
                "test/ui/workspace.test.tsx": "e3a18ed2e39820e2723b8b43b826697e6451f02cb97b225da0a5389930032bc8"
              },
              "single_change": [
                "src/web-push.ts",
                "ON CONFLICT (endpoint) DO UPDATE SET p256dh = excluded.p256dh, auth = excluded.auth",
                "ON CONFLICT (endpoint) DO UPDATE SET p256dh = excluded.p256dh"
              ],
              "raw_attempt": 2,
              "results": [
                {
                  "files": [
                    "test/web-push.test.ts"
                  ],
                  "counts": [
                    8,
                    1,
                    0
                  ],
                  "exit": 1,
                  "name_filter": null,
                  "failed_assertions": [
                    {
                      "name": "notifications sends one reminder per device using its current keys and removes a subscription when its service returns 410",
                      "message": "OperationError: Decryption failed. This could be due to a ciphertext authentication failure, bad padding, incorrect CryptoKey, or another algorithm-specific reason. Input length was 71, output length expected to be 71 for AES-GCM",
                      "stack_locations": [
                        "at decrypt (/work/test/web-push.test.ts:61:53)",
                        "at /work/test/web-push.test.ts:260:23"
                      ]
                    }
                  ]
                }
              ]
            },
            "original-clean": {
              "source_sha256": {
                "src/web-push.ts": "f978280d7ba639c77f45660f15a6692c01e5140aced34b6cd21954f107524640",
                "src/agent.ts": "06ca3ce4fc5de3bbbad07c4180d7a61f40af9468719243acc9a3720c8fe011cc",
                "test/web-push.test.ts": "310f48d8110f1f22054da0912a9e17d915f7609cf2f02af919213d46a7638ca6",
                "test/ui/workspace.test.tsx": "e3a18ed2e39820e2723b8b43b826697e6451f02cb97b225da0a5389930032bc8"
              },
              "single_change": null,
              "raw_attempt": 3,
              "results": [
                {
                  "files": [
                    "test/web-push.test.ts"
                  ],
                  "counts": [
                    9,
                    0,
                    0
                  ],
                  "exit": 0,
                  "name_filter": null,
                  "failed_assertions": []
                },
                {
                  "files": [
                    "test/ui/workspace.test.tsx"
                  ],
                  "counts": [
                    4,
                    0,
                    49
                  ],
                  "exit": 0,
                  "name_filter": "notification settings",
                  "failed_assertions": []
                }
              ]
            },
            "candidate-allowed": {
              "source_sha256": {
                "src/web-push.ts": "f387e39d5c2986e6f584c37899143968b170bc8ce5c9ecc118dce011a87e5093",
                "src/agent.ts": "06ca3ce4fc5de3bbbad07c4180d7a61f40af9468719243acc9a3720c8fe011cc",
                "test/web-push.test.ts": "c855f55c22dd23e09379f0ffc1410b44846a41ca63880665150bddf2e5b6a254",
                "test/ui/workspace.test.tsx": "e3a18ed2e39820e2723b8b43b826697e6451f02cb97b225da0a5389930032bc8"
              },
              "single_change": [
                "src/web-push.ts",
                "ON CONFLICT (endpoint) DO UPDATE SET p256dh = excluded.p256dh, auth = excluded.auth",
                "ON CONFLICT (endpoint) DO UPDATE SET (p256dh, auth) = (excluded.p256dh, excluded.auth)"
              ],
              "raw_attempt": 4,
              "results": [
                {
                  "files": [
                    "test/web-push.test.ts"
                  ],
                  "counts": [
                    9,
                    0,
                    0
                  ],
                  "exit": 0,
                  "name_filter": null,
                  "failed_assertions": []
                }
              ]
            },
            "candidate-cleanup": {
              "source_sha256": {
                "src/web-push.ts": "f978280d7ba639c77f45660f15a6692c01e5140aced34b6cd21954f107524640",
                "src/agent.ts": "778c543950fa3d993cc704fb9ae675d6a6fc92fb485efb306b676e0499d00e70",
                "test/web-push.test.ts": "c855f55c22dd23e09379f0ffc1410b44846a41ca63880665150bddf2e5b6a254",
                "test/ui/workspace.test.tsx": "e3a18ed2e39820e2723b8b43b826697e6451f02cb97b225da0a5389930032bc8"
              },
              "single_change": [
                "src/agent.ts",
                "if (status === 404 || status === 410) this.pushSubscriptions.remove(subscription.endpoint);",
                "if (status === 404) this.pushSubscriptions.remove(subscription.endpoint);"
              ],
              "raw_attempt": 5,
              "results": [
                {
                  "files": [
                    "test/web-push.test.ts"
                  ],
                  "counts": [
                    0,
                    1,
                    8
                  ],
                  "exit": 1,
                  "name_filter": "sends one reminder per device using its current keys",
                  "failed_assertions": [
                    {
                      "name": "notifications sends one reminder per device using its current keys and removes a subscription when its service returns 410",
                      "message": "AssertionError: expected [ …(2) ] to deeply equal [ Array(1) ]",
                      "stack_locations": [
                        "at /work/test/web-push.test.ts:261:35"
                      ]
                    }
                  ]
                }
              ]
            }
          },
          "unchanged_named_cases": [
            "VAPID (RFC 8292) serves the public key to a signed-in page, and null when the deployment has no VAPID key",
            "VAPID (RFC 8292) signs an ES256 JWT for the push service's origin, at most 24 hours long, naming the deployment's contact, with the key the page subscribes with",
            "message encryption (RFC 8291) encrypts RFC 8291's example to the exact message in its section 5, from the keys and salt in Appendix A",
            "message encryption (RFC 8291) uses a new sender key and salt for every message",
            "notifications says a scheduled task ran, in the User's words, and nothing else",
            "push services sends only to Google's, Mozilla's, Apple's and Microsoft's push services, over https on the standard port",
            "subscriptions keeps and forgets a browser's subscription, signed in and from this origin only, for a known push service only",
            "subscriptions keeps at most 10 devices, dropping the oldest"
          ],
          "raw": {
            "path": "controller/outputs/760faa4901a0a237/push-runs.ndjson",
            "sha256": "69c83eb3957608df9d428b95991ab7ec9556495a5fbee37424a4c1d81374c416"
          },
          "reproduce": "python -B controller/outputs/760faa4901a0a237/push-controls.py"
        },
        "source_review": {
          "fixture": "The service worker posts fresh subscription JSON to the same-origin registration API; the Settings action uses that API too. The server explicitly supports updating the existing endpoint's two keys. The browser fixture calls WebCrypto to generate a fresh ECDH P-256 key pair and a random 16-byte auth secret for each registration. Its exported public point is the standard 65-byte uncompressed form; the production parser checks the 0x04 prefix, point length and secret length. No invalid key data or database injection creates the renewal state.",
          "boundary": "The helper calls the actual Worker registration route. The production agent writes the subscription to its SQLite store. The real scheduler emits the reminder, the agent loads the stored keys, and the production sender builds and encrypts the outbound request. The test push service records its actual bytes and answers controlled HTTP statuses. A synthetic receiver opens those bytes. The renewal POST is supplied directly by the test; native browser event dispatch, push-network delivery and OS display are separate boundaries.",
          "oracle": "The test receiver uses its own private key and auth to parse and open the real ciphertext. Its receiver-side derivation is separate from the production encryption helper and is checked against an external RFC known answer in the same module. The two paths share WebCrypto and the repository's base64url transport utilities. The expected reminder text originates in the scheduling input.",
          "registration_scope": "This evidence concerns refresh at an unchanged endpoint. Browser behavior when a subscription receives a different endpoint and display on a device were outside these native selections."
        },
        "secondary_findings": [
          {
            "kind": "Source-supported test gap, unchanged",
            "claim": "The supplied push-service scenario exercises successful sends and a 410. Source removes subscriptions on 404 or 410 and records other statuses, so tests could separately check 404 removal and subsequent successful delivery after a 503. The 404 registration/deletion route assertions exercise a different HTTP response.",
            "references": [
              "pda-spec.md:772",
              "src/agent.ts:519",
              "src/web-push.ts:303",
              "test/web-push.test.ts:253"
            ],
            "validation": "No dedicated 404 or 503 behavior control or candidate test was implemented for this lead."
          },
          {
            "kind": "Source-supported test coupling, unchanged",
            "claim": "The documented limit is 10. Production exports that value and the scanned test builds its fixture from the same imported constant, registering one extra device and checking that the oldest is gone. The literal ten is not an independent expected value in that test.",
            "references": [
              "pda-spec.md:234",
              "src/web-push.ts:244",
              "src/web-push.ts:292",
              "test/web-push.test.ts:218"
            ],
            "validation": "The oldest-first case passed clean. Sensitivity to changing the numeric limit was not separately exercised."
          }
        ],
        "static_validation": {
          "raw": {
            "path": "controller/outputs/760faa4901a0a237/push-static.ndjson",
            "sha256": "a31bcfc37da318fdfa17f035443c598f269a7a4444db30d010b29e2494ab0eda"
          },
          "node": "v24.22.3",
          "typescript": "Version 6.0.3",
          "typecheck_exit": 0,
          "patch_check_exit": 0,
          "diff_check_exit": 0,
          "production_unchanged_exit": 0,
          "patch_applies_byte_for_byte": true,
          "actual_numstat": "8\t3\ttest/web-push.test.ts"
        },
        "ui_validation": {
          "config": "test/ui/vitest.config.ts",
          "file": "test/ui/workspace.test.tsx",
          "filter": "notification settings",
          "passed": 4,
          "failed": 0,
          "filtered_out": 49,
          "passed_cases": [
            "notification settings turns notifications on: asks permission, subscribes with the deployment's key and hands the subscription to the agent; off unsubscribes and forgets it",
            "notification settings subscribes nothing when the browser's permission is refused, and says how to allow it",
            "notification settings hides the option when the deployment has no VAPID key",
            "notification settings says how to get them on an iPhone when this browser can't take push messages"
          ],
          "provenance": "The independent selection ran on the clean pinned tree. Its production, UI test, fixture and runner bytes equal those in the sealed candidate; the only different file is the Workers Web Push test, which the UI selection excludes."
        },
        "source_provenance": {
          "immutable_snapshot": "controller/candidate-snapshots/760faa4901a0a237",
          "files_compared": 560,
          "all_manifest_hashes_verified": true,
          "input_scope": "For both PDA candidates reviewed by this verifier, all candidate evidence came from sealed source snapshots, frozen participant files, and evaluator controls. An initial workspace-wide search for AGENTS.md filenames returned some opaque subject-directory IDs. A directory-entry search was the full extent of that exposure. The verifier did not open live-subject files, assignment maps, or arm labels.",
          "image": "node@sha256:49f7adaf9f1574bc45c20ea317139b39a59d7e758d0e93745e112fd85cb42623",
          "node": "v24.22.3",
          "candidate_sources": {
            "pda-spec.md": {
              "sha256": "313953c8faa654542d718c57acc2bbcdb9ac797417457799adbe58e021011c43",
              "lines": [
                "149",
                "234",
                "772-773"
              ]
            },
            "public/sw.js": {
              "sha256": "dd817213f0164414e285334a5a0f27290720a3ac83813d8469cc19b60624409a",
              "lines": [
                "5-17",
                "33-48"
              ]
            },
            "src/ui/notifications.tsx": {
              "sha256": "0595a641f996230bec17139efa9669eabbb7c5074dcaaf11eb91337f3b1f1d07",
              "lines": [
                "59-79"
              ]
            },
            "src/index.ts": {
              "sha256": "68dd074eb45c3e705ece41e40c48c5fa0a3d9b5c65971d2ed362070f34b9526a",
              "lines": [
                "355-384"
              ]
            },
            "src/agent.ts": {
              "sha256": "06ca3ce4fc5de3bbbad07c4180d7a61f40af9468719243acc9a3720c8fe011cc",
              "lines": [
                "507-525",
                "532-536"
              ]
            },
            "src/web-push.ts": {
              "sha256": "f978280d7ba639c77f45660f15a6692c01e5140aced34b6cd21954f107524640",
              "lines": [
                "53-72",
                "178-200",
                "217-238",
                "243-249",
                "273-293"
              ]
            },
            "src/schedules.ts": {
              "sha256": "dfaa52daba0ac79b4a70b8d12eea3b2f20a463d11fb30ac9a67de9096417bbd0",
              "lines": [
                "189-200"
              ]
            },
            "test/web-push.test.ts": {
              "sha256": "c855f55c22dd23e09379f0ffc1410b44846a41ca63880665150bddf2e5b6a254",
              "lines": [
                "18-76",
                "80-104",
                "185-215",
                "218-224",
                "228-262"
              ]
            },
            "test/agent-helpers.ts": {
              "sha256": "9df7708228cf6c43d9283558ee93f99e7513fb3057558e8c4c64535a03b375a5",
              "lines": [
                "71-73"
              ]
            },
            "test/worker.ts": {
              "sha256": "4b1702f9fe6357e45d8d2c94a2560542c3915f127bdfe436a058f0a4c2dd0da5",
              "lines": [
                "1286-1304"
              ]
            },
            "test/ui/workspace.test.tsx": {
              "sha256": "e3a18ed2e39820e2723b8b43b826697e6451f02cb97b225da0a5389930032bc8",
              "lines": [
                "1047-1175"
              ]
            },
            "test/agent-data.test.ts": {
              "sha256": "b98932cc313cf0f09aaca06f7269832bcb5cfdbc2dce256238fc9adb81d8827d",
              "lines": [
                "86-99"
              ]
            },
            "test/ui/attachments.test.tsx": {
              "sha256": "3eb340117ae01a72fd65cfb50c4de11bee39e19514828ea89412531021837a28",
              "lines": [
                "111-130"
              ]
            }
          },
          "baseline_test": {
            "path": "preparation/pda/participant/repo/test/web-push.test.ts",
            "sha256": "310f48d8110f1f22054da0912a9e17d915f7609cf2f02af919213d46a7638ca6"
          },
          "evidence_inputs": [
            {
              "path": "controller/outputs/760faa4901a0a237/disposition.json",
              "sha256": "5b862971054d36f4622a5c10f7e7052508a5d0c31548fe9692c3d63d8dc9c3d5"
            },
            {
              "path": "controller/outputs/760faa4901a0a237/response.md",
              "sha256": "9d89c945196f4d11704b65b5e733ab389d8805b5e995209656b4f27a9802af37"
            },
            {
              "path": "controller/outputs/760faa4901a0a237/patch.diff",
              "sha256": "6f0cfde54f031ffda8f39d40ebbb69f56c4650570fa035023abf0588d397c385"
            },
            {
              "path": "controller/outputs/760faa4901a0a237/candidate-snapshot.json",
              "sha256": "bed9cc454999f797d538d4928d4e2fc82929e29badf9b8c1a7cec5e63d82c1db"
            },
            {
              "path": "controller/outputs/760faa4901a0a237/push-controls.py",
              "sha256": "7e9338897d59c2f3123e18a68b4985756d07e7d8ee81797c7e4f2efd39200a7a"
            },
            {
              "path": "preparation/pda/README.md",
              "sha256": "b8d832d4788960d43d95689b6492e3f12a184f8f778b4dbef0d618018d954672"
            },
            {
              "path": "preparation/pda/participant/inventory.json",
              "sha256": "cf827440745efe277fb6bbe7ff389ceb30e6e39f24f8d4202c1f4b517d7e8cee"
            },
            {
              "path": "preparation/pda/evaluator/SCORING.md",
              "sha256": "75587b689d500380552df45205830caf26560018a3ca95a952229c651801ac76"
            },
            {
              "path": "preparation/pda/evaluator/case-lock.json",
              "sha256": "125f5a05b9faa3131836f0c791bc3ded0eb8d45cdaa9ce91b34a01dbf76c9550"
            },
            {
              "path": "preparation/pda/evaluator/controls.py",
              "sha256": "3913d69fb2a2c0acd28f9a114c916cd07d6e965252a275a2e6ba5fe9a99b0498"
            },
            {
              "path": "preparation/pda/evaluator/driver.mjs",
              "sha256": "973e9b56f1d4ef78436212655f675b6c19f44d2fbf3f3a64e24f29acdb02fdc9"
            },
            {
              "path": "preparation/pda/evaluator/source-manifest.json",
              "sha256": "4a89263f43ee7f16911ffda118de130898b617ccc90c7f6e1dff953024ecd11d"
            }
          ],
          "historical_ci": [
            {
              "name": "Check action pins",
              "conclusion": "success",
              "source_commit": "c0a9a85c8f690eb77313b9627e3ea39cadc58968",
              "url": "https://github.com/adewale/pda/actions/runs/45800972780/job/139843780636",
              "receipt": {
                "path": "preparation/pda/participant/ci/jobs-45800972780.json",
                "sha256": "0e66dc6fa31430d3982f2021296a832ca676989f459788d31078bdc34dd4dc3d"
              }
            },
            {
              "name": "interop",
              "conclusion": "success",
              "source_commit": "c0a9a85c8f690eb77313b9627e3ea39cadc58968",
              "url": "https://github.com/adewale/pda/actions/runs/45800972796/job/139843780982",
              "receipt": {
                "path": "preparation/pda/participant/ci/jobs-45800972796.json",
                "sha256": "d7687d3aa3a346e1482c19524632d90030ab08115317989882b109d78625f6d7"
              }
            },
            {
              "name": "test",
              "conclusion": "success",
              "source_commit": "c0a9a85c8f690eb77313b9627e3ea39cadc58968",
              "url": "https://github.com/adewale/pda/actions/runs/45800972889/job/139843781530",
              "receipt": {
                "path": "preparation/pda/participant/ci/jobs-45800972889.json",
                "sha256": "e722f0ba7943aa1af4725227e1563bd0d421ece8fc5ff34081b394df2d5cb235"
              }
            }
          ]
        },
        "limits": [
          "The packet supplied 56 of 155 named modules. Original versus revised fault sensitivity applies to the complete nine-test Web Push file. Other modules may cover related behavior indirectly.",
          "The hosted action-pins, interop and test jobs succeeded on the original upstream commit. This campaign's results cover its selected offline modules and controls; the patched full-suite and hosted outcomes remain unknown.",
          "Subject runtime measurements, reported reading of other tests, and its temporary scratch history were not independently timed or observed. Independent checks verified sealed file identity, the actual paired native failure and the named clean and keeper selections."
        ]
      }
    }
  ]
}
