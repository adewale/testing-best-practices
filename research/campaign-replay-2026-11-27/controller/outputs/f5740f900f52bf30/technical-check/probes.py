"""Fresh native Worker/app runs for the specific claims outside the frozen matrix."""
import ast
import csv
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time


HERE = Path(__file__).resolve().parent
OUTPUT = HERE.parent
TOP = HERE.parents[3]
PREP = TOP / 'preparation/keyboardia'
RUNTIME = PREP / 'participant/runtime'
BASE = PREP / 'participant/repo'
CANDIDATE = TOP / 'controller/candidate-snapshots' / OUTPUT.name
MODEL = 'app/test/integration/state-machine-fuzz.test.ts'
OWNER = 'app/src/worker/live-session.ts'
DATABASE = 'app/test/integration/known-failures.json'
DEP_APP = '/tmp/keyboardia-v2-app-deps/node_modules'
DEP_WORKER = '/tmp/keyboardia-v2-worker-deps/node_modules'
HIST = '45182094013'
OTHER = '20261127'
TITLE = 'model: read-your-writes'
MODEL_ARGS = [str(RUNTIME/'run-worker.sh'),'state-machine-fuzz.test.ts','-t',TITLE]
THREE_ARGS = [str(RUNTIME/'run-worker.sh'),'--reporter=verbose','state-machine-fuzz.test.ts','overlap-fuzz.test.ts','eviction-recovery.test.ts']
WAVE_ARGS = [str(RUNTIME/'run-unit.sh'),'--reporter=verbose','src/components/waveform-peaks.test.ts']
CASES = [
    ('stale_original',BASE,HIST,'stale',MODEL_ARGS),
    ('stale_candidate',CANDIDATE,HIST,'stale',MODEL_ARGS),
    ('candidate_trace',CANDIDATE,HIST,'trace',MODEL_ARGS),
    ('continuous_32_reference',BASE,HIST,'continuous_32',MODEL_ARGS),
    ('candidate_trace_capture',CANDIDATE,HIST,'captured_trace',MODEL_ARGS),
    ('continuous_32_capture',BASE,HIST,'captured_reference',MODEL_ARGS),
    ('missing_swing',CANDIDATE,HIST,'no_swing',MODEL_ARGS),
    ('other_seed_original',BASE,OTHER,None,MODEL_ARGS),
    ('other_seed_candidate',CANDIDATE,OTHER,None,MODEL_ARGS),
    ('private_get_representation',CANDIDATE,HIST,'equivalent_get',MODEL_ARGS),
    ('weekly_selection',CANDIDATE,HIST,None,THREE_ARGS),
    ('waveform_clean',CANDIDATE,None,None,WAVE_ARGS),
    ('waveform_flat',CANDIDATE,None,'waveform_flat',WAVE_ARGS),
    ('client_persistence_keeper',CANDIDATE,None,None,[str(RUNTIME/'run-unit.sh'),'--reporter=verbose','src/sync/session.persistence.test.ts']),
    ('promoted_clean_control',CANDIDATE,HIST,'promoted_clean',MODEL_ARGS),
    ('final_flush_model_original',BASE,HIST,'frozen_flush',MODEL_ARGS),
    ('final_flush_model_candidate',CANDIDATE,HIST,'frozen_flush',MODEL_ARGS),
]


def save(path, obj):
    data = obj if isinstance(obj,bytes) else (json.dumps(obj,indent=2)+'\n').encode()
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        assert path.read_bytes()==data, path
    else:
        with path.open('xb') as out:
            out.write(data)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def check_integrity():
    seal = json.loads((OUTPUT/'disposition.json').read_text())
    for name,h in seal['files_sha256'].items():
        assert sha((OUTPUT/name).read_bytes())==h
    attachments = OUTPUT/'submitted-artifacts'
    receipt = json.loads((attachments/'evidence-collection.json').read_text())
    found = {p.name for p in (attachments/'evidence').iterdir() if p.is_file()}
    assert found == {f['path'] for f in receipt['files']}
    for f in receipt['files']:
        b=(attachments/'evidence'/f['path']).read_bytes()
        assert sha(b)==f['sha256'] and len(b)==f['bytes']
        assert f['source_mtime_utc']<=seal['controller_sealed_utc']
    def tree(repo):
        return {str(path.relative_to(repo)):sha(path.read_bytes()) for path in repo.rglob('*') if path.is_file() and '.git' not in path.relative_to(repo).parts}
    base=tree(BASE)
    candidate=tree(CANDIDATE)
    assert candidate==json.loads((OUTPUT/'candidate-snapshot.json').read_text())['files']
    with (PREP/'participant/source-manifest.tsv').open() as f:
        assert base=={r['path']:r['sha256'] for r in csv.DictReader(f,delimiter='\t')}
    assert set(base)==set(candidate)
    delta=[p for p in base if base[p]!=candidate[p]]
    assert delta==[MODEL]
    prep_manifest=json.loads((PREP/'freeze-manifest.json').read_text())
    for k,v in prep_manifest['evaluator_sha256'].items():
        assert sha((PREP/'evaluator'/k).read_bytes())==v
    subprocess.run(['git','-C',str(BASE),'apply','--check','--whitespace=error',str(OUTPUT/'patch.diff')],check=True)
    with (PREP/'participant/sample.tsv').open() as f:
        sampled=list(csv.DictReader(f,delimiter='\t'))
    for row in sampled:
        b=(BASE/row['path']).read_bytes()
        assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['git_blob_sha1']
    evidence={'candidate_and_pristine_files':len(candidate),'unique_changed_path':MODEL,'changed_model_sha256':candidate[MODEL],
              'base_model_sha256':base[MODEL],'sampled_blob_ids_checked':len(sampled),'sealed_sha256':seal['files_sha256'],
              'submitted_evidence_files_verified':len(found),'submitted_artifact_earliest_mtime':min(f['source_mtime_utc'] for f in receipt['files']),
              'submitted_artifact_latest_mtime':max(f['source_mtime_utc'] for f in receipt['files']),
              'submitted_artifact_collection':receipt['collected_utc'],'controller_sealed_utc':seal['controller_sealed_utc'],
              'all_frozen_evaluator_hashes_matched':True,'patch_applies_to_pristine_with_whitespace_error_check':True}
    save(HERE/'integrity.json', evidence)
    return evidence


def edit(repo, relative, old, new, dest):
    file=repo/relative
    original=file.read_text()
    assert original.count(old)==1, (relative,original.count(old))
    changed=original.replace(old,new)
    file.write_text(changed)
    patch=difflib.unified_diff(original.splitlines(True),changed.splitlines(True),fromfile='a/'+relative,tofile='b/'+relative)
    save(dest,''.join(patch).encode())
    return sha(original.encode()),sha(changed.encode())


def mutate(repo, which, dest):
    if not which: return
    if which=='stale':
        return edit(repo,OWNER,'      state: this.state,  // Override with DO state (includes pending changes)',
                    '      state: kvSession.state,  // Diagnostic stale persisted state',dest/'stimulus.diff')
    if which=='frozen_flush':
        script=ast.parse((PREP/'postcandidate.py').read_text())
        known,=[ast.literal_eval(node.value) for node in script.body if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=='SEED_MUTATION' for target in node.targets)]
        return edit(repo,OWNER,known,known.replace('await this.saveToKV();','void this.state;'),dest/'stimulus.diff')
    if which=='no_swing':
        line="  swingArb.map((swing) => new SessionCommand({ kind: 'ws_swing', swing })),\n"
        return edit(repo,MODEL,line,'',dest/'stimulus.diff')
    if which=='equivalent_get':
        old='    const response = {\n      ...kvSession,\n      state: this.state,  // Override with DO state (includes pending changes)\n      immutable: this.immutable,\n    };'
        new='    const response = Object.assign({}, kvSession, {\n      state: this.state,\n      immutable: this.immutable,\n    });'
        return edit(repo,OWNER,old,new,dest/'stimulus.diff')
    if which=='waveform_flat':
        return edit(repo,'app/src/components/Waveform.tsx','    mins[i] = min;\n    maxs[i] = max;',
                    '    mins[i] = 0;\n    maxs[i] = 0;',dest/'stimulus.diff')
    if which=='promoted_clean':
        before=(repo/DATABASE).read_text()
        actual=(HERE/'exploratory/stale_candidate/promoted-known-failures.json').read_text()
        assert json.loads(before)['stateMachine']==[] and json.loads(actual)['stateMachine']==[[{'kind':'ws_tempo','tempo':60}]]
        return edit(repo,DATABASE,before,actual,dest/'stimulus.diff')
    if which in ('trace','continuous_32'):
        anchor='          await fc.asyncModelRun(() => run, commands);'
        result=edit(repo,MODEL,anchor,anchor+'\n          console.log("VERIFY_SCHEDULE=" + JSON.stringify({ actions: replayableActions(commands), accepted: coverage.accepted, dirty: coverage.dirtyDisconnects, byKind: coverage.byKind }));',dest/'logging.diff')
        if which=='continuous_32':
            return edit(repo,MODEL,'        numRuns: RUNS_PER_SEED,','        numRuns: 32,',dest/'reference-count.diff')
        return result
    if which in ('captured_trace','captured_reference'):
        edit(repo,MODEL,'const commandArbs = [','const verifierScheduleTrace: string[] = [];\nconst commandArbs = [',dest/'capture-buffer.diff')
        original='          await fc.asyncModelRun(() => run, commands);'
        edit(repo,MODEL,original,original+'\n          verifierScheduleTrace.push(JSON.stringify({ actions: replayableActions(commands), accepted: coverage.accepted, dirty: coverage.dirtyDisconnects, byKind: coverage.byKind }));',dest/'capture-observation.diff')
        if which=='captured_reference':
            edit(repo,MODEL,'        numRuns: RUNS_PER_SEED,','        numRuns: 32,',dest/'reference-count.diff')
        end='  assertModelCoverage(coverage);' if which=='captured_reference' else '  expect(missingModelCoverage(coverage), JSON.stringify(coverage)).toEqual([]);'
        return edit(repo,MODEL,end,end+'\n  throw new Error("VERIFY_CAPTURE_COMPLETE\\n" + verifierScheduleTrace.map((value) => "VERIFY_SCHEDULE=" + value).join("\\n"));',dest/'capture-output.diff')
    raise ValueError(which)


def observe(args,cwd,env,dest):
    started=time.monotonic()
    try:
        proc=subprocess.run(args,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=195)
        code, data=proc.returncode,proc.stdout
    except subprocess.TimeoutExpired as exc:
        code,data=124,(exc.stdout or b'')+b'\nVERIFIER TIME LIMIT\n'
    save(dest,data)
    txt=re.sub('\x1b\\[[0-9;]*m','',data.decode(errors='replace'))
    result={'exit':code,'wall_seconds':round(time.monotonic()-started,3),'log':str(dest.relative_to(OUTPUT)),'sha256':sha(data)}
    for key,pattern in [('test_files','Test Files'),('tests','Tests')]:
        m=re.search(r'^\s*'+pattern+r'\s+([0-9][^\n]*)',txt,re.M)
        if m: result[key]=m.group(1).strip()
    return result,txt


def run(row):
    name,source,seed,variant,args=row
    dest=HERE/'exploratory'/name
    if dest.exists():
        raise SystemExit('Existing attempt kept: '+name)
    dest.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix='scratch-',dir=HERE) as scratch:
        repo=Path(scratch)/'repo'
        shutil.copytree(source,repo,ignore=shutil.ignore_patterns('.git','node_modules','.vite','.wrangler','dist'))
        hashes=mutate(repo,variant,dest)
        attach=[sys.executable,str(RUNTIME/'attach.py'),'--repo',str(repo),'--app-modules',DEP_APP,'--worker-modules',DEP_WORKER]
        env={**os.environ,'KEYBOARDIA_REPO':str(repo),'NO_COLOR':'1','FORCE_COLOR':'0','WRANGLER_LOG_PATH':str(Path(scratch)/'logs'),'WRANGLER_SEND_METRICS':'false','NPM_CONFIG_UPDATE_NOTIFIER':'false'}
        for var in ('FUZZ_SEEDS','FC_SEED'):
            env.pop(var,None)
            if seed is not None: env[var]=seed
        with (dest/'attach.log').open('xb') as log:
            subprocess.run(attach,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        result,txt=observe(args,repo,env,dest/'run.log')
        result.update({'source':'original' if source==BASE else 'submitted','stimulus':variant,'seed':seed,'selected_command':[a.replace(str(RUNTIME),'runtime') for a in args]})
        if hashes: result['stimulus_file_hash_before_after']=hashes
        if variant in ('trace','continuous_32','captured_trace','captured_reference'):
            data=[json.loads(line.split('VERIFY_SCHEDULE=',1)[1]) for line in txt.splitlines() if line.startswith('VERIFY_SCHEDULE=')]
            save(dest/'schedule-trace.json',data)
        if name=='stale_candidate':
            cli=['node','node_modules/tsx/dist/cli.mjs','scripts/promote-pbt-counterexamples.ts',str(dest/'run.log'),'test/integration/known-failures.json']
            result['promotion'],_=observe(cli,repo/'app',env,dest/'promotion.log')
            save(dest/'promoted-known-failures.json',(repo/DATABASE).read_bytes())
            result['known_replay'],_=observe(MODEL_ARGS,repo,env,dest/'known-replay.log')
        save(dest/'result.json',result)
        print(name,result['exit'],result.get('tests'),flush=True)


if __name__=='__main__':
    check_integrity()
    for r in CASES:
        if len(sys.argv)==1 or r[0] in sys.argv[1:]:
            run(r)
