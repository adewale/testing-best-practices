from pathlib import Path
import json,hashlib
from collections import defaultdict,Counter
L=Path(__file__).resolve().parents[1]; R=L/'repo'; G=L.parent/'openclaw'
raw=L/'evidence'/'read-events.json'
if not raw.exists(): raw.write_text((L/'read-ledger.json').read_text())
events=json.loads(raw.read_text()); groups=defaultdict(list)
for e in events: groups[e['path']].append(e['lines'])
def merged(ranges):
 out=[]
 for start,end in sorted(ranges):
  if out and start<=out[-1][1]+1: out[-1][1]=max(end,out[-1][1])
  else: out.append([start,end])
 return out
def add(x,r): groups[x].extend(r)
for f in ['.agents/skills/test-audit/SKILL.md','.agents/skills/test-audit/references/audit.md','.agents/skills/openclaw-testing/SKILL.md','docs/help/testing/writing-tests.md']:
 p=(G/f).resolve()
 add(str(p),[[1,len(p.read_text().splitlines())]])
add('src/cli/args.ts',[[43,43],[59,59],[112,112],[128,131]])
add('website/source/assets/shader-mark.js',[[94,101]])
add('src/theme.ts',[[317,317],[320,320]])
add('src/output-security.ts',[[15,15],[585,585],[607,607]])
add('e2e/run-browser-contracts.ts',[[5,5],[46,49],[55,55]])
# The following long reads were requested in full; conservatively list only
# reaches actually inspected after the tool's output truncation.
groups['src/__tests__/deploy-workflow-transaction.test.ts']=[[19,73],[87,122],[407,425],[451,516]]
groups['src/__tests__/browser-script-harness.ts']=[[1,10],[44,58],[357,376]]
groups['src/__tests__/editor-theme-switch.test.ts']=[[1,159],[161,216]]
groups['e2e/cli.e2e.test.ts']=[[1,166]]
groups['src/__tests__/graph-layout-selection.test.ts']=[[1,131]]
groups['src/__tests__/cli-error-envelope.test.ts']=[[205,240],[243,280]]
groups['website/source/assets/styles.css']=[[1,115],[267,291]]
groups['src/layout-engine.ts']=[[1406,1411],[1420,1458]]
groups['src/__tests__/cli-flags-help-sync.test.ts']=[[1,217]]
groups['docs/testing-strategy.md']=[[785,846]]
for k in ['package.json','bunfig.toml','CLAUDE.md','AGENTS.md']:
 assert k in groups
role={}
for r,paths in {
 'candidate test':['src/__tests__/chrome-token-lockstep.test.ts','src/__tests__/cli-multi-input.test.ts','src/__tests__/layout-bundle-proposals.test.ts','src/__tests__/agent-cli-render-formats.test.ts'],
 'owner or caller':['src/layout/passes/edge-bundling.ts','src/cli/index.ts','src/layout-engine.ts','src/layout/bundle-routes.ts','src/cli/preflight.ts','src/cli/args.ts','src/cli/help.ts','src/cli/run-entrypoint.ts','src/cli/deadline.ts','bin/am.ts','editor/css/topbar.css','editor/css/variables.css','editor/js/rendering.js','editor/html/topbar.html','website/build.ts','website/source/pages/home.html','website/source/assets/styles.css','website/source/assets/shader-mark.js'],
 'project instructions or independent contract':['AGENTS.md','CLAUDE.md','docs/testing-strategy.md','DESIGN.md','docs/features.md'],
 'collection, package or CI':['package.json','bunfig.toml','.github/workflows/ci.yml','scripts/ci/unit-test-files.ts','scripts/ci/run-unit-tests.ts','e2e/browser-contract-files.ts','e2e/run-browser-contracts.ts'],
 'sibling proof or supporting fixture':['src/__tests__/cli-jsonl.test.ts','src/__tests__/cli-batch-render-parity.test.ts','src/__tests__/cli-flags-help-sync.test.ts','src/__tests__/cli-error-envelope.test.ts','src/__tests__/editor-theme-switch.test.ts','src/__tests__/helpers/cli-capture.ts','src/__tests__/helpers/temp-dir.ts','src/__tests__/helpers/editor-module-harness.ts','src/__tests__/browser-script-harness.ts','e2e/cli.e2e.test.ts']
}.items():
 for p in paths: role[p]=r
files=[]
for p,ranges in sorted(groups.items()):
 path=Path(p) if p.startswith('/') else R/p
 n=len(path.read_text().splitlines()); ranges=merged(ranges)
 if str(path).startswith(str(G)+'/'):
  origin='assigned guidance'; relative=str(path.relative_to(G))
 else: origin='target'; relative=p
 files.append({'origin':origin,'path':relative,'coverage':'full' if ranges==[[1,n]] else 'partial','reviewed_line_ranges':ranges,'file_lines':n,'role':'assigned audit or linked testing guide' if origin=='assigned guidance' else role.get(p,'discovery or alternative explanation')})
search=['discovery','leads-assertions','leads-implementation','leads-names','supervision-routing','file-association','scope-routing-docs','cli-contract-refs','palette-refs','paint-consumers','strict-contract','recent-graph','bundle-context','shared-brand-siblings','incidence','graph-browser-state','graph-ink-siblings','css-caller-extra','cli-flag-owners']
out={'base_sha':'f49196e7f5d6d2f0970a4a76fe62644ee5e9d004','method':'Self-recorded source reading. Full and partial refer to inspected content, not files merely traversed by rg, imports, tests or Git. Line numbering is 1-based inclusive. Raw attempted read ranges are in evidence/read-events.json. A few files were fully opened but only substantive visible ranges are counted. Exact line matches of the broader candidate searches are available in the listed logs.','counts':dict(Counter(f["origin"]+" "+f["coverage"] for f in files)),'files':files,'outside_repo_material':[{'file':'../task-packets.json','coverage':'partial','fields':['common','openclaw','runtime_path']},{'file':'dependency-install.log','coverage':'full','purpose':'verify private installation and version from prepared input'}],'discovery_searches':[f'evidence/commands/{s}.log' for s in search],'public_target_history':[str(f.relative_to(L)) for f in sorted((L/'evidence'/'commands').glob('*.log')) if any(k in f.stem for k in ('history','blame','origin','original-cli-contract'))],'discovery_scope_note':'The initial CLI terms search returned incidental lines from target historical material under docs/design and docs/project. They were not selected, opened for review or used as evidence for a finding. The other comparison lane and comparison studies were not opened.','queried_only':'Repository-wide file-name and text matches are discovery only; no claim of a substantive read of every matching file or coverage of all 606 source unit-test files.'}
(L/'read-ledger.json').write_text(json.dumps(out,indent=2)+'\n')
print(out['counts'])
