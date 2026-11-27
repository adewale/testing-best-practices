"""Decode sealed project judgments without inventing an overall quality score."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
jobs=[r for r in json.loads((HERE/'judge-map.json').read_text()) if r['phase']=='B']
assert len(jobs)==3 and all((HERE/'judgments'/r['id']/'receipt.json').is_file() for r in jobs)
seal=json.loads((HERE/'phase-b-output-seal.json').read_text())
for name,digest in seal['files_sha256'].items():assert sha256((HERE/name).read_bytes()).hexdigest()==digest
subjects={r['id']:r for r in json.loads((HERE/'generation-map.json').read_text())}
rows=[];issues=[];states={};unavailable=[]
for job in jobs:
 folder=HERE/'judgments'/job['id'];receipt=json.loads((folder/'receipt.json').read_text())
 if receipt['state']!='returned':
  unavailable.append({'case':job['case'],'judge_id':job['id'],'state':receipt['state']})
  for member in job['candidates']:
   subject=subjects[member['subject_id']];source=HERE/'outputs'/subject['id'];disposition=json.loads((source/'disposition.json').read_text())['state'];states[disposition]=states.get(disposition,0)+1
   rows.append({'case':job['case'],'arm':subject['arm'],'subject_id':subject['id'],'blind_id':member['blind_id'],'source_disposition':disposition,'report_exists':(source/'response.md').exists(),'patch_bytes':(source/'patch.diff').stat().st_size,'judgment':None,'judge_id':job['id'],'judge_status':receipt['state']})
  continue
 data=(folder/'verdict.json').read_bytes();assert sha256(data).hexdigest()==receipt['sha256']
 verdict=json.loads(data);assert verdict['case']==job['case']
 lookup={r['blind_id']:r['subject_id'] for r in job['candidates']}
 assert len(verdict['candidates'])==4 and {r['id'] for r in verdict['candidates']}==set(lookup)
 for candidate in verdict['candidates']:
  subject=subjects[lookup[candidate['id']]];source=HERE/'outputs'/subject['id'];disposition=json.loads((source/'disposition.json').read_text())['state'];states[disposition]=states.get(disposition,0)+1
  required={'id','disposition','known_findings','novel_findings','unsupported_or_refuted_claims','repair','preservation','scope','coverage','uncertainties'}
  missing=sorted(required-set(candidate))
  if missing:issues.append({'case':job['case'],'blind_id':candidate['id'],'missing_fields':missing})
  rows.append({'case':job['case'],'arm':subject['arm'],'subject_id':subject['id'],'blind_id':candidate['id'],'source_disposition':disposition,'report_exists':(source/'response.md').exists(),'patch_bytes':(source/'patch.diff').stat().st_size,'judgment':candidate,'judge_id':job['id']})
out={'decoded_utc':datetime.now(timezone.utc).isoformat(),'allocated':12,'disposition_counts':states,'judgment_attempts':3,'completed_judgments':3-len(unavailable),'unavailable_judgments':unavailable,'judgment_schema_issues':issues,'rows':rows,'scope':'Descriptive per-case observations. No pooled quality score, population effect, or imputation of interrupted trials.'}
target=HERE/'analysis-b.json';assert not target.exists();target.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'allocated':12,'dispositions':states,'schema_issues':issues,'unavailable_judgments':unavailable,'rows':[{'case':r['case'],'arm':r['arm'],'id':r['subject_id'],'disposition':r['source_disposition']} for r in rows]},indent=2))
