import json
import subprocess
import sys
from pathlib import Path

out = Path(__file__).resolve().parent
top = out.parents[3]
p = top / 'preparation/keyboardia'
candidate = top / 'controller/candidate-snapshots' / out.parent.name
old = p / 'participant/repo'
app = '/tmp/keyboardia-v2-app-deps/node_modules'
worker = '/tmp/keyboardia-v2-worker-deps/node_modules'
controls = ['default_model','valid_schedule','persistence_original','persistence_fault']
plan = {'claim':'The existing registered Worker model keeps its workload floor (100 commands, both WS write kinds and a dirty disconnect), drawing successive schedules from the same seed for at most one additional batch. Seed 45182094013 should turn green; the original fixed final-save keeper and property failure/shrink/replay still reject damaged storage behavior. No production or configuration changes.',
        'prepared_controls': controls,
        'supplemental_exploratory':'Check the submitted stale-GET fault on each tree, CLI promotion and replay, deliberate absence of WS swing generation, fixed non-historical seed 20261127, equivalent private GET response construction, same-stream offsets and exact observed work on the historical seed, native CI three-file selection and waveform zero-peaks open finding. These are separate from frozen inputs and outcomes.'}
planpath=out/'plan.json'
if planpath.exists(): assert json.loads(planpath.read_text())==plan
else: planpath.write_text(json.dumps(plan,indent=2)+'\n')
if sys.argv[1]=='native':
 for label,repo,flag in [('original',old,'--assert-original'),('candidate',candidate,'--assert-repaired')]:
  dest=out/('frozen-native-'+label)
  if dest.exists(): raise SystemExit('Previous frozen native attempt preserved')
  dest.mkdir()
  cmd=[sys.executable,str(p/'evaluator/evaluate-seed.py'),'--repo',str(repo),'--out',str(dest/'raw'),'--app-modules',app,'--worker-modules',worker,flag]
  with (dest/'driver.log').open('xb') as log: proc=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
  print(label,proc.returncode,flush=True)
  if proc.returncode: raise SystemExit(proc.returncode)
elif sys.argv[1]=='docker':
 for case in controls:
  dest=out/'frozen-offline-candidate'/case
  if dest.exists(): raise SystemExit('Previous frozen Docker attempt preserved')
  dest.mkdir(parents=True)
  cmd=['flock','/tmp/test-audit-v2-docker.lock',sys.executable,str(p/'postcandidate.py'),'--repo',str(candidate),'--out',str(dest/'raw'),'--scenario','seed','--case',case]
  with (dest/'driver.log').open('xb') as log: proc=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
  print(case,proc.returncode,flush=True)
  if proc.returncode: raise SystemExit(proc.returncode)
else: raise SystemExit('Specify native or docker')
