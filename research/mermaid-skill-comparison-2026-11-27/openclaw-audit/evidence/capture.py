import argparse,datetime,fcntl,json,os,pathlib,shlex,subprocess,time
from pathlib import Path
L=Path(__file__).resolve().parents[1]
repo=L/'repo'
runtime='/workspace/mermaid-skill-comparison-2026-11-27/toolchain/node_modules/.bin:/tmp/test-audit-validation/bin'
def append(name,r):
 p=L/name
 with (L/'evidence'/(name+'.lock')).open('a') as g:
  fcntl.flock(g,fcntl.LOCK_EX)
  rows=json.loads(p.read_text()) if p.exists() else []
  rows.append(r)
  tmp=p.with_suffix('.tmp')
  tmp.write_text(json.dumps(rows,indent=2)+'\n'); tmp.replace(p)
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds')
def read(a):
 p=(repo/a.file).resolve()
 lines=p.read_text().splitlines()
 e=a.end or len(lines)
 s=a.start
 print('\n'+str(a.file)+' ('+str(len(lines))+' lines)\n'+'\n'.join(f'{i:5} {lines[i-1]}' for i in range(s,min(e,len(lines))+1)))
 append('read-ledger.json',{'path':a.file,'coverage':'full' if s==1 and e>=len(lines) else 'partial','lines':[s,min(e,len(lines))],'length':len(lines),'method':'numbered file inspection'})
def run(a):
 env=os.environ.copy();env.update(PATH=runtime+':'+env['PATH'], BUN_INSTALL_CACHE_DIR=str(L/'cache'), XDG_CACHE_HOME=str(L/'cache'/'xdg'),TMPDIR=str(L/'scratch'/'tmp'), BUN_RUNTIME_TRANSPILER_CACHE_PATH=str(L/'cache'/'transpiler'))
 (L/'scratch'/'tmp').mkdir(exist_ok=True)
 argv=a.command[1:] if a.command[:1]==['--'] else a.command
 ts=now(); t=time.monotonic(); dst=L/'evidence'/'commands'/(a.name+'.log')
 with dst.open('w') as fp:
  res=subprocess.run(argv,cwd=Path(a.cwd).resolve(),env=env,stdout=fp,stderr=subprocess.STDOUT)
 d=round(time.monotonic()-t,3); row={'id':a.name,'started_utc':ts,'elapsed_seconds':d,'cwd':str(Path(a.cwd).resolve()),'argv':argv,'command':shlex.join(argv),'exit_code':res.returncode,'artifact':str(dst.relative_to(L))}
 append('command-ledger.json',row)
 print(json.dumps(row)); print(dst.read_text(errors='replace')[:a.show])
if __name__=='__main__':
 parser=argparse.ArgumentParser()
 sub=parser.add_subparsers(dest='action',required=True)
 p=sub.add_parser('read');p.add_argument('file');p.add_argument('start',type=int,nargs='?',default=1);p.add_argument('end',type=int,nargs='?')
 p=sub.add_parser('run');p.add_argument('name');p.add_argument('--cwd',default=str(repo));p.add_argument('--show',type=int,default=30000);p.add_argument('command',nargs=argparse.REMAINDER)
 args=parser.parse_args();(read if args.action=='read' else run)(args)
