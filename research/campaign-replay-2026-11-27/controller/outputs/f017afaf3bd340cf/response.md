Both public editor evaluations awarded **3/3** to advice to edit generated `editor.html` directly and skip the rebuild. An answer that named the download handler and both build commands earned **2/3** because it omitted the standalone generator’s filename. A maintainer following the higher-scoring advice could lose the change on the next build.

`editor/js/export.js` binds both download buttons and sets `diagram.png` and `diagram.svg`. `editor/js/app.js` initializes those handlers. `scripts/site/editor.ts` bundles `editor/js/entry.js` and writes standalone `editor.html`. For the hosted page, `package.json` invokes `website/build.ts` and `e2e/editor-site-interactions.e2e.test.ts` consumes `website/public/editor/index.html`. The hosted builder itself is outside the sample.

I repaired the two cases in `skill-evals/shared-benchmark.json`. Each now asks for a plain-JSON plan for changing download filenames and scores the edit target, generator, generated file and rebuild script by role. The standalone case also distinguishes SVG/PNG downloads from the ASCII/Unicode views in `editor/js/buttons.js`. I aligned `skills/agentic-mermaid-live-editor/SKILL.md` and `skill-evals/ablations/no-editor-source-of-truth.patch` with those roles.

| Identical saved plan | Original word checks | Repaired plan check |
|---|---:|---:|
| Correct standalone plan | 3/3 | 1/1 |
| Same plan, changing only the edit target to `editor.html` | 3/3 | 0/1 at `edit` |
| Correct hosted plan | 1/3 | 1/1 |
| Standalone build prescribed for the hosted page | 3/3 | 0/1 |

I ran the following commands from `work/`. The controls are saved in `controls/`. The original manifest is available through `git -C repo show HEAD:skill-evals/shared-benchmark.json` for replay with `--manifest`.

```sh
python3 -B support/grade_text.py --case pos-live-editor-source-of-truth --answer-file controls/standalone-edit-html.txt
python3 -B support/grade_text.py --case adv-reject-editor-html-direct-edit --answer-file controls/hosted-good.txt
python3 -B support/focused_baseline.py
```

Across both cases, four valid JSON plans passed, including reordered fields and `./` paths. All 12 incorrect plans failed on the relevant fields, with zero deferred judgments. The harness’s `grade` command confirmed four selected saved runs. All 10 tests in `eval/benchmark/visualizations/mermaid_baseline_test.py` passed before and after. Manifest validation passed on both versions with 32 existing warnings. The editor ablation materialized cleanly. Full `materialize-ablations` stopped on both versions because `no-verify-before-serialize.patch` no longer matches its target at line 62. `git diff --check` passed for the three evaluation and guidance files (+42/−35 lines).

I screened test declarations across all 58 sampled files in the 660-file inventory. I inspected `scripts/ci/unit-test-files.ts`, `e2e/browser-contract-files.ts`, the CI and coverage workflows, and sampled `flowchart-marker-raster.test.ts`, `property-invariance-colour.test.ts`, `website-build.test.ts` and `e2e/dist-artifact.e2e.test.ts`. The skill manifest separately lists 43 tune cases and eight private stubs. The local editor results measure saved-answer grading. Model behavior and browser exports were unmeasured. Historical `support/ci-observations.json` records zero canonical CI runs at `f49196e7` and a coverage-shard failure for the CJK font prerequisite at `src/__tests__/png-fonts.test.ts:89`.
