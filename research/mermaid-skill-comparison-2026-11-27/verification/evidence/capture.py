"""Capture bounded parent verification commands; no model or test-quality scoring."""
import hashlib,json,os,pathlib,subprocess,time
ROOT=pathlib.Path(__file__).resolve().parent
BUN='/workspace/mermaid-skill-comparison-2026-11-27/toolchain/node_modules/.bin'

def run(label,argv,cwd,extra_env=None,timeout=120):
    env=os.environ.copy();env['PATH']=BUN+':/tmp/test-audit-validation/bin:'+env['PATH']
    env['BUN_INSTALL_CACHE_DIR']=str(ROOT/'private-cache')
    if extra_env:env.update(extra_env)
    start=time.monotonic()
    try:
        p=subprocess.run(argv,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
        code=p.returncode;stdout=p.stdout;stderr=p.stderr;status='completed'
    except subprocess.TimeoutExpired as e:
        code=None;stdout=e.stdout or b'';stderr=e.stderr or b'';status='timeout'
    duration=time.monotonic()-start
    (ROOT/(label+'.stdout')).write_bytes(stdout);(ROOT/(label+'.stderr')).write_bytes(stderr)
    item={'label':label,'argv':argv,'cwd':str(cwd),'extra_env':extra_env or {},'timeout_seconds':timeout,'exit_code':code,'status':status,'duration_seconds':duration,'stdout_sha256':hashlib.sha256(stdout).hexdigest(),'stderr_sha256':hashlib.sha256(stderr).hexdigest()}
    (ROOT/(label+'.receipt.json')).write_text(json.dumps(item,indent=2)+'\n')
    print(json.dumps(item));return item,stdout,stderr
