"""Seal the completed execution artifacts before constructing blind judge packets."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
rows=[r for r in json.loads((HERE/'generation-map.json').read_text()) if r['phase']=='B']
assert len(rows)==12
files={}
for row in rows:
 folder=HERE/'outputs'/row['id']
 disposition=json.loads((folder/'disposition.json').read_text())
 for name,digest in disposition['files_sha256'].items():assert sha256((folder/name).read_bytes()).hexdigest()==digest
 json.loads((folder/'behavior.json').read_text())
 for name in ('disposition.json','response.md','patch.diff','behavior.json','candidate-snapshot.json'):
  path=folder/name
  if path.exists():files[path.relative_to(HERE).as_posix()]=sha256(path.read_bytes()).hexdigest()
target=HERE/'phase-b-output-seal.json';assert not target.exists()
target.write_text(json.dumps({'sealed_utc':datetime.now(timezone.utc).isoformat(),'scope':'All twelve allocated execution attempts, including interruptions, before blind judging','files_sha256':files},indent=2)+'\n')
print('Sealed twelve execution attempts and their technical evidence')
