"""Publish sealed public audit artifacts without source/dependency worktrees."""
from pathlib import Path
from hashlib import sha256
import argparse,json,shutil

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--destination',type=Path,required=True)
a=parser.parse_args();root=Path(__file__).resolve().parent;dest=a.destination
seal=json.loads((root/'audit-output-seal.json').read_text())
selected={}
for name in ['protocol.json','task-packets.json','source-manifest.json','guidance-manifest.json','openclaw-manifest.json','SKILL-COMPARISON.md','RESULTS.md','README.md','ATTRIBUTION.md','LICENSE.Agentic-Mermaid','LICENSE.OpenClaw','audit-output-seal.json','publish.py']:
 p=root/name
 if p.exists():selected[name]=p
for folder in ['openclaw','controller-evidence','verification/evidence']:
 for p in sorted((root/folder).rglob('*')):
  if p.is_file() and not p.is_symlink() and not any(x in p.parts for x in ['__pycache__','private-cache','browser-config','node_modules','.git']) and p.suffix not in ['.pyc','.lock']:
   selected[str(p.relative_to(root))]=p
for lane in ['ours-audit','openclaw-audit']:
 for name in ['report.md','findings.json','read-ledger.json','command-ledger.json','dependency-install.log']:
  p=root/lane/name
  if p.exists():selected[str(p.relative_to(root))]=p
 for p in sorted((root/lane/'evidence').rglob('*')):
  if p.is_file() and not p.is_symlink() and not any(x in ['node_modules','.git','__pycache__'] for x in p.parts) and p.suffix not in ['.pyc','.lock']:
   selected[str(p.relative_to(root))]=p
for name,item in seal['files'].items():
 p=root/name
 assert p.exists() and sha256(p.read_bytes()).hexdigest()==item['sha256'],f'Sealed artifact changed: {name}'
index={}
for name,p in sorted(selected.items()):
 assert p.stat().st_size<8*1024*1024, f'Review large artifact: {name}'
 data=p.read_bytes();target=dest/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
 index[name]={'sha256':sha256(data).hexdigest(),'bytes':len(data)}
(dest/'evidence-index.json').write_text(json.dumps({'scope':'Public comparison and sealed model outputs, plus separately labelled parent technical checks; excludes worktrees, dependencies, caches and credentials.','files':index},indent=2)+'\n')
print(json.dumps({'published_files':len(index),'bytes':sum(x['bytes'] for x in index.values())},indent=2))
