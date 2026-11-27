import datetime, json, os, pathlib, subprocess, sys, time, fcntl
ident, cwd, command = sys.argv[1:]
lane = pathlib.Path(__file__).resolve().parent.parent
log = lane / 'evidence' / (ident + '.log')
env = dict(os.environ)
env.update({'BUN_INSTALL_CACHE_DIR': str(lane / 'cache'), 'XDG_CACHE_HOME': str(lane / 'cache' / 'xdg'), 'TMPDIR': str(lane / 'scratch' / 'tmp'), 'CI': '1', 'NO_COLOR': '1'})
(lane / 'scratch' / 'tmp').mkdir(parents=True,exist_ok=True)
start = time.monotonic()
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
with log.open('wb') as f:
 p = subprocess.run(['bash','-o','pipefail','-c',command],stdout=f,stderr=subprocess.STDOUT,cwd=cwd,env=env)
entry = {'id': ident, 'command': command, 'cwd': cwd, 'exit': p.returncode, 'started_utc': now,'elapsed_seconds': round(time.monotonic()-start,4), 'artifact': str(log.relative_to(lane))}
ledger = lane / 'command-ledger.json'
with open(lane / 'evidence' / 'ledger.lock','a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 records = json.loads(ledger.read_text()) if ledger.exists() else []
 records.append(entry)
 tmp=ledger.with_suffix('.tmp')
 tmp.write_text(json.dumps(records,indent=2)+'\n')
 tmp.replace(ledger)
sys.stdout.buffer.write(log.read_bytes())
print('\n[exit %d, %.4fs, %s]' % (p.returncode,entry['elapsed_seconds'],entry['artifact']))
sys.exit(p.returncode)
