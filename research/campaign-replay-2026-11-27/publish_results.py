"""Publish retained public study artifacts after all allocated attempts are sealed."""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil

EXCLUDE={'.git','node_modules','__pycache__','.wrangler','.vite','.vite-temp','.audit-xdg'}

def members(root):
 for parent,dirs,names in os.walk(root):
  dirs[:]=sorted(d for d in dirs if d not in EXCLUDE)
  for name in sorted(names):
   p=Path(parent)/name
   if p.is_symlink():continue
   if p.is_file() and not name.endswith('.pyc'):yield p.relative_to(root),p

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--study-root',type=Path,default=Path(__file__).resolve().parent);p.add_argument('--destination',type=Path,required=True);p.add_argument('--preview',action='store_true');a=p.parse_args()
root=a.study_root.resolve();dest=a.destination.resolve();control=root/'controller'
subjects=json.loads((control/'generation-map.json').read_text());judges=json.loads((control/'judge-map.json').read_text())
assert len(subjects)==48 and len(judges)==12
if not a.preview:
 assert all((control/'outputs'/r['id']/'disposition.json').exists() for r in subjects),'Unsealed subject attempt'
 assert all((control/'judgments'/r['id']/'receipt.json').exists() for r in judges),'Unsealed judge attempt'
selected={}
for folder in ['launches','judge-launches','judgments','outputs','baselines']:
 path=control/folder
 if path.exists():
  for rel,src in members(path):selected[Path('controller')/folder/rel]=src
names=['analysis-a.json','analysis-b.json','summarize_a.py','summarize_b.py','seal_b.py','seal_judge.py','snapshot_candidates.py','environment-event.json','environment-event-2.json','agent-assignments.json','public-input-verification.json','checkpoint-ci.json','post-followup-ci.json','case-links.md','phase-b-output-seal.json','judgments-seal.json','execution.json']
for name in names:
 src=control/name
 if src.exists():selected[Path('controller')/name]=src
for rel,src in members(root/'judges'):selected[Path('judges')/rel]=src
if a.preview:
 print(json.dumps({'files':len(selected),'bytes':sum(s.stat().st_size for s in selected.values()),'missing_subjects':[r['id'] for r in subjects if not (control/'outputs'/r['id']/'disposition.json').exists()],'missing_judges':[r['id'] for r in judges if not (control/'judgments'/r['id']/'receipt.json').exists()]},indent=2));raise SystemExit(0)
index={}
for rel,src in sorted(selected.items()):
 assert src.stat().st_size<16*1024*1024, f'Review large artifact {rel}'
 target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
 data=target.read_bytes();index[rel.as_posix()]={'sha256':sha256(data).hexdigest(),'bytes':len(data)}
(dest/'evidence-index.json').write_text(json.dumps({'scope':'Allocated trial/judge artifacts and technical verification; frozen source archives have their own index. Runtime dependencies and mutable caches excluded.','excluded_runtime_directories':sorted(EXCLUDE),'files':index},indent=2)+'\n')
if Path(__file__).resolve()!=(dest/'publish_results.py').resolve():shutil.copyfile(Path(__file__),dest/'publish_results.py')
print(json.dumps({'published_files':len(index),'bytes':sum(r['bytes'] for r in index.values())},indent=2))
