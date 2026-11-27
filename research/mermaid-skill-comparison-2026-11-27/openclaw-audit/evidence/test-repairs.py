from pathlib import Path
import subprocess,sys
L=Path(__file__).resolve().parents[1]; W=L/'scratch'/'control'
if Path.cwd().resolve()!=W: raise ValueError('wrong checkout')
which=sys.argv[1]
if which=='cli':
 file='src/__tests__/cli-multi-input.test.ts'
 before=subprocess.check_output(['git','show','HEAD:'+file],text=True)
 old="""    const a = tmp('flowchart TD\\n A --> B')
    const b = tmp('flowchart LR\\n X --> Y')
    const bad = tmp('not a diagram')
    const { code, out } = capture(() => runCli(['render', a, b, bad, '--format', 'ascii']))
    expect(code).toBe(0)
    const payload = JSON.parse(out)
    expect(payload.files.length).toBe(3)
    expect(payload.files[0].ok).toBe(true)
    expect(payload.files[1].ok).toBe(true)
    expect(payload.files[2].ok).toBe(false)
    expect(payload.files[2].error.code).toBe('UNKNOWN_HEADER')"""
 new="""    const first = tmp('flowchart TD\\n A[First Label] --> B')
    const bad = tmp('not a diagram')
    const last = tmp('flowchart LR\\n X[Final Label] --> Y')
    const { code, out } = capture(() => runCli(['render', first, bad, last, '--format', 'ascii']))
    expect(code).toBe(0)
    expect(JSON.parse(out).files).toEqual([
      expect.objectContaining({ index: 0, file: first, ok: true, output: expect.stringContaining('First Label') }),
      expect.objectContaining({ index: 1, file: bad, ok: false, error: expect.objectContaining({ code: 'UNKNOWN_HEADER' }) }),
      expect.objectContaining({ index: 2, file: last, ok: true, output: expect.stringContaining('Final Label') }),
    ])"""
 assert before.count(old)==1
 after=before.replace(old,new)
elif which=='graph':
 file='src/__tests__/layout-bundle-proposals.test.ts'
 before=subprocess.check_output(['git','show','HEAD:'+file],text=True)
 old='const before = edges.map(edge => edge.points)'
 old2='expect(edges[i]!.points).toBe(before[i]!)'
 assert before.count(old)==3 and before.count(old2)==3
 after=before.replace(old,'const before = structuredClone(edges.map(edge => edge.points))').replace(old2,'expect(edges[i]!.points).toEqual(before[i]!)')
else: raise ValueError(which)
(W/file).write_text(after)
(L/'evidence'/(which+'-repair.patch')).write_bytes(subprocess.check_output(['git','diff','--',file]))
print(which, file)
