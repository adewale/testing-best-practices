"""Operator-only checks. Runs as a command inside a fresh frozen postcandidate container."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys

TEST = Path('app/test/integration/state-machine-fuzz.test.ts')
OWNER = Path('app/src/worker/live-session.ts')
DATABASE = Path('app/test/integration/known-failures.json')
MODEL = ['/case/runtime/run-worker.sh', 'state-machine-fuzz.test.ts', '-t', 'model: read-your-writes', '--reporter=verbose']
SEED = '45182094013'


def single(text, before, after):
    assert text.count(before) == 1, before
    return text.replace(before, after)


def run_model(label, seed=None):
    env = dict(os.environ)
    if seed is not None:
        env.update(FC_SEED=seed, FUZZ_SEEDS=seed)
    child = subprocess.run(MODEL, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    body = child.stdout
    print('EXPLORATORY run=' + label + ' exit=' + str(child.returncode), flush=True)
    print(body, flush=True)
    return child.returncode, body


def coverage(body):
    return [(int(runs), json.loads(counts)) for runs, counts in re.findall(r'\[stateMachine\] seeds=\S+ runsPerSeed=(\d+) coverage=(\{[^\n]+\})', body)]


def compare_stream():
    source = TEST.read_text()
    line = 'await fc.asyncModelRun(() => run, commands);'
    traced = single(source, line, line + "\n        console.info('VERIFIER_SCHEDULE=' + JSON.stringify(replayableActions(commands)));")
    TEST.write_text(traced)
    rc, split = run_model('candidate-split', SEED)
    assert rc == 0
    # Reference uses fast-check's ordinary run from the same seed with no path option.
    ref = single(traced, 'path: String(offset),\n      numRuns: RUNS_PER_SEED,', 'numRuns: 2 * RUNS_PER_SEED,')
    TEST.write_text(ref)
    rc, contiguous = run_model('single-60-reference', SEED)
    assert rc == 0
    pattern = r'^VERIFIER_SCHEDULE=(.+)$'
    series = [[json.loads(line) for line in re.findall(pattern, body, re.M)] for body in (split, contiguous)]
    assert len(series[0]) == len(series[1]) == 60
    assert series[0] == series[1]
    def digest(values):
        return hashlib.sha256(json.dumps(values, separators=(',', ':')).encode()).hexdigest()
    first, second = series[0][:30], series[0][30:]
    assert first != second and [sum(map(len, partition)) for partition in (first, second)] == [99, 135]
    print('VERIFIER_STREAM=' + json.dumps({'peer':'single ordinary fast-check invocation, same seed, 60 schedules, no path option','matched':len(series[0]),'commands':[99,135],'schedule_sha256':[digest(first),digest(second),digest(series[0])]}), flush=True)


def cap_swing():
    healthy = OWNER.read_text()
    anchor = "        this.validateAndRepairState('restApiPatch');"
    OWNER.write_text(single(healthy, anchor, anchor + '\n        this.state.swing = Math.min(this.state.swing, 99);'))
    rc, body = run_model('cap-REST-PATCH-at-99', SEED)
    assert rc == 1 and 'expected 99 to be 100' in body and 'Coverage budget exhausted' not in body
    assert [n for n,_ in coverage(body)] == [30]
    event = re.search(r'^PBT_COUNTEREXAMPLE=(.+)$', body, re.M)
    assert event is not None
    record = json.loads(event[1])
    assert record == {'lane':'stateMachine','example':[{'kind':'rest_patch_state','tempo':60,'swing':100}],'seed':-2062546243,'path':'51:1','shrinks':1}, record
    log = Path('/tmp/keyboardia-verified-failure.log')
    log.write_text(body)
    assert json.loads(DATABASE.read_text())['stateMachine'] == []
    subprocess.run(['app/node_modules/.bin/tsx','app/scripts/promote-pbt-counterexamples.ts',str(log),str(DATABASE)],check=True)
    promoted = json.loads(DATABASE.read_text())['stateMachine']
    assert promoted == [record['example']], promoted
    rc, replay = run_model('actual-promotion-replay-under-42', '42')
    assert rc == 1 and 'known-failure #0 regressed: expected 99 to be 100' in replay and not coverage(replay) and 'PBT_COUNTEREXAMPLE=' not in replay
    OWNER.write_text(healthy)
    rc, restored = run_model('same-promoted-example-healthy-under-42', '42')
    assert rc == 0 and coverage(restored)
    print('VERIFIER_PROMOTION=' + json.dumps({'first_stimulus':record,'stored':promoted,'replay_seed':42,'faulted_replay_exit':1,'restored_replay_exit':0}),flush=True)


def remove_hibernation():
    anchor = "  fc.constant(new SessionCommand({ kind: 'hibernate' })),\n"
    TEST.write_text(single(TEST.read_text(), anchor, ''))
    status, _ = run_model('remove-only-hibernate-arbitrary')
    return status


def clean_disconnects():
    anchor = '  check(model: Readonly<SessionModel>): boolean {'
    rule = "\n    if (this.action.kind === 'disconnect') return model.connected && model.tempo === model.kvTempo && model.swing === model.kvSwing && model.name === model.kvName;"
    TEST.write_text(single(TEST.read_text(), anchor, anchor + rule))
    status, output = run_model('only-clean-graceful-disconnects', SEED)
    stats = coverage(output)
    assert status == 1 and 'Coverage budget exhausted' in output and [n for n,_ in stats] == [30,60,90]
    last = stats[-1][1]
    assert last['accepted'] >= 100 and last['dirtyDisconnects'] == 0 and min(last['byKind'].values()) > 0
    return status


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'stream':
        compare_stream()
    elif mode == 'promotion':
        cap_swing()
    elif mode == 'hibernate':
        sys.exit(remove_hibernation())
    elif mode == 'dirty':
        sys.exit(clean_disconnects())
    else:
        raise ValueError(mode)
