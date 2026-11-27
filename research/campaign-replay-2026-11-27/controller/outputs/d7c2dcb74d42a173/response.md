# Editor export guidance

Both public editor cases gave full credit to advice to change `scripts/site/editor.ts` and hand-edit the generated HTML. A rebuild can erase that patch. The image download handlers live in `editor/js/export.js`, loaded by `editor/js/app.js`. The standalone assembler writes `editor.html`. For the hosted editor, `package.json` selects `website/build.ts`, and `e2e/editor-site-interactions.e2e.test.ts` consumes `website/public/editor/index.html`.

I repaired `pos-live-editor-source-of-truth` and `adv-reject-editor-html-direct-edit` in `work/repo/skill-evals/shared-benchmark.json`. Each now grades a JSON maintenance plan by the edit target, each output’s builder, and its rebuild action and command. The positive case also distinguishes SVG/PNG downloads from ASCII/Unicode text. The corresponding `skill-evals/ablations/no-editor-source-of-truth.patch` now removes the modular behavior source-map row alongside the assembler row and generated-output warning.

**Local evidence.** I graded the same 16 positive and 14 adversarial saved answers against the original and repaired manifests with the supplied harness. Each cell shows passed assertions. All judgments completed locally.

| Saved answer | Original positive | Repaired positive | Original adversarial | Repaired adversarial |
|---|---:|---:|---:|---:|
| Correct handler and builders | 3/3 | 4/4 | 3/3 | 3/3 |
| Handler and standalone assembler swapped | 3/3 | 2/4 | 3/3 | 1/3 |
| Hand-edit the hosted output | 3/3 | 3/4 | 3/3 | 2/3 |
| Image and text format roles swapped | 3/3 | 3/4 | — | — |

The documented `editor/js/` directory and reordered JSON keys also received full credit. The revised prompts require JSON, so a sound prose-only answer received zero. These scores measure grader behavior on saved answers. Model performance, private splits and browser behavior were outside the run.

Replay the role swap from `work/` with `python3 -B support/grade_text.py --case pos-live-editor-source-of-truth --answer-file editor-controls/positive/swapped-owners.txt`. The project’s Node-run manifest materializer followed by `skill_benchmark.py validate` accepted 51 cases and four ablations. Editor-only ablation materialization passed. Full `materialize-ablations` stopped on the unrelated `no-verify-before-serialize` patch at line 62 on both the clean original and repaired trees. `python3 -B support/focused_baseline.py` passed all 10 retained-data tests before and after.

**Audit scope and CI.** I scanned all 58 sampled conventional test files across 13 strata in the 660-file inventory. I inspected the editor interaction, theme-switch, website-build, Section B visual-golden and benchmark version checks, the public live-editor skill, and the unit/browser selectors. The two public skill cases are outside the conventional count. Historical `support/ci-observations.json` records zero canonical CI runs at upstream `f49196e7` and a failed coverage diagnostic there. The older canonical run at `17c400a9` failed quality gates and passed browser-site.
