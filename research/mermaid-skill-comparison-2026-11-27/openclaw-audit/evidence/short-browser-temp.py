"""Chromium needs a short Unix socket address; all backing files remain in this lane."""
from pathlib import Path
import os,sys,subprocess
lane=Path(__file__).resolve().parents[1]
tmp=lane/'scratch'/'tmp'
config=lane/'cache'/'chromium-config'
config.mkdir(exist_ok=True)
fd=os.open(tmp,os.O_RDONLY|os.O_DIRECTORY)
try:
 env=dict(os.environ, TMPDIR=f'/proc/{os.getpid()}/fd/{fd}', XDG_CONFIG_HOME=str(config))
 res=subprocess.run(['bun',str(lane/'evidence'/'color-witness.cjs')],env=env)
finally: os.close(fd)
sys.exit(res.returncode)
