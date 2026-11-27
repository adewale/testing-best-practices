"""Rebuild immutable validation inputs from the retained source and sealed diff."""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
NAMES={'B01':'agentic-mermaid','B02':'keyboardia','B03':'pda'}
for row in json.loads((HERE/'generation-map.json').read_text()):
 if row['phase']!='B':continue
 ident=row['id'];out=HERE/'outputs'/ident;dest=HERE/'candidate-snapshots'/ident
 if not (out/'disposition.json').exists() or dest.exists():continue
 source=ROOT/'preparation'/NAMES[row['case']]/'participant/repo'
 dest.parent.mkdir(exist_ok=True);shutil.copytree(source,dest)
 subprocess.run(['git','-C',str(dest),'init','--template=','-q'],check=True)
 patch=out/'patch.diff'
 subprocess.run(['git','-C',str(dest),'apply','--binary','--allow-empty',str(patch)],check=True)
 files={p.relative_to(dest).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(dest.rglob('*')) if p.is_file() and '.git' not in p.relative_to(dest).parts}
 receipt={'case':row['case'],'subject_id':ident,'input':'frozen participant source plus immutable sealed patch','patch_sha256':sha256(patch.read_bytes()).hexdigest(),'files':files}
 (out/'candidate-snapshot.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(ident,len(files),'files rebuilt')
