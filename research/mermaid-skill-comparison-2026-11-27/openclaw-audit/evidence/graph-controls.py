"""Compare two scratch implementations of speculative route updates."""
from pathlib import Path
import sys,subprocess
L=Path(__file__).resolve().parents[1]; W=L/'scratch'/'control'
if Path.cwd().resolve()!=W: raise ValueError('wrong checkout')
mode=sys.argv[1]
assert mode in ('fault','permitted')
path='src/layout/passes/edge-bundling.ts'
base=subprocess.check_output(['git','show','HEAD:'+path],text=True)
old="""      const clear = admittedMembers(members, candidates)
      if (clear.length === members.length) {
        for (const { edge } of members) {
          edge.points = candidates.get(edge)!
        }
        retainConstructedBundleRoutes(members.map(member => member.edge), processed)
        break
      }
      members = clear"""
if mode=='fault':
 backup='edge.points'
 apply='edge.points.splice(0, edge.points.length, ...candidates.get(edge)!)'
else:
 backup='edge.points.slice()'
 apply='edge.points = candidates.get(edge)!'
new=f"""      const previous = members.map(({{ edge }}) => {backup})
      const clear = admittedMembers(members, candidates)
      for (const {{ edge }} of members) {{
        {apply}
      }}
      if (clear.length === members.length) {{
        retainConstructedBundleRoutes(members.map(member => member.edge), processed)
        break
      }}
      for (const [index, {{ edge }}] of members.entries()) edge.points = previous[index]!
      members = clear"""
assert base.count(old)==2
(W/path).write_text(base.replace(old,new))
(L/'evidence'/('graph-'+mode+'.patch')).write_bytes(subprocess.check_output(['git','diff','--',path]))
print(mode, path)
