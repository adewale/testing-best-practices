from pathlib import Path
import json,shutil,subprocess
from capture import run
R=Path('/workspace/mermaid-skill-comparison-2026-11-27');W=R/'verification/repo';E=R/'verification/evidence';O=R/'ours-audit/evidence/probes';rows=[]
def cmd(label,argv,want=0,env=None):
 r,_,err=run(label,argv,W,env);rows.append(r)
 assert r['exit_code']==want,(label,r,err[-1500:].decode(errors='replace'))
def patch(name):cmd('ours-apply-'+name,['git','apply',str(O/(name+'.patch'))])
def restore(*paths):
 for path in paths:(W/path).write_bytes(subprocess.check_output(['git','show','HEAD:'+path],cwd=W))
font_env={'CI':'true','AM_CJK_FONT_DIR':'/usr/share/fonts/opentype/noto'}
cmd('ours-coverage-missing',['env','-u','AM_CJK_FONT_DIR','CI=true','bun','test','--coverage','src/__tests__/png-fonts.test.ts'],1)
cmd('ours-coverage-with-font',['bun','test','--coverage','src/__tests__/png-fonts.test.ts'],env=font_env)
for name in ['journey-font-choice.ts','journey-pixels.ts','source-edit-bytes.ts']:shutil.copyfile(O/name,W/('.parent-'+name))
fonts=['bun','test','src/__tests__/png-fonts.test.ts','src/__tests__/journey-svg-snapshot.test.ts','src/__tests__/agent-png-determinism.test.ts','--timeout','30000']
cmd('ours-font-choice-baseline',['bun','.parent-journey-font-choice.ts'],env=font_env)
patch('fallback-only-fonts');cmd('ours-font-fault-old',fonts,env=font_env);cmd('ours-font-choice-fault',['bun','.parent-journey-font-choice.ts'],1,font_env)
restore('src/agent/png.ts');cmd('ours-font-choice-restored',['bun','.parent-journey-font-choice.ts'],env=font_env)
color=['bun','test','src/__tests__/authored-style-color-admission.test.ts','src/__tests__/quadrant-style.test.ts','--timeout','30000']
patch('terminal-error-wrapping');cmd('ours-format-fault-old',color)
patch('color-test-request-fix');cmd('ours-format-fault-repaired',color,1)
restore('src/cli/index.ts');cmd('ours-format-repaired-clean',color)
restore('src/__tests__/authored-style-color-admission.test.ts','src/__tests__/quadrant-style.test.ts')
cmd('ours-eol-clean',['bun','.parent-source-edit-bytes.ts'])
patch('normalized-line-endings');cmd('ours-eol-fault-public',['bun','.parent-source-edit-bytes.ts'],1)
# Parent scope is the fixed source-preservation owner. The audit's separate 403-case run remains raw evidence.
owner=['bun','test','src/__tests__/agent-source-preserving-edit.test.ts','--timeout','30000']
cmd('ours-eol-fault-owner',owner)
restore('src/agent/source-projection.ts');cmd('ours-eol-restored-public',['bun','.parent-source-edit-bytes.ts']);cmd('ours-eol-restored-owner',owner)
cmd('ours-restored-diff',['git','diff','--exit-code','HEAD'])
for name in ['journey-font-choice.ts','journey-pixels.ts','source-edit-bytes.ts']:(W/('.parent-'+name)).unlink()
(E/'ours-verification.json').write_text(json.dumps({'scope':'Parent native reproduction of CI setup, font selection, format fixtures and mixed-EOL behavior; the byte-preservation parent owner selection is narrower than the auditor 403-case matrix.','results':rows},indent=2)+'\n')
print('Ours parent verification complete')
