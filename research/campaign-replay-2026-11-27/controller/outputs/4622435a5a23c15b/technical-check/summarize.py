"""Build the blind technical evidence record from completed runs and pinned source."""
import collections
import csv
import json
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
from verify import BASE, CANDIDATE, DELIVERY, NEW, OLD, PREP, WORK, artifact, digest, integrity, rows


def load(path):
    return json.loads(path.read_text())


def summarize(name):
    raw = WORK / 'runs' / name / 'raw'
    results = load(raw / 'results.json')
    record, = results.values()
    logfile = raw / record['log']
    payload = logfile.read_bytes()
    content = re.sub('\x1b\\[[0-9;]*m', '', payload.decode())
    summary = {}
    for label, prefix in [('test_files', 'Test Files'), ('tests', 'Tests')]:
        match = re.search(r'^\s*' + prefix + r'\s+([0-9][^\n]*)$', content, re.M)
        if match:
            summary[label] = match.group(1).strip()
    failed = re.findall(r'^\s*FAIL\s+\|[^|]+\|\s+([^\n]+)', content, re.M)
    return {
        'state':record['state'], 'exit':record['exit'], **summary,
        'failed_identities':failed, 'raw_log':str(logfile.relative_to(DELIVERY)),
        'raw_sha256':digest(payload),
    }, content


def main():
    all_rows = rows()
    outcomes, logs = {}, {}
    for name, *_ in all_rows:
        outcomes[name], logs[name] = summarize(name)
    for name, outcome in outcomes.items():
        assert outcome['state']=='observed', (name, outcome)
    for variant in ('clean','touch_swap','mouse_guards','private_adapter'):
        assert outcomes[variant+'_original']['tests']=='50 passed (50)', variant
        for tree in ('original','candidate'):
            name=variant+'_'+tree
            expected_exit=int(tree=='candidate' and variant in ('touch_swap','mouse_guards'))
            expected_summary='2 failed | 48 passed (50)' if expected_exit else '50 passed (50)'
            assert (outcomes[name]['exit'], outcomes[name]['tests'])==(expected_exit,expected_summary), name
    for name, count in [('new_file_only',4),('demo_clean',5),('demo_out_of_scale',5),('default_units',341)]:
        assert outcomes[name]['exit']==0 and outcomes[name]['tests']==f'{count} passed ({count})', name
    assert outcomes['seed_45182094013']['tests']=='1 failed | 27 passed (28)'
    assert outcomes['unit_discovery']['exit']==0
    assert "expected [ [ 'Swing', 135 ] ] to deeply equal [ [ 'Tempo', 135 ] ]" in logs['touch_swap_candidate']
    assert "expected [ [ 'Tempo', 59 ] ] to deeply equal [ [ 'Swing', 59 ] ]" in logs['touch_swap_candidate']
    for control, value in [('Tempo',135),('Swing',59)]:
        assert f"expected [ [ '{control}', {value} ] ] to deeply equal []" in logs['mouse_guards_candidate']
    evidence = integrity()
    manifest = load(PREP / 'freeze-manifest.json')
    for name, expected in manifest['evaluator_sha256'].items():
        assert digest((PREP/'evaluator'/name).read_bytes()) == expected
    assert digest((PREP/'participant/ci-snapshot.json').read_bytes()) == manifest['ci_snapshot_sha256']
    assert digest((PREP/'participant/sample.tsv').read_bytes()) == manifest['sample_sha256']
    with (PREP / 'participant/source-manifest.tsv').open() as handle:
        baseline = {r['path']:r['sha256'] for r in csv.DictReader(handle, delimiter='\t')}
    assert all(digest((BASE/path).read_bytes()) == expected for path,expected in baseline.items())
    subprocess.run(['git', '-C', str(BASE), 'apply', '--check', '--whitespace=error', str(DELIVERY/'patch.diff')],check=True)
    numstat=subprocess.check_output(['git','apply','--numstat',str(DELIVERY/'patch.diff')],text=True)
    added,removed=zip(*[(int(n[0]),int(n[1])) for line in numstat.splitlines() if (n:=line.split('\t'))])
    evidence.update({'pristine_source_hashes_matched':len(baseline),'all_frozen_evaluator_hashes_matched':True,'patch_applies_to_pristine_with_whitespace_error_check':True,'insertions':sum(added),'deletions':sum(removed),'production_paths_changed':0})
    discovery = [line for line in logs['unit_discovery'].splitlines() if re.search(r'(?:^|\s)(?:src|scripts|test)/\S*\.test\.[jt]sx?$',line)]
    new_in_lane=any(line.endswith(NEW) for line in logs['unit_discovery'].splitlines())
    focused = (PREP / 'participant/runtime/focused-unit.txt').read_text().splitlines()
    phases = {
        'clean':'Pinned production.',
        'touch_swap':'Swap only the two onTouchMove callback arguments. Both received numbers stay correct. The original suites omit the mounted adapter.',
        'mouse_guards':'Remove the two e.buttons === 1 checks. A secondary drag now sends Tempo 135 or Swing 59.',
        'private_adapter':'Replace the private type/range positional parameters and conditional sensitivity lookup with two configuration objects used by both mouse and touch move handlers. Public props, labels, bounds, arithmetic and event bindings retain their values.',
    }
    classification={'clean':'unchanged','touch_swap':'exploratory fault','mouse_guards':'exploratory fault','private_adapter':'exploratory behavior-preserving transformation'}
    matrix=[]
    for variant,reason in phases.items():
        row={'stimulus':variant,'classification':classification[variant],'change':reason,
             'behavioral_verdict_for_variant':'accept' if variant in ('clean','private_adapter') else 'reject',
             'original':outcomes[variant+'_original'],'submitted':outcomes[variant+'_candidate']}
        if variant!='clean':
            a=load(WORK/'runs'/(variant+'_original')/'variant.json')
            b=load(WORK/'runs'/(variant+'_candidate')/'variant.json')
            assert a==b
            row.update({'identical_production_hashes_for_original_and_submitted_suites':True,'variant':a,'stimulus_diff':'technical-check/mutations/'+variant+'.diff'})
        matrix.append(row)
    all_clean_names={}
    for label in ('original','candidate'):
        lines=re.findall(r'^\s*✓\s+\|unit\|\s+(\S+) > (.+?) \d+(?:\.\d+)?m?s$',logs['clean_'+label],re.M)
        all_clean_names[label]=set(lines)
    retained=all_clean_names['candidate'] & all_clean_names['original']
    assert len(retained)==46
    counts={k:dict(collections.Counter(file for file,_ in names)) for k, names in all_clean_names.items()}
    seedlog = logs['seed_45182094013']
    counter = re.search(r'(\{"accepted":\d+,"dirtyDisconnects":\d+,"byKind":\{[^}]*\}\})',seedlog)
    seedstats = json.loads(counter.group(1)) if counter else None
    assert seedstats and seedstats['accepted']==99 and seedstats['dirtyDisconnects']==3
    assert len(seedstats['byKind'])==9 and all(seedstats['byKind'].values())
    prep_sync = load(PREP/'evidence/final-sync-controls/results.json')
    prep_grader = load(PREP/'evidence/grader-controls.json')
    prep_seed = load(PREP/'evidence/seed-controls/results.json')
    history=load(PREP/'participant/ci-snapshot.json')['runs']
    mac=next(j for j in history[0]['jobs'] if j['name']=='Visual Tests (macOS)')
    identity=next(j for j in history[0]['jobs'] if j['name']=='Stack A Identity')
    audio=next(j for j in history[0]['jobs'] if j['name']=='Unit Tests')
    soak=next(j for j in history[1]['jobs'] if 'rotating soak seed' in j['name'])
    source_refs = [
        'app/src/components/TransportBar.test.tsx:14,28,39 (submitted)',
        'app/src/components/tempo-change.test.ts:421,447 (pinned)',
        'app/src/components/swing-control.test.ts:33,402,428 (pinned)',
        'app/src/components/TransportBar.tsx:45,68,127,150',
        'app/src/components/StepSequencer.tsx:226,230,656',
        'app/src/components/transport-drag.ts:3-16',
        'app/src/shared/constants.ts:33-43',
        'app/e2e/multiplayer.spec.ts:132-153',
        'app/src/components/Transport.tsx:215,228',
    ]
    record={
        'role':'Independent technical evidence for blind review.',
        'repository':'adewale/keyboardia','upstream_commit':'aa67598560f8eaf2509a3ad4bc73edee2f8bea8a',
        'verification_artifact':evidence,
        'declared_repair':'Replace the two Tempo and two Swing callback cases that used local simulations or directly called a spy. Add four jsdom cases driving the two real mobile TransportBar sliders, and correct stale browser-test comments.',
        'control_design':{
            'status':'The alternate-repair adjudication route was specified in advance. The two particular mobile faults were claimed in the sealed response and independently reconstructed afterwards. The private adapter transformation was chosen by the verifier. All three supplemental stimuli are EXPLORATORY. No frozen control or witness was edited.',
            'method':'The frozen postcandidate.py ran each selection in its own fresh Node 24.22.3 Linux Docker container with no network, read-only dependency mounts, 2 CPUs and 2 GiB. The frozen runtime supplies Vitest 4.1.11, React 19.2.1, jsdom 27.3.0 and workerd 1.20261006.1. Docker operations used the shared host lock. Each original/submitted pair received the exact same production bytes. A submitted test is the only new detector counted here.',
            'original_command':['/case/runtime/run-unit.sh','--reporter=verbose',*OLD],
            'submitted_command':['/case/runtime/run-unit.sh','--reporter=verbose',NEW,*OLD],
            'driver_envelope':'Alternate component stimuli are materialized before the frozen --scenario clean driver. Its raw expected_behavior field always says accept for clean transport. The independently classified expected behavior for each variant appears in this matrix.',
            'full_run_commands':'technical-check/plan.json','replay_script':'technical-check/verify.py',
            'driver_sha256':digest((PREP/'postcandidate.py').read_bytes()),
        },
        'exploratory_component_matrix':matrix,
        'expected_values_and_test_boundary':{
            'new_tests':sorted(name for file,name in all_clean_names['candidate'] if file==NEW),
            'removed_original_tests':sorted(file+' > '+name for file,name in all_clean_names['original']-retained),
            'callback_identity':'StepSequencer passes distinct handlers that dispatch SET_TEMPO and SET_SWING. The sliders are independently labeled Tempo and Swing. The tests select by accessible role/name and append callback-specific labels and values into one ordered array. This observes cross-routing, extra edits and missing edits in the exercised sequence.',
            'drag_values':'A move from y=100 to 70 produces 135 from 120 at 0.5 BPM/pixel, or 59 from 50 at 0.3 percentage points/pixel. The retained original Swing helper test independently calls the production calculation for that exact 59. The deleted fake callback case hard-codes 1.0 and expects 80 for the same 30-pixel delta. The new tests use literal observations and do not call the helper to compute the expected result. The precise sensitivities are characterization of the pinned calibration, also present in extant helper examples. Both upward examples land on integers, so these DOM cases do not isolate fractional rounding. The helper suites include separate rounding examples. The available product descriptions do not establish a fixed UX requirement for exact per-pixel rates.',
            'bounds_and_buttons':'The second touch move, y=300, reaches 60 BPM or 0% Swing. These limits agree with the shared domain constants and slider aria limits. The button cases send a secondary drag, assert silence, then send a primary drag and assert one correctly routed edit. This checks the buttons===1 behavior already expressed by each mouse adapter.',
            'failure_diagnostics':'The touch-swap assertions report Swing 135 where Tempo 135 is expected, and Tempo 59 where Swing 59 is expected, at TransportBar.test.tsx:32. With the mouse guards removed the secondary-button assertions at line 44 receive a one-element edit list instead of an empty list. Each fault leaves the opposite input modality green.',
            'bounded_scope':'The component is rendered with fixed props. Its two callbacks record delivered edits. No app-level rerender, downstream dispatch, server, audio, real browser, touch-action, viewport, pointer capture or after-release behavior is exercised. The existing two-client desktop #tempo range-input test drives ArrowUp and is separate. Nearby helper cases retain upper-bound assertions.',
            'source':source_refs,
        },
        'registration':{
            'add_file':NEW,'new_file_in_isolation':outcomes['new_file_only'],
            'ordinary_unit_discovery':outcomes['unit_discovery'],'unfiltered_discovery_lists_new_file':new_in_lane,
            'unfiltered_discovery_files_with_test_suffix':len(discovery),
            'ci_source':'The required Unit Tests job invokes npm run test:unit, which runs vitest run --project unit. The unit project includes src/**/*.test.tsx. The local unfiltered listing verifies collection. The prior hosted job predates this patch. See .github/workflows/ci.yml:151-156, app/package.json:15 and app/vitest.config.ts:87-96.',
            'prepared_default_file_count':len(focused),'included_component_files':[p for p in [*OLD,NEW] if p in focused],
            'default_unit_original_published':{'files':23,'tests':343,'source':'preparation/keyboardia/baseline.json'},
            'default_unit_candidate_observed':outcomes['default_units'],
            'difference':'The prepared 23-file filter selects tempo-change.test.ts only. Its two removed cases reduce that filter’s total by two. The two old full component suites had 23 and 27 cases. The submitted selection has 21, 25 and four. The added jsdom suite requires an explicit argument to the prepared wrapper or ordinary unfiltered unit project.',
        },
        'keepers':[
            {'owner':'Original tempo/swing suites','identities_preserved':len(retained),'clean_file_counts':counts,'evidence':'The same 46 retained identities pass on clean code and in both submitted fault runs. They include production drag arithmetic and properties, real gridReducer updates and field isolation, and state mutations/serialization. Swing tests asserting stored values do not establish audible scheduler timing. The two edited E2E files change comments only.'},
            {'owner':'overlap-fuzz and eviction-recovery','evidence':'Existing workerd checks derive toggle parity from sent operations, check per-socket contiguous sequence numbers, and compare three snapshots and REST. The cold-disconnect example observes stale KV 120, then KV 145 after wake and close. Both files pass in the three-file seed replay. These checks predate the component change.','source':['app/test/integration/overlap-fuzz.test.ts:216,254,277,303','app/test/integration/eviction-recovery.test.ts:761-780']},
            {'owner':'Client persistence','evidence':'The unchanged tests inspect the outbound URL after switching sessions and inspect the second outgoing body after a pending response resolves. The prepared default that includes this file passed. External fetch is a test double.','source':['app/src/sync/session.persistence.test.ts:64,87','preparation/keyboardia/participant/runtime/focused-unit.txt']},
            {'owner':'Native audio render','evidence':'The source counts PCM onsets and compares their timings with a literal step × 0.125 seconds, tolerance below 0.010 seconds. The hosted Unit Tests job recorded the required audio-render step as successful on the pinned commit. No native audio run was performed for this candidate.','source':['app/src/audio/session-render-conservation.render.test.ts:87-100',audio['html_url']]},
        ],
        'open_findings':[
            {'claim':'Rotating Worker run fails the accepted-work floor after its model assertions.','historical_status':'Previously recorded as keyboardia-02 and included as a secondary control. The submission reports this as an open finding.','independent_native':outcomes['seed_45182094013'],'coverage':seedstats,'evidence':'Both seed variables were 45182094013. The trace reaches assertModelCoverage at line 494 after fc.check failure handling. Every one of the nine command kinds appears. The separate coverage assertions explicitly require both WebSocket edit kinds and a dirty disconnect. The hosted receipt records the same quota assertion and a separate step restoring failure after diagnostics. The proposed generation change has no submitted implementation.','sources':['app/test/integration/state-machine-fuzz.test.ts:315,492,510,531,546','.github/workflows/property-seed.yml:100-137',soak['html_url']]},
            {'claim':'The pinned Darwin lane was cancelled before running its three cases.','historical_status':'Previously recorded as keyboardia-01 and included in the prepared lane evidence. The submission reports this as an open finding.','evidence_kind':'Pinned archived hosted job receipt plus source, without a local Darwin execution.','run':history[0]['id'],'conclusion':mac['conclusion'],'steps':len(mac['steps']),'annotation':mac['annotations'][0]['message'],'lane_expected_passes':3,'case_identities':load(CANDIDATE/'app/e2e/lane-identities.json')['lanes']['visual-macos'],'stack_a_identity':{'conclusion':identity['conclusion'],'steps':len(identity['steps']),'source':'.github/workflows/ci.yml:163-167 requires pull_request and audio/full scope'},'sources':[mac['html_url'],identity['html_url'],'app/e2e/populated-visual.spec.ts:10,19,32,45','app/e2e/lane-contracts.json:12']},
            {'claim':'The demo test entitled “playable range and scale” accepts a first active string note outside its authored scale.','historical_status':'Additional finding relative to the four findings in the supplied prior audit and the frozen scoring cases. The fixture test was in the 58-file sample, outside the purposeful anchor list. This open finding has no submitted repair.','control':'EXPLORATORY diagnostic. The independently reconstructed variant changes only the first active string pitch offset from 2 to 3.','ground_truth':'The checked-in fixture sets the locked scale to D natural minor. The string manifest gives a range of 33–88 and omits playbackNote, so the test uses 60. The track transpose is zero. MIDI 62 is D. MIDI 63 is one semitone above D, outside the natural-minor intervals [0,2,3,5,7,8,10]. Both lie in the instrument range. The existing assertion checks only per-note range. This demonstrates a gap in that named fixture test’s scale claim.','clean':outcomes['demo_clean'],'out_of_scale':outcomes['demo_out_of_scale'],'stimulus_diff':'technical-check/mutations/demo_out_of_scale.diff','sources':['app/scripts/demo-sessions/whisper-to-roar.json:28,59','app/public/instruments/string-section/manifest.json:7','app/src/music/music-theory.ts:21,48','app/src/data/phase44-demo-session.test.ts:105-116']},
        ],
        'frozen_reference':{
            'provenance':'The following exit codes come from the independent pre-submission calibration. These are distinct from the new component matrix. Newly authored checks target the mobile component only. The submitted patch does not change these named observers or their production inputs.',
            'sync_original_calibration':{k:{name:v['exit'] for name,v in vset.items()} for k,vset in prep_sync.items()},
            'discovery_original_calibration':{k:v['exit'] for k,v in prep_grader.items()},
            'worker_seed_original_calibration':{k:v['exit'] for k,v in prep_seed.items()},
            'persistence_reference':'The frozen existing state-machine example with the final KV flush removed sees 120 where 150 is expected. This reference case is distinct from the submitted report’s cited 145 cold-disconnect example.',
            'candidate_specific_scope':'Only the frozen valid_schedule stimulus was independently rerun on the submitted tree for the open seed finding, with the three-file selector shown in the report. The remaining results reflect the earlier calibration. The submitted tests exercise the mobile sliders.',
            'sources':['preparation/keyboardia/evaluator/hidden-controls.md','preparation/keyboardia/evidence/final-sync-controls/results.json','preparation/keyboardia/evidence/grader-controls.json','preparation/keyboardia/evidence/seed-controls/results.json'],
        },
        'study_scope':{
            'historical_provenance':['current-test-audit-2026-11-26/reports/keyboardia.json (designated prior report)','preparation/keyboardia/prepare.py:23-40 (purposeful anchors)','preparation/keyboardia/participant/sample.tsv'],
            'historical_context':'The four findings in the designated prior audit covered Darwin cancellation, the rotating command quota, sync-validator behavior and discovery-grader ordering. The mobile callback repair is an additional finding relative to that list and the frozen controls. Its tempo-change.test.ts file was a purposeful sampling anchor, while swing-control.test.ts was a neighboring file followed beyond the sample. Neither that distinction nor the demo result establishes first-ever discovery or a novel-discovery rate.',
            'sample':'58 sampled paths, nine strata, 370 conventionally named original tests. All 58 original sampled blob IDs match independently. The submitted command selects 34 sampled ordinary unit files. Including eight Worker files and one tooling file gives the reported 43. The scope arithmetic and membership were checked. Reading depth and the subject’s execution history were not directly observable from the sealed outputs.',
            'remaining_self_report':'The 490/36 expanded units, 12/12 verification-tooling, 84/8 Worker default and 131/11 Worker full after submission, and code-quality subcommand outcomes were not independently rerun for this record. The original prepared 84/8 and 131/11 Worker counts exist in baseline.json and the Worker code/tests are byte-identical. The response reports unavailable Playwright collection, ESLint and React/Node declarations. Those top-level dependencies are absent from the slim app runtime. The response’s wall times are subject observations. All independent run logs retain their own timings.',
            'unexecuted':'Full upstream CI on this patch, a real browser/mobile device, native audio, Darwin and real codec/browser verification. The historic hosted green audio step applies to pinned code. Claims about all-suite mutation detection or general UX precision fall outside the demonstrated controls.',
        },
    }
    assert new_in_lane
    artifact(DELIVERY/'behavior.json',record)
    print(DELIVERY/'behavior.json')


if __name__=='__main__':
    main()
