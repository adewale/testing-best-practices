"""Retain an exact returned blind verdict and checksum before label decoding."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
jobs={r['id']:r for r in json.loads((HERE/'judge-map.json').read_text())}
for identifier in sys.argv[1:]:
 job=jobs[identifier];source=ROOT/'judges'/identifier/'verdict.json';assert source.is_file() and not source.is_symlink()
 data=source.read_bytes();v=json.loads(data);assert v['case']==job['case']
 assert len(v['candidates'])==4 and {r['id'] for r in v['candidates']}=={r['blind_id'] for r in job['candidates']}
 out=HERE/'judgments'/identifier;out.mkdir(parents=True,exist_ok=True);assert not (out/'receipt.json').exists()
 (out/'verdict.json').write_bytes(data)
 (out/'receipt.json').write_text(json.dumps({'state':'returned','sealed_utc':datetime.now(timezone.utc).isoformat(),'sha256':sha256(data).hexdigest(),'case':job['case'],'packet_sha256':sha256((source.parent/'packet.md').read_bytes()).hexdigest()},indent=2)+'\n')
 print('Sealed blind judgment',identifier,job['case'])
