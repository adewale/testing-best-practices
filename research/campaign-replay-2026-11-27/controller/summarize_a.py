"""Decode only after every historical-case blind judgment has been sealed."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
jobs=[r for r in json.loads((HERE/'judge-map.json').read_text()) if r['phase']=='A']
assert len(jobs)==9 and all((HERE/'judgments'/r['id']/'receipt.json').is_file() for r in jobs)
subjects={r['id']:r for r in json.loads((HERE/'generation-map.json').read_text())}
cases={r['id']:r for r in json.loads((HERE/'historical-cases.json').read_text())}
totals={arm:{'PASS':0,'FAIL':0,'UNCERTAIN':0,'INVALID':0} for arm in ['none','pr41','candidate','openclaw']}
rows=[];failures=[];disagreements=[]
for job in jobs:
 folder=HERE/'judgments'/job['id']; data=(folder/'verdict.json').read_bytes(); receipt=json.loads((folder/'receipt.json').read_text());assert sha256(data).hexdigest()==receipt['sha256']
 verdict=json.loads(data);assert verdict['case']==job['case'];expected={r['blind_id']:r['subject_id'] for r in job['candidates']}
 assert len(verdict['candidates'])==4 and set(r['id'] for r in verdict['candidates'])==set(expected)
 for result in verdict['candidates']:
  subject=subjects[expected[result['id']]]; items=result['criteria'];required=set(range(1,len(cases[job['case']]['criteria'])+1));assert len(items)==len(required) and {r['criterion'] for r in items}==required
  assert all(r['verdict'] in {'PASS','FAIL','UNCERTAIN'} for r in items)
  computed='FAIL' if any(r['verdict']=='FAIL' for r in items) else 'UNCERTAIN' if any(r['verdict']=='UNCERTAIN' for r in items) else 'PASS'
  if result['overall']!=computed:disagreements.append({'case':job['case'],'blind_id':result['id'],'reported':result['overall'],'computed':computed})
  totals[subject['arm']][computed]+=1
  row={'case':job['case'],'arm':subject['arm'],'subject_id':subject['id'],'blind_id':result['id'],'reported_overall':result['overall'],'computed_overall':computed,'judge_id':job['id']};rows.append(row)
  if computed!='PASS':failures.append({**row,'criteria':[r for r in items if r['verdict']!='PASS']})
output={'decoded_utc':datetime.now(timezone.utc).isoformat(),'scheduled':36,'returned':36,'judged':36,'cases':9,'replicates':1,'totals':totals,'rows':rows,'failures':failures,'arithmetic_disagreements':disagreements,'scope':'Frozen planning cases and same-family blind judgments; no autonomous prevention or population-level uplift inference.'}
target=HERE/'analysis-a.json';assert not target.exists();target.write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps({'totals':totals,'failures':failures,'arithmetic_disagreements':disagreements},indent=2))
