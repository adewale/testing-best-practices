from pathlib import Path
import json,os,shutil,subprocess,tempfile
from capture import run
R=Path('/workspace/mermaid-skill-comparison-2026-11-27');W=R/'verification/repo';E=R/'verification/evidence';O=R/'openclaw-audit/evidence'
link=W/'node_modules'
if not link.exists():link.symlink_to(R/'openclaw-audit/repo/node_modules',target_is_directory=True)
(E/'dependency-note.json').write_text(json.dumps({'scope':'Parent verification borrows the completed OpenClaw lane installation; no model subject runs against it now. Source worktree and mutable command/cache/temporary paths are separate. Shared-host execution, not independent dependency provenance.','source_sha':'f49196e7f5d6d2f0970a4a76fe62644ee5e9d004'},indent=2)+'\n')
results=[]
def cmd(label,argv,expected=0,env=None):
 r,stdout,stderr=run(label,argv,W,env);results.append(r)
 if r['exit_code']!=expected:raise AssertionError((label,r['exit_code'],expected,stderr[-2000:].decode(errors='replace')))
 return stdout,stderr
def restore(*paths):
 for path in paths:(W/path).write_bytes(subprocess.check_output(['git','show','HEAD:'+path],cwd=W))
def patch(name):cmd('apply-'+name,['git','apply',str(O/(name+'.patch'))])
cli='src/__tests__/cli-multi-input.test.ts';graph='src/__tests__/layout-bundle-proposals.test.ts';css='src/__tests__/chrome-token-lockstep.test.ts'
cli_owner='src/cli/index.ts';graph_owner='src/layout/passes/edge-bundling.ts';css_owner='website/source/assets/styles.css'
cmd('oc-baseline-owners',['bun','test',cli,graph,css,'--timeout','30000'])
patch('cli-fault');cmd('oc-cli-fault-owner',['bun','test',cli,'--timeout','30000'])
patch('cli-repair');cmd('oc-cli-repair-fault',['bun','test',cli,'--timeout','30000'],1)
restore(cli_owner);patch('cli-permitted');cmd('oc-cli-repair-permitted',['bun','test',cli,'--timeout','30000'])
restore(cli_owner,cli)
patch('graph-fault');cmd('oc-graph-fault-owner',['bun','test',graph,'--timeout','30000'],1)
patch('graph-repair');cmd('oc-graph-repair-fault',['bun','test',graph,'--timeout','30000'],1)
restore(graph_owner);patch('graph-permitted');cmd('oc-graph-repair-permitted',['bun','test',graph,'--timeout','30000'])
restore(graph);cmd('oc-graph-old-permitted',['bun','test',graph,'--timeout','30000'],1)
restore(graph_owner)
shutil.copyfile(O/'color-witness.cjs',E/'browser-witness.cjs')
with tempfile.TemporaryDirectory(prefix='mtv-',dir='/tmp') as t:
 env={'TMPDIR':t,'XDG_CONFIG_HOME':str(E/'browser-config')}
 cmd('oc-css-baseline-browser',['bun',str(E/'browser-witness.cjs')],env=env)
 patch('css-fault');cmd('oc-css-fault-owner',['bun','test',css,'--timeout','30000']);cmd('oc-css-fault-browser',['bun',str(E/'browser-witness.cjs')],1,env)
 restore(css_owner);patch('css-permitted');cmd('oc-css-permitted-owner',['bun','test',css,'--timeout','30000'],1);cmd('oc-css-permitted-browser',['bun',str(E/'browser-witness.cjs')],env=env)
 restore(css_owner)
cmd('oc-restored-diff',['git','diff','--exit-code','HEAD'])
(E/'openclaw-verification.json').write_text(json.dumps({'scope':'Independent execution of reviewed, retained fault/repair/permitted patches on a clean worktree; browser uses production header fragments and actual CSS, not a built-site E2E.','results':results},indent=2)+'\n')
print('OpenClaw parent verification complete')
