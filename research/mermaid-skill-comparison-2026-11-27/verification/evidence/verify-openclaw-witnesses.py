from pathlib import Path
import json,subprocess
from capture import run
R=Path('/workspace/mermaid-skill-comparison-2026-11-27');W=R/'verification/repo';E=R/'verification/evidence';O=R/'openclaw-audit/evidence';rows=[]
def cmd(label,argv,want=0):
 r,_,_=run(label,argv,W);rows.append(r);assert r['exit_code']==want,(label,r);return r
def restore(path):(W/path).write_bytes(subprocess.check_output(['git','show','HEAD:'+path],cwd=W))
cmd('oc-cli-public-baseline',['python3',str(O/'cli-witness.py')])
cmd('oc-cli-output-policy',['python3',str(O/'cli-output-policy.py')])
cmd('oc-cli-public-apply',['git','apply',str(O/'cli-fault.patch')]);cmd('oc-cli-public-fault',['python3',str(O/'cli-witness.py')],1);restore('src/cli/index.ts')
cmd('oc-graph-geometry-baseline',['bun',str(O/'bundle-witness.ts')])
cmd('oc-graph-geometry-apply',['git','apply',str(O/'graph-fault.patch')]);cmd('oc-graph-geometry-fault',['bun',str(O/'bundle-witness.ts')],1);restore('src/layout/passes/edge-bundling.ts')
cmd('oc-graph-geometry-permitted-apply',['git','apply',str(O/'graph-permitted.patch')]);cmd('oc-graph-geometry-permitted',['bun',str(O/'bundle-witness.ts')]);restore('src/layout/passes/edge-bundling.ts')
cmd('oc-public-restored-diff',['git','diff','--exit-code','HEAD'])
(E/'openclaw-public-verification.json').write_text(json.dumps({'scope':'Parent execution of reviewed public CLI and geometry witnesses against clean/fault/permitted variants','results':rows},indent=2)+'\n')
