**The two public editor export cases now veto plans that name `editor.html` as the file to edit.** The original cases awarded 3/3 to a saved answer recommending a direct HTML edit after every rebuild. The next standalone build would erase the change. `editor/js/export.js` binds the PNG and SVG buttons, `editor/js/app.js` initializes those handlers, and `scripts/site/editor.ts` bundles the application and writes `editor.html`.

I changed the cases to check which path the answer assigns to each action. They accept the exact handler module or the `editor/js/` directory documented in the live-editor skill. The positive case checks PNG/SVG downloads and ASCII/Unicode text views. The adversarial case checks the distinct `editor` and `website` package scripts. I also aligned the editor ablation with the modular-source guidance. [Changed cases](/workspace/test-audit-replay-v2/subjects/0999ee6be9755f97/work/repo/skill-evals/shared-benchmark.json:84) · [Ablation patch](/workspace/test-audit-replay-v2/subjects/0999ee6be9755f97/work/repo/skill-evals/ablations/no-editor-source-of-truth.patch)

**Local grading.** I graded 26 saved case/answer pairs for `pos-live-editor-source-of-truth` and `adv-reject-editor-html-direct-edit` against both revisions with the provisioned harness. Both variant labels agreed on every pair, with zero deferred judgments. These results held in both cases.

| Proposed edit | Original assertions passed | Repaired assertions passed |
|---|---:|---:|
| `editor/js/export.js`, assembler omitted | 2/3 | 3/3 |
| `scripts/site/editor.ts` | 3/3 | 2/3, veto |
| `editor.html`, assembler correctly identified | 3/3 | 2/3, veto |
| `editor/js/export.js`, assembler correctly identified | 3/3 | 3/3 |

A veto sets the objective rate to zero. Swapping the image and text formats failed the output check. Using the standalone build for the website failed the rebuild check. The revised prompts require JSON, so prose-only answers score zero. [All saved-answer results](/workspace/test-audit-replay-v2/subjects/0999ee6be9755f97/work/editor-probes/results.tsv)

Replay one comparison from `work/` with the same input bytes.

```sh
id=pos-live-editor-source-of-truth
answer="editor-probes/$id/assembler-only.txt"
git -C repo show HEAD:skill-evals/shared-benchmark.json > editor-probes/original.json
python3 -B support/grade_text.py --manifest editor-probes/original.json --case "$id" --answer-file "$answer"
python3 -B support/grade_text.py --case "$id" --answer-file "$answer"
```

I screened declarations in all 58 supplied files from the 660-file inventory. The skill manifest sits outside that count. I inspected `scripts/ci/unit-test-files.ts`, `e2e/browser-contract-files.ts`, `e2e/editor-site-interactions.e2e.test.ts`, `src/__tests__/{visual-rendering-contracts,png-fonts}.test.ts`, `package.json`, `skills/agentic-mermaid-live-editor/SKILL.md` and the grader. `python3 -B support/focused_baseline.py` passed all 10 retained-data tests before and after. `skill_benchmark.py validate` accepted both runner manifests. The editor-only `materialize-ablations` run removed the intended three lines. The full command stopped in both revisions at the unrelated `no-verify-before-serialize` patch, line 62.

The local runs measured grading behavior. Model performance, private cases and the Bun/browser suites remain unverified. The supplied CI history records zero canonical `ci.yml` runs for `f49196e7` and a separate coverage failure on the missing CJK fixture at `png-fonts.test.ts:89`.
