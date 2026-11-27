import json,re,pathlib,collections,subprocess
L=pathlib.Path(__file__).resolve().parent.parent
base='f49196e7f5d6d2f0970a4a76fe62644ee5e9d004'
R=L/'repo'
# Full only where the whole file was covered by reads and reviewed.
full=[
 ('AGENTS.md','02'),('CLAUDE.md','02,05'),
 ('bunfig.toml','05'),('e2e/bunfig.toml','05'),
 ('.github/workflows/coverage.yml','43'),('scripts/ci/run-unit-tests.ts','69'),
 ('scripts/ci/unit-test-files.ts','74'),('e2e/run-browser-contracts.ts','16'),
 ('e2e/browser-contract-files.ts','22,69'),
 ('src/__tests__/cli-batch-render-parity.test.ts','11'),('src/__tests__/cli-multi-input.test.ts','11,18'),
 ('src/__tests__/png-fonts.test.ts','43,51,53,58'),('src/__tests__/helpers/png-pixels.ts','48'),
 ('src/__tests__/helpers/cli-capture.ts','25'),('src/__tests__/helpers/temp-dir.ts','25'),
 ('src/__tests__/journey-svg-snapshot.test.ts','53,56'),('src/__tests__/fanout-symmetry.test.ts','17,94'),
 ('src/__tests__/helpers/fc-parameters.ts','87'),('src/__tests__/property-source-preserving-edit.test.ts','17,34,77,95'),
 ('src/agent/font-coverage.ts','63'),
]
part=[
 ('package.json','package exports, scripts, pinned deps','02,13,22,89'),
 ('.github/workflows/ci.yml','1–280, CLI and E2E portions, selected matches including 570–581, 775–806','05,13,43,69,96'),
 ('.github/workflows/qualify-ci.yml','dispatch and job setup','05,69'),('.github/workflows/contract-discovery.yml','1–65 plus selected seed and trigger lines','10,13,22,96'),
 ('docs/testing-strategy.md','headings, normative contract-review section, CI selection and seed matches','05,13,43'),
 ('docs/features.md','101–106 and matching references','15,18,20'),('docs/custom-fonts.md','native rasterizer and density, especially 274–293','72,77,82'),
 ('docs/agent-mutation-policy.md','145–181,257–295; selected byte and order references','34,37,39,95'),
 ('docs/design/system/layout-rubric.md','selected layout-contract/geometry references','31'),
 ('src/__tests__/authored-style-color-admission.test.ts','fixture, validation and transport rows, especially 14–64,111–222','23,24,26,29'),
 ('src/__tests__/quadrant-style.test.ts','1–245 plus matched declarations and diagnostic assertions','23,24,26,29'),
 ('src/__tests__/theme-color-admission.test.ts','297–361','24'),
 ('src/__tests__/property-cli-surface-fuzz.test.ts','142–191 and batch-family grep matches','20,26'),
 ('src/__tests__/agent-source-preserving-edit.test.ts','1–49,468–488,620–703; selected fixture and assertion matches','34,37,40,81,84,87'),
 ('src/__tests__/agent-class.test.ts','69–119,630–652,681–702,791–805 and matched selectors','70,76,81'),
 ('src/__tests__/agent.test.ts','56–81','76,81'),('src/__tests__/mermaid-cleanup.test.ts','127–163,219–260','81,84'),
 ('src/__tests__/extension-family-public-api.test.ts','198–226 and batch parse matches','20,76,81'),
 ('src/__tests__/agent-source-map.test.ts','matched CRLF/span assertions, 974–1190','67'),
 ('src/__tests__/property-source-preservation.test.ts','1–90; adjacent canonical-serialization owner','39,77'),
 ('src/__tests__/fc-seed.preload.ts','seed policy/config matches','20,76'),
 ('src/__tests__/helpers/upstream-mermaid.ts','88–139,211–235; Node/installed Mermaid handoff','77,84,89,91'),
 ('src/__tests__/agent-png-determinism.test.ts','20–63, named tests and adjacent checks','63,67,74'),
 ('src/__tests__/agent-png.test.ts','selected test titles, baselines and pixel oracles','58,63,67'),
 ('src/__tests__/host-png-backend-parity.test.ts','selected adapter/provenance assertions','63,65,67,82'),
 ('src/__tests__/embedded-font-resources.test.ts','selected file and verification evidence','65,67'),
 ('src/__tests__/journey-integration.test.ts','1–100','50'),
 ('src/__tests__/journey-layout-quality.test.ts','1–38','72'),('src/__tests__/journey-theme.test.ts','task text/box source matches','47,50'),
 ('src/__tests__/helpers/svg-normalize.ts','1–60; snapshot contract','65'),
 ('src/__tests__/marker-raster-parity-browser.test.ts','1–105, synthetic orientation cases and guard,103–143','13'),
 ('src/__tests__/svg-style-isolation-browser.test.ts','1–76','16'),('src/__tests__/editor-style-switch.test.ts','1–65','16'),
 ('src/__tests__/editor-theme-switch.test.ts','1–54','16'),
 ('src/__tests__/graph-layout-selection.test.ts','188–237,282–333 plus test declarations and parameter groups','12,31'),
 ('src/__tests__/route-contracts.test.ts','declarations/churn only','04,12'),('src/__tests__/self-loop-arcs.test.ts','declarations/churn only','04,12'),
 ('src/__tests__/cli-error-envelope.test.ts','225–245','25'),
 ('e2e/cli.e2e.test.ts','1–145,146–212 and command declarations','19,25,32,95'),
 ('e2e/tarball-consumer-fuzz.e2e.test.ts','395–485 incl independent content/invalid lines','19,20'),
 ('e2e/editor-site-interactions.e2e.test.ts','discovery only, selected artifact and recovery assertions','10'),
 ('src/cli/index.ts','68–91,200–440,1334–1545, central return/failure catch and callers','11,15,19,26,32'),
 ('src/cli/jsonl.ts','line stream and ownership, via 19','19'),
 ('src/agent/png.ts','50–135,177–266 plus call sites','44,50,53,56,74'),
 ('src/png-contract.ts','font defaults/runtime and policy matches','44,56'),
 ('src/journey/renderer.ts','535–711 incl task geometry, label and paint','50,51,53'),
 ('src/agent/apply.ts','118–191','76,84'),('src/agent/mutate.ts','265–395','37,76,84,87'),
 ('src/agent/source-projection.ts','1–180,1490–1585,1616–1635 and eol/diff references','37,39,40,70,84,87'),
 ('src/layout/passes/fanout.ts','1–235 plus historical preserving patch and selected output/call-site lines','31,35,94'),
 ('src/layout-engine.ts','fanout pass and downstream mutator declarations','31,35,94'),
 ('src/quadrant/point-style.ts','nominal error definition and field matches','26,41'),('src/render-error-diagnostic.ts','selected nominal diagnostic declarations','26,41'),
]
def fentry(p,s):
 path=R/p
 assert path.is_file(),p
 return {'path':p, 'lines':len(path.read_bytes().splitlines()),'evidence_ids':s.split(',')}
known={p for p,s in full}|{p for p,q,s in part}
tracked=set(subprocess.check_output(['git','ls-files'],cwd=R,text=True).splitlines())
match=collections.defaultdict(lambda:collections.defaultdict(set))
for log in sorted((L/'evidence').glob('*.log')):
 for line in log.read_text(errors='replace').splitlines():
  m=re.match(r'^((?:src|e2e|docs|scripts|eval|editor|website|\.github)/[^:\t]+|(?:README|AGENT_NATIVE|CLAUDE)\.md|package\.json):(\d+):',line)
  if m and m[1] in tracked:
   match[m[1]][log.name].add(int(m[2]))
res={'base':base,'inventory':{'tracked_paths':3512,'test_or_spec_named_files':659,'canonical_unit_entries':608,'core_unit_named_files':606,'e2e_named_files':12,'references':['evidence/01-baseline.log','evidence/04-test-inventory.log','evidence/89-actual-enrollment.log']},
 'method':'Human review of cited full files and partial ranges. Search-hit paths and line numbers below are mechanical discovery, never a claim that a file or parameter matrix was fully reviewed. Range is the extraction window and can exceed the portion discussed. A focused runner can execute parameter rows outside the manually reviewed range. Hosted run paths are omitted from this checkout ledger.',
 'selected_strata':['default branch CI and scheduled diagnostic wiring','CLI batch/multi-input and public error transport','native PNG font selection and appearance','structured source-preserving edits','recently changed ELK pass as a positive control','browser gate routing and package-level CLI as overlapping proof'],
 'guidance':{'package':'../ours/testing-best-practices','files':['SKILL.md','references/test-types.md','references/antipatterns.md','references/test-audit.md','references/test-audit-patterns.md','references/typescript.md','references/gate-integrity.md','references/property-based-testing.md','references/golden-file-testing.md','references/mutation-testing.md'],'scope':'Root skill read in full. Topical and language references consulted at the relevant sections; combined captured text need not have been read word for word.'},
 'full':[fentry(p,s) for p,s in full],
 'partial':[dict(fentry(p,s),scope=q) for p,q,s in part],
 'search_only':{p:{log:sorted(lines) for log,lines in m.items()} for p,m in sorted(match.items()) if p not in known},
 'unrun':['local full three-shard suite and full instrumented coverage','type/lint/CI quality gates','full website or dist build','fresh tarball/installed bin, multi-OS and single-binary lanes','full Chromium/public site and image corpus','external grammar corpus and live provider calls','unselected families, files and parameter rows']}
(L/'read-ledger.json').write_text(json.dumps(res,indent=2)+'\n')
