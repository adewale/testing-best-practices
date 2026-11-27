"""Technical follow-up. All temporary variant trees live below this script."""
import argparse
import csv
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


WORK = Path(__file__).resolve().parent
DELIVERY = WORK.parent
ROOT = DELIVERY.parents[2]
PREP = ROOT / 'preparation/keyboardia'
BASE = PREP / 'participant/repo'
CANDIDATE = ROOT / 'controller/candidate-snapshots' / DELIVERY.name
BAR = 'app/src/components/TransportBar.tsx'
DEMO = 'app/scripts/demo-sessions/whisper-to-roar.json'
OLD = ['src/components/tempo-change.test.ts', 'src/components/swing-control.test.ts']
NEW = 'src/components/TransportBar.test.tsx'
LOCK = '/tmp/test-audit-v2-docker.lock'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def artifact(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = value if isinstance(value, bytes) else (json.dumps(value, indent=2) + '\n').encode()
    if path.exists():
        assert path.read_bytes() == data, f'Existing evidence differs: {path}'
    else:
        with path.open('xb') as handle:
            handle.write(data)


def edit(text, old, new, count=1):
    assert text.count(old) == count, (old, text.count(old))
    return text.replace(old, new)


def stimulus(text, which):
    if which == 'touch_swap':
        for prop, bounds, original, wrong in [('tempo', '60, 180', 'Tempo', 'Swing'), ('swing', '0, 100', 'Swing', 'Tempo')]:
            line = f"onTouchMove={{(e) => handleDragMove(e, '{prop}', {bounds}, on{original}Change)}}"
            text = edit(text, line, line.replace('on' + original + 'Change', 'on' + wrong + 'Change'))
    elif which == 'mouse_guards':
        text = edit(text, 'onMouseMove={(e) => e.buttons === 1 && ', 'onMouseMove={(e) => ', 2)
    elif which == 'private_adapter':
        marker = 'interface TransportBarProps {'
        config = ('const tempoDrag = { sensitivity: TEMPO_DRAG_SENSITIVITY, min: 60, max: 180 };\n'
                  'const swingDrag = { sensitivity: SWING_DRAG_SENSITIVITY, min: 0, max: 100 };\n\n')
        text = edit(text, marker, config + marker)
        text = edit(text, "    type: 'tempo' | 'swing',\n    min: number,\n    max: number,\n",
                    '    control: { sensitivity: number; min: number; max: number },\n')
        text = edit(text, "    const sensitivity = type === 'tempo' ? TEMPO_DRAG_SENSITIVITY : SWING_DRAG_SENSITIVITY;\n", '')
        text = edit(text, '      sensitivity,\n      min,\n      max,', '      control.sensitivity,\n      control.min,\n      control.max,')
        text = edit(text, "handleDragMove(e, 'tempo', 60, 180,", 'handleDragMove(e, tempoDrag,', 2)
        text = edit(text, "handleDragMove(e, 'swing', 0, 100,", 'handleDragMove(e, swingDrag,', 2)
    elif which == 'demo_out_of_scale':
        original = json.loads(text)
        track = original['state']['tracks'][0]
        assert (track['sampleId'],track['steps'][0],track['parameterLocks'][0]['pitch'],track['transpose']) == ('sampled:string-section', True, 2, 0)
        text = edit(text, '"pitch": 2,\n            "volume": 0.3', '"pitch": 3,\n            "volume": 0.3')
        track['parameterLocks'][0]['pitch'] = 3
        assert original == json.loads(text)
    else:
        raise ValueError(which)
    return text


def u(files):
    return {'cwd': '.', 'args': ['/case/runtime/run-unit.sh', '--reporter=verbose', *files]}


def rows():
    output = []
    for label, description in {
        'clean': 'Pinned production on the original and submitted test suites.',
        'touch_swap': 'EXPLORATORY fault: swap only the two touch-move callbacks at the mobile sliders; preserve values, selectors, mouse callbacks and drag calculation.',
        'mouse_guards': 'EXPLORATORY fault: remove only the primary-button check from both mouse-move adapters. The pinned controls explicitly guard on buttons === 1.',
        'private_adapter': 'EXPLORATORY allowed change: replace the private move handler’s positional type/bounds and conditional sensitivity lookup with per-control objects. All public behavior, limits, sensitivity, arithmetic and callback bindings are identical.',
    }.items():
        for tree, files in [('original', OLD), ('candidate', [NEW, *OLD])]:
            output.append((label+'_'+tree, tree, label, u(files), description))
    output.extend([
        ('new_file_only','candidate','clean',u([NEW]),'New registered test in isolation, with the existing real unit project and actual added file.'),
        ('unit_discovery','candidate','clean',{'cwd':'app','args':['node','node_modules/vitest/vitest.mjs','list','--project','unit','--filesOnly']},'Unfiltered file discovery in the real CI unit project. This command lists files and does not execute the entire upstream suite.'),
        ('demo_clean','candidate','clean',u(['src/data/phase44-demo-session.test.ts']),'Clean control for the submitted open demo finding.'),
        ('demo_out_of_scale','candidate','demo_out_of_scale',u(['src/data/phase44-demo-session.test.ts']),'EXPLORATORY diagnostic for an open finding, no candidate repair: active first string lock changed from pitch offset 2 to 3, leaving scale, range and all other fields intact.'),
        ('seed_45182094013','candidate','valid_schedule',{'cwd':'.','args':['/case/runtime/run-worker.sh','--reporter=verbose','state-machine-fuzz.test.ts','overlap-fuzz.test.ts','eviction-recovery.test.ts']},'Existing frozen seed 45182094013, both seed variables; select the same three submitted suites to check the quota and the named preexisting Worker keepers. No variant of the frozen stimulus.'),
        ('default_units','candidate','clean',{'cwd':'.','args':['/case/runtime/run-unit.sh']},'Prepared default 23-file selection, including the preexisting pending-save tests. Clean original 343 recorded in the frozen preparation.'),
    ])
    return output


def integrity():
    disposition=json.loads((DELIVERY/'disposition.json').read_text())
    for name, expected in disposition['files_sha256'].items():
        assert digest((DELIVERY/name).read_bytes())==expected
    snapshot=json.loads((DELIVERY/'candidate-snapshot.json').read_text())
    def hash_tree(root):
        return {str(path.relative_to(root)):digest(path.read_bytes()) for path in root.rglob('*') if path.is_file() and '.git' not in path.relative_to(root).parts}
    current=hash_tree(CANDIDATE)
    assert current==snapshot['files']
    original=hash_tree(BASE)
    delta={path for path in current.keys()|original.keys() if current.get(path)!=original.get(path)}
    assert delta=={'app/'+NEW,'app/'+OLD[0],'app/'+OLD[1],'app/e2e/core.spec.ts','app/e2e/phase3-refactoring.spec.ts'}
    with (PREP/'participant/sample.tsv').open() as handle:
        sample=list(csv.DictReader(handle,delimiter='\t'))
    for record in sample:
        body=(BASE/record['path']).read_bytes()
        assert str(len(body))==record['bytes']
        blob=b'blob '+str(len(body)).encode()+b'\0'+body
        assert hashlib.sha1(blob).hexdigest()==record['git_blob_sha1']
    return {'candidate_files_verified':len(current),'original_files':len(original),'changed_files':sorted(delta),
            'sampled_git_blobs_checked_on_original':len(sample), 'sealed_checksums':disposition['files_sha256'],
            'snapshot_manifest_sha256':digest((DELIVERY/'candidate-snapshot.json').read_bytes())}


def run_row(row):
    name, tree, variant, command, _ = row
    dest=WORK/'runs'/name
    command_file=dest/'command.json'
    raw=dest/'raw'
    if (dest/'driver.log').exists() or raw.exists():
        print(f'{name}: previous attempt preserved', flush=True)
        return
    artifact(command_file,command)
    root=BASE if tree=='original' else CANDIDATE
    with tempfile.TemporaryDirectory(prefix='scratch-',dir=WORK) as td:
        repo=root
        if variant not in ('clean','valid_schedule'):
            file=DEMO if variant=='demo_out_of_scale' else BAR
            repo=Path(td)/'repo'
            shutil.copytree(root,repo,ignore=shutil.ignore_patterns('.git'))
            before=(repo/file).read_text()
            after=stimulus(before,variant)
            (repo/file).write_text(after)
            artifact(WORK/'mutations'/(variant+'.diff'),''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+file,tofile='b/'+file)).encode())
            artifact(dest/'variant.json',{'changed_file':file,'old_sha256':digest(before.encode()),'new_sha256':digest(after.encode())})
        scenario=['--scenario','seed','--case','valid_schedule'] if variant=='valid_schedule' else ['--scenario','clean']
        args=['flock',LOCK,sys.executable,str(PREP/'postcandidate.py'),'--repo',str(repo),*scenario,
              '--command-json',str(command_file),'--out',str(raw),'--timeout','240']
        print(f'{name}: acquiring shared Docker lock',flush=True)
        with (dest/'driver.log').open('xb') as handle:
            result=subprocess.run(args,stdout=handle,stderr=subprocess.STDOUT)
        print(f'{name}: driver {result.returncode}',flush=True)
        if not (raw/'results.json').is_file():
            raise RuntimeError(f'{name}: no results from frozen driver')
        report=json.loads((raw/'results.json').read_text())
        if not all(value.get('state')=='observed' for value in report.values()):
            raise RuntimeError(f'{name}: infrastructure failure retained in {raw}')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('names',nargs='*')
    p.add_argument('--prepare',action='store_true')
    args=p.parse_args()
    cases=rows()
    artifact(WORK/'integrity.json',integrity())
    artifact(WORK/'plan.json',{'scope':'Technical verification. Only the candidate complete tree and pristine pinned comparator are used. Open-ended mobile controls are exploratory, separate from the published frozen sync, grader and seed controls.','claimed_boundary':'Four self-generated callback cases replaced by four jsdom cases. Exactly two new touch failures on swapped callbacks, exactly two mouse failures with primary guards removed and restored total 50.','expected_sensitivity':'Identity and bounds follow separate labeled sliders, dispatch and aria limits. The exact upward deltas characterize existing calibration and do not establish immutable UX requirements.','rows':[dict(zip(('run','source','stimulus','command','reason'),row)) for row in cases]})
    if args.prepare:
        return
    known={row[0] for row in cases}
    if not set(args.names)<=known:
        raise SystemExit('Unknown row')
    for row in cases:
        if not args.names or row[0] in args.names:
            run_row(row)


if __name__=='__main__':
    main()
