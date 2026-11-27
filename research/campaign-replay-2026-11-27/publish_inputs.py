"""Copy the frozen public research inputs without runtime dependency installs."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import tarfile

ROOT=Path(__file__).resolve().parent
DEST=None

def archive(source,target,select=None):
    target.parent.mkdir(parents=True,exist_ok=True)
    raw=io.BytesIO()
    with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,filename='') as gz:
        with tarfile.open(fileobj=gz,mode='w|',format=tarfile.PAX_FORMAT) as tar:
            for p in sorted(source.rglob('*')):
                rel=p.relative_to(source)
                if any(x in {'__pycache__','.git'} for x in rel.parts) or p.name.endswith('.pyc'): continue
                if select is not None and not select(rel,p): continue
                if not p.is_file(): continue
                if p.is_symlink(): raise ValueError(f'Unexpected input link {p}')
                data=p.read_bytes()
                info=tarfile.TarInfo(rel.as_posix());info.size=len(data);info.mode=0o755 if p.stat().st_mode&0o111 else 0o644
                info.uid=info.gid=info.mtime=0
                tar.addfile(info,io.BytesIO(data))
    data=raw.getvalue();target.write_bytes(data)
    with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as tar:
        for member in tar.getmembers():
            assert tar.extractfile(member).read()==(source/member.name).read_bytes()
    return {'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination',type=Path,required=True)
    parser.add_argument('--study-root',type=Path,default=ROOT)
    args=parser.parse_args();ROOT=args.study_root.resolve();DEST=args.destination.resolve()
    assert (ROOT/'controller/freeze.json').is_file(), 'Freeze before publishing'
    manifest={}
    for name in ['agentic-mermaid','keyboardia','pda']:
        manifest[f'inputs/{name}.tar.gz']=archive(ROOT/'preparation'/name,DEST/'inputs'/f'{name}.tar.gz')
    manifest['inputs/openclaw.tar.gz']=archive(ROOT/'openclaw',DEST/'inputs/openclaw.tar.gz')
    manifest['inputs/packets.tar.gz']=archive(ROOT/'subjects',DEST/'inputs/packets.tar.gz',
        lambda rel,p: len(rel.parts)==2 and rel.parts[1]=='packet.md' or len(rel.parts)>2 and rel.parts[1]=='guidance')
    for name in ('RUNTIME.md','runtime.json','attach-runtime.py'):
        target=DEST/'runtime-smoke/pda'/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'runtime-smoke/pda'/name,target)
    control=DEST/'controller';control.mkdir(parents=True,exist_ok=True)
    names=('build_packets.py','control_run.py','protocol.md','protocol.json','grading-a.md','grading-b.md','protocol-review.md',
        'source-manifest.json','historical-cases.json','historical-response-format.txt','generation-map.json','judge-map.json','manifest.json','freeze.json')
    for name in names: shutil.copyfile(ROOT/'controller'/name,control/name)
    (DEST/'inputs/archives.json').write_text(json.dumps(manifest,indent=2)+'\n')
    if Path(__file__).resolve() != (DEST/'publish_inputs.py').resolve():
        shutil.copyfile(Path(__file__),DEST/'publish_inputs.py')
    print(json.dumps(manifest,indent=2))
