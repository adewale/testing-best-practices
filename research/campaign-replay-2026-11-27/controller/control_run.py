#!/usr/bin/env python3
"""Controller-only launch and immutable output receipts; does not launch models."""
import argparse
from datetime import datetime, timezone, timedelta
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent

def git(repo,*args,check=True,stdin=None):
    return subprocess.run(['git','-C',str(repo),*args],check=check,capture_output=True,input=stdin)

def write(path,data):
    if path.exists(): raise SystemExit(f'Refusing to overwrite {path}')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2)+'\n')

def now(): return datetime.now(timezone.utc)

RUNTIME_DIRS = {
    'node_modules', '.git', '.vite', '.vite-temp', '.wrangler', '__pycache__',
    '.pytest_cache', '.hypothesis', '.hegel', '.venv', 'coverage',
    'playwright-report', 'test-results',
}

def submission_additions(repo, case):
    # Git does not follow directory symlinks. Limit traversal of dependency trees
    # and separately consider ignored sources so a new ignored test is retained.
    paths = ['.', *(f':(exclude,glob)**/{d}/**' for d in sorted(RUNTIME_DIRS))]
    additions = set()
    for ignored in (False, True):
        args = ['ls-files', '--others', '--exclude-standard', '-z']
        if ignored:
            args.append('--ignored')
        raw = git(repo, *args, '--', *paths).stdout
        for value in raw.split(b'\0'):
            if not value:
                continue
            path = Path(os.fsdecode(value))
            if any(part in RUNTIME_DIRS for part in path.parts):
                continue
            # Keyboardia attaches its static test assets under app/dist before launch.
            if case == 'B02' and path.parts[:2] == ('app', 'dist'):
                continue
            if ignored:
                if (path.name.endswith(('.log', '.pyc')) or path.name in {
                    '.DS_Store', '.live-identity.json', 'deployment.local.json'
                } or path.name.startswith(('.env', '.dev.vars'))):
                    continue
                if path.parts[:2] == ('interop', 'results'):
                    continue
            additions.add(value)
    return sorted(additions)

def initialize():
    rows=json.loads((HERE/'generation-map.json').read_text())
    sources=json.loads((HERE/'source-manifest.json').read_text())
    for row in rows:
        if row['phase']!='B': continue
        repo=STUDY/'subjects'/row['id']/'work/repo'
        git(repo,'init','-q')
        paths=[name[5:] for name in sources['cases_B'][row['case']]['participant_files'] if name.startswith('repo/')]
        git(repo,'add','-f','--pathspec-from-file=-','--pathspec-file-nul',stdin=b''.join(p.encode()+b'\0' for p in paths))
        git(repo,'-c','user.name=Replay Controller','-c','user.email=replay@example.invalid','commit','-qm','Frozen participant input')
        head=git(repo,'rev-parse','HEAD').stdout.decode().strip()
        write(HERE/'baselines'/f"{row['id']}.json",{'git_head':head})
    print('Initialized independent review baselines.')

def launch(identifier):
    if not (HERE/'freeze.json').exists(): raise SystemExit('Freeze required')
    row=next(r for r in json.loads((HERE/'generation-map.json').read_text()) if r['id']==identifier)
    start=now(); minutes=10 if row['phase']=='A' else 25
    deadline=start+timedelta(minutes=minutes)
    packet=STUDY/row['packet']
    message=(f'You are an independent replay subject. Read and follow only {packet}. '
             f'Your allowed directory is {packet.parent}. Do not inspect other study directories, '
             'prior reports, controller/evaluator material, network or other agents. '
             f'Your {minutes}-minute wall budget starts now; deadline {deadline.isoformat()}. '
             'Write the exact final response to response.md beside your packet and return it. '
             'For planning tasks, preserve the packet\'s JSON format and word cap. '
             'For execution tasks, leave the actual bounded change in work/repo/.')
    record={'subject_id':identifier,'phase':row['phase'],'case':row['case'],
            'controller_dispatch_utc':start.isoformat(),'deadline_utc':deadline.isoformat(),
            'budget_minutes':minutes,'requested_model':'gpt-6.2-astra','requested_reasoning_effort':'max',
            'fork_turns':'none','message':message}
    write(HERE/'launches'/f'{identifier}.json',record)
    print(message)

def seal(identifier,state):
    row=next(r for r in json.loads((HERE/'generation-map.json').read_text()) if r['id']==identifier)
    cell=STUDY/'subjects'/identifier; out=HERE/'outputs'/identifier
    if (out/'disposition.json').exists(): raise SystemExit('Already sealed')
    out.mkdir(parents=True,exist_ok=True)
    response=cell/'response.md'; hashes={}
    if response.is_file() and not response.is_symlink():
        data=response.read_bytes(); (out/'response.md').write_bytes(data)
        hashes['response.md']=sha256(data).hexdigest()
    elif state=='returned': state='returned-without-file'
    if row['phase']=='B':
        repo=cell/'work/repo'
        head=json.loads((HERE/'baselines'/f'{identifier}.json').read_text())['git_head']
        additions=submission_additions(repo,row['case'])
        if additions:
            git(repo,'--literal-pathspecs','add','-f','--intent-to-add','--pathspec-from-file=-',
                '--pathspec-file-nul',stdin=b'\0'.join(additions)+b'\0')
        diff=git(repo,'diff','--no-ext-diff','--no-textconv','--binary',head).stdout
        (out/'patch.diff').write_bytes(diff); hashes['patch.diff']=sha256(diff).hexdigest()
        (out/'git-status.txt').write_bytes(git(repo,'status','--short').stdout)
    launch_record=json.loads((HERE/'launches'/f'{identifier}.json').read_text())
    end=now()
    write(out/'disposition.json',{'state':state,'controller_sealed_utc':end.isoformat(),
        'dispatch_to_seal_seconds':(end-datetime.fromisoformat(launch_record['controller_dispatch_utc'])).total_seconds(),
        'response_file_mtime_utc':datetime.fromtimestamp(response.stat().st_mtime,timezone.utc).isoformat() if response.exists() else None,
        'files_sha256':hashes,'timing_scope':'dispatch to controller seal; includes observation delay, not precise model runtime'})
    print(f'Sealed {identifier}: {state}')

p=argparse.ArgumentParser(description=__doc__); p.add_argument('command',choices=['initialize','launch','seal']); p.add_argument('identifier',nargs='?'); p.add_argument('--state',default='returned')
a=p.parse_args()
if a.command=='initialize': initialize()
elif a.command=='launch': launch(a.identifier)
else: seal(a.identifier,a.state)
