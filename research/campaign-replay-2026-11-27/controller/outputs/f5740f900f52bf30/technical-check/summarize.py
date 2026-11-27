"""Summarize raw technical observations without assigning an audit score."""
import collections
import csv
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode=True
from probes import HERE, OUTPUT, PREP, CANDIDATE, MODEL, check_integrity, sha, save


def load(path):
    return json.loads(path.read_text())


def inspect_log(path, code):
    data=path.read_bytes()
    txt=re.sub('\x1b\\[[0-9;]*m','',data.decode(errors='replace'))
    obs={'exit':code,'log':str(path.relative_to(OUTPUT)),'sha256':sha(data)}
    for k,label in [('files','Test Files'),('tests','Tests'),('vitest_duration','Duration')]:
        m=re.search(r'^\s*'+label+r'\s+([^\n]+)',txt,re.M)
        if m: obs[k]=m.group(1).strip().split(' (transform')[0]
    return obs, txt


def entry(name):
    raw=load(HERE/'exploratory'/name/'result.json')
    obs,txt=inspect_log(OUTPUT/raw['log'],raw['exit'])
    assert raw['sha256']==obs['sha256']
    return obs,txt


def counter(txt):
    found=re.search(r'(\{"accepted":\d+,"dirtyDisconnects":\d+,"byKind":\{[^}]+\}\})',txt)
    return json.loads(found.group(1)) if found else None


def pbt(txt):
    match=re.search(r'^PBT_COUNTEREXAMPLE=(\{[^\n]+\})',txt,re.M)
    return json.loads(match.group(1))


def main():
    integrity=check_integrity()
    names=['default_model','valid_schedule','persistence_original','persistence_fault']
    frozen=[]
    quals=['Clean default seed list and real generated model.','Accepted historical schedule, with both fast-check bindings set to 45182094013.','Existing explicit WebSocket, GET and KV lifecycle example on clean production.','Remove exactly the final save inside flushPendingKVSave. Run the same existing lifecycle example.']
    seed_coverage=None
    for n,name in enumerate(names):
        row={'case':name,'meaning':quals[n],'ground_truth':'reject' if n==3 else 'accept'}
        for label,tree in [('original','original'),('submitted','candidate')]:
            folder=HERE/('frozen-native-'+tree)/'raw'
            result=load(folder/'results.json')[name]
            record,txt=inspect_log(folder/result['log'],result['exit'])
            assert result['matched'] and record['exit']==(int(n in (1,3)) if tree=='original' else int(n==3))
            if n==1 and tree=='original': seed_coverage=counter(txt)
            if n==3: assert 'expected 120 to be 150' in txt
            row[label]=record
        folder=HERE/'frozen-offline-candidate'/name/'raw'
        product=load(folder/'results.json')[name]
        assert product['state']=='observed' and product['exit']==int(n==3)
        row['submitted_offline_repeat'],txt=inspect_log(folder/product['log'],product['exit'])
        if n==3: assert 'expected 120 to be 150' in txt
        frozen.append(row)
    assert seed_coverage['accepted']==99 and seed_coverage['dirtyDisconnects']==3 and len(seed_coverage['byKind'])==9
    fullfolder=HERE/'ci-worker-full/raw'
    x=load(fullfolder/'results.json')['original']
    all_workers,alltxt=inspect_log(fullfolder/x['log'],x['exit'])
    assert x['state']=='observed' and (all_workers['exit'],all_workers['tests'],all_workers['files'])==(0,'131 passed (131)','11 passed (11)')
    assert re.search(r'^\s*✓.*state-machine-fuzz\.test\.ts > model: read-your-writes',alltxt,re.M)
    included=sorted(set(re.findall(r'^\s*✓\s+\|keyboardia-integration\| (\S+\.test\.ts) >',alltxt,re.M)))
    assert len(included)==11
    preserved_fixed=[m for m in re.findall(r'^\s*✓\s+\|keyboardia-integration\| state-machine-fuzz\.test\.ts > (.+?) \d+ms$',alltxt,re.M) if not m.startswith('model:')]
    assert len(preserved_fixed)==5
    weekly,weeklytxt=entry('weekly_selection')
    assert weekly['tests']=='28 passed (28)' and weekly['exit']==0
    trace_a=HERE/'exploratory/candidate_trace_capture/schedule-trace.json'
    trace_b=HERE/'exploratory/continuous_32_capture/schedule-trace.json'
    trace=load(trace_a)
    assert len(trace)==32 and trace==load(trace_b) and trace_a.read_bytes()==trace_b.read_bytes()
    assert [r['accepted'] for r in trace[-3:]]==[99,99,101] and [r['dirty'] for r in trace[-3:]]==[3,3,4]
    assert sum(len(r['actions']) for r in trace)==101
    assert trace[30]['actions']==[] and trace[31]['actions']==[{'kind':'ws_swing','swing':50},{'kind':'disconnect'}]
    assert all('VERIFY_CAPTURE_COMPLETE' in entry(n)[1] for n in ('candidate_trace_capture','continuous_32_capture'))
    stale_a,stale_atxt=entry('stale_original'); stale_b,stale_btxt=entry('stale_candidate')
    assert pbt(stale_atxt)==pbt(stale_btxt) and 'expected 120 to be 60' in stale_atxt and 'expected 120 to be 60' in stale_btxt
    missing,missingtxt=entry('missing_swing')
    miss=counter(missingtxt)
    assert missing['exit']==1 and miss['accepted']==247 and miss['byKind']['ws_swing']==0 and 'WS swing writes' in missingtxt
    flush_a,fa=entry('final_flush_model_original');flush_b,fb=entry('final_flush_model_candidate')
    assert pbt(fa)==pbt(fb) and pbt(fb)['example']==[{'kind':'ws_tempo','tempo':60},{'kind':'disconnect'}]
    wrong=HERE/'exploratory/stale_candidate'
    promotion,pr=inspect_log(wrong/'promotion.log',load(wrong/'result.json')['promotion']['exit'])
    replay,kr=inspect_log(wrong/'known-replay.log',load(wrong/'result.json')['known_replay']['exit'])
    promoted=load(wrong/'promoted-known-failures.json')
    assert promotion['exit']==0 and promoted['stateMachine']==[pbt(stale_btxt)['example']]
    assert replay['exit']==1 and 'known-failure #0 regressed: expected 120 to be 60' in kr
    legitimate_names=('other_seed_original','other_seed_candidate','private_get_representation','promoted_clean_control')
    allowed={n:entry(n)[0] for n in legitimate_names}
    assert all(v['exit']==0 and v['tests']=='1 passed | 5 skipped (6)' for v in allowed.values())
    waveform={n:entry(n)[0] for n in ('waveform_clean','waveform_flat')}
    assert all(v['exit']==0 and v['tests']=='4 passed (4)' for v in waveform.values())
    client,ct=entry('client_persistence_keeper')
    assert client['exit']==0 and client['tests']=='7 passed (7)' and 'retains an edit scheduled while a flush is awaiting the network' in ct
    for fault in ('stale','final_flush_model'):
        a=load(HERE/'exploratory'/(fault+'_original')/'result.json')
        b=load(HERE/'exploratory'/(fault+'_candidate')/'result.json')
        assert a['stimulus_file_hash_before_after']==b['stimulus_file_hash_before_after']
    public=OUTPUT/'submitted-artifacts/evidence'
    with (public/'survey.tsv').open() as f: survey=list(csv.DictReader(f,delimiter='\t'))
    with (PREP/'participant/sample.tsv').open() as f: sample=list(csv.DictReader(f,delimiter='\t'))
    assert {(r['sample_path'],r['stratum']) for r in survey}=={(r['path'],r['stratum']) for r in sample} and len(survey)==58
    units=set((public/'unit-files.txt').read_text().splitlines())
    assert units=={r['sample_path'].removeprefix('app/') for r in survey if r['local_execution']=='unit project, passed'} and len(units)==34
    archived={}
    for name in ['pinned-unit','pinned-worker','survey-units','all-workers','seed-before','seed-after','seed-three-files','stale-before','stale-after','known-replay','no-swing','waveform-control','workload-diagnostic']:
        data=(public/(name+'.log')).read_text(); m=re.search(r'^\s*Tests\s+(\d+[^\n]+)',data,re.M)
        archived[name]=m.group(1).strip() if m else None
    tsc=(public/'worker-tsc.log').read_bytes()
    assert tsc==(public/'pinned-worker-tsc.log').read_bytes() and tsc.count(b'error TS')==6
    prev_sync=load(PREP/'evidence/final-sync-controls/results.json')
    prev_grader=load(PREP/'evidence/grader-controls.json')
    hist=load(PREP/'participant/ci-snapshot.json')['runs']
    mac=next(j for j in hist[0]['jobs'] if j['name']=='Visual Tests (macOS)')
    linux=next(j for j in hist[0]['jobs'] if j['name']=='E2E Visual Regression')
    identity=next(j for j in hist[0]['jobs'] if j['name']=='Stack A Identity')
    soak=next(j for j in hist[1]['jobs'] if 'rotating soak seed' in j['name'])
    audio=next(j for j in hist[0]['jobs'] if j['name']=='Unit Tests')
    quality_source=public/'test-quality.log'
    first_attempts={}
    for n in ('candidate_trace','continuous_32_reference'):
        assert load(HERE/'exploratory'/n/'schedule-trace.json')==[]
        first_attempts[n]=entry(n)[0]
    record={
      'role':'Independent technical verification for blind review.',
      'repository':'adewale/keyboardia','upstream_commit':'aa67598560f8eaf2509a3ad4bc73edee2f8bea8a','integrity':integrity,
      'submitted_repair':'Change the existing registered Worker command-model test to continue drawing whole schedules from each allowed seed while its accepted-work or lifecycle requirements are missing. The one-file patch leaves the command generator, production owners, CI, five fixed examples and known-failure database byte-identical outside the changed end of the test file.',
      'verification_method':{
        'predeclared_target':'Prior audit finding keyboardia-02 and the frozen Worker-seed secondary matrix. The matched original and submitted commands used evaluator/evaluate-seed.py --assert-original or --assert-repaired with the shared pinned dependencies. All four submitted rows also ran separately through postcandidate.py --scenario seed in fresh offline Docker containers with 2 CPUs and 2 GiB. Exit 1 in a fault row is an assertion failure. Each title filter selected one actual test and filtered the file’s other five.',
        'supplemental':'Additional fault, representation, seed and trace checks are explicitly EXPLORATORY. They used independent disposable trees, real Node 24.22.3, Vitest 4.1.11, workerd 1.20261006.1 and Worker fast-check 4.9.0. Their shared-host transport differs from the independent offline Docker repeat. All Docker calls acquired the shared lock.',
        'evidence_sources':['technical-check/plan.json','technical-check/frozen.py','technical-check/probes.py','submitted-artifacts/evidence-collection.json'],
      },
      'frozen_seed_matrix':frozen,
      'historical_seed':{'seed':45182094013,'signed_fast_check_seed':-2062546243,'baseline_actual_coverage':seed_coverage,
        'failure_cause':'The original run completed its generated properties, then failed only the 100-accepted-command floor at state-machine-fuzz.test.ts:494. The post-repair row is the same registered model and same seed. The original archived rotating-unit job passed. The hosted Worker job uploaded its diagnostic before its failure-preservation step returned red.',
        'hosted_worker_receipt':soak['html_url']},
      'extension_evidence':{
        'logic':'Let S be the number of supplied seeds and R = ceil(30 / S). Each seed first runs R schedules. If any shared witness is deficient, each seed draws one more schedule at offset R + extraRun. There are at most R such rounds. A batch finishes for every seed before coverage is checked again. The maximum is 2 × S × R scheduled cases before shrink/replay, and the normal 11 unique default seeds give 33 initial and at most 66 cases. This historical single-seed configuration starts at 30 and caps at 60. Each schedule allows up to 18 generated commands with preconditions.',
        'witnesses':'At least 100 accepted commands, at least one acknowledged WebSocket tempo write, one WebSocket swing write, and one disconnect while the model’s live and KV state differ. An accepted action calls the real owner and compares expected state through REST, KV and socket observations. A property failure is handled immediately before any coverage top-up. The other seven command kinds are generated but each is not independently required by the final predicate.',
        'same_stream':'The fixed package implements a single numeric fast-check path by dropping that many initial producers from the same seed’s generator stream. It honors numRuns when that path has no shrink segment. The repair uses the original signed seed and increasing case offsets. In a disposable diagnostic we recorded all accepted action objects and cumulative coverage after each successful real model schedule. All 32 records were byte-identical to one uninterrupted 32-case run of the original generator with the same seed.',
        'trace_support':{'length':len(trace),'accepted_action_count':sum(len(r['actions']) for r in trace),'trace_sha256':sha(trace_a.read_bytes()),'submitted_trace':str(trace_a.relative_to(OUTPUT)),'uninterrupted_reference_trace':str(trace_b.relative_to(OUTPUT)),
          'after_case_30':{'accepted':trace[29]['accepted'],'dirty_disconnects':trace[29]['dirty']},'case_31':trace[30],'case_32':trace[31]},
        'cost':'For this seed the repair executed two extra schedules. Case 31 had no accepted action. Case 32 sent swing 50 and disconnected, raising 99 to 101 and three dirty closes to four. The uninstrumented paired local Vitest process times and isolated repeats are in the matrix. Each extra fc.check reinitializes a runner and advances to an offset. The outer test timeout is unchanged at max(120000, 15000 × S) ms. interruptAfterTimeLimit is per fc.check, including each extra call. No suite-wide runtime multiplier or all-seed success rate was measured.',
        'diagnostic_attempts':{'first_passing_runs_with_no_emitted_trace':first_attempts,'reason':'The first successful runs emitted no console.log records. Their empty traces give no stream comparison. The retained follow-ups accumulated records, ran the original coverage assertion and then deliberately raised a diagnostic error to deliver the trace. The added diagnostic exit supplies observations only. The frozen uninstrumented runs establish pass/fail.',
          'submitted_capture':entry('candidate_trace_capture')[0],'reference_capture':entry('continuous_32_capture')[0]},
        'sources':['app/test/integration/state-machine-fuzz.test.ts:315,346,391,412,445,455,492,501,524,537,547','Worker fast-check 4.9.0 lib/fast-check.js:2327,2532']},
      'exploratory_checks':{
        'stale_get':{'classification':'Additional submitted fault, independently reconstructed on original and submitted model. Existing regression detection is retained.','change':'Serve the stale KV state instead of the active Durable Object state in the real Worker GET merge. Both versions shrink to one WebSocket tempo write of 60. The acknowledgement arrives and the following GET observes the original 120. Both matrices fail before the coverage check.','original':stale_a,'submitted':stale_b,'shrunk_record':pbt(stale_btxt),'same_modified_owner_bytes':True},
        'promotion_and_replay':{'classification':'Existing real counterexample CLI and registered replay loop.','result':'The actual promote-pbt-counterexamples.ts CLI consumed the independently produced failure log and added the shrunk schedule to the otherwise empty stateMachine array. Known case 0 failed before exploration with 120 where 60 was required while the stale GET remained. The same promoted schedule passed with correct production restored.','CLI':promotion,'promoted_database':'technical-check/exploratory/stale_candidate/promoted-known-failures.json','faulty_known_replay':replay,'restored_production':allowed['promoted_clean_control']},
        'flush_fault_actual_generated_model':{'classification':'Unchanged frozen missing-final-save stimulus, with an EXPLORATORY selection of the registered generated model as observer.','original':flush_a,'submitted':flush_b,'shrunk_record':pbt(fb),'same_modified_owner_bytes':True,'result':'Both reach the same failing generated schedule, a tempo write to 60 followed by disconnect. The KV observation stays 120. This is distinct from the fixed frozen 150 example and demonstrates preservation of an existing sensitivity.'},
        'missing_swing_generator':{'classification':'EXPLORATORY damaged workload generator.','submitted':missing,'coverage':miss,'result':'Deleting only the WebSocket swing generator still fails after the capped extension. The native assertion reports the missing WS swing witness (observed 0, minimum 1), even after 247 accepted actions and four dirty disconnects. The original model already required this witness.'},
        'different_allowed_seed':{'seed':20261127,'original':allowed['other_seed_original'],'submitted':allowed['other_seed_candidate'],'result':'Both registered models passed the separately selected valid seed with both seed bindings set.'},
        'equivalent_get_representation':{'submitted':allowed['private_get_representation'],'result':'The submitted model accepted a private Object.assign construction producing the same plain response as the previous object spread, retaining KV metadata and authoritative DO state, on 45182094013.'},
      },
      'registration_and_retained_checks':{
        'ordinary_ci':{'observed':all_workers,'files':included,'scope':'The complete ordinary Worker test entry ran npm test (vitest run, no file/title filters) in app/test/integration under isolated Docker. It collected all 11 Worker files, all six state-machine identities and 131 passes. The pinned CI builds first, installs Worker dependencies, then calls test:integration:built, which delegates here. The prepared runner supplied the two small static assets and HTML. A complete application build or hosted patch run is outside this observation.','sources':['.github/workflows/ci.yml:241-255','app/package.json:23-24','app/test/integration/package.json:6','app/test/integration/vitest.config.ts:21-50']},
        'rotating_ci':{'observed':weekly,'scope':'Exact three registered files with both replay seed variables, all 28 passed. The registered modified model, five fixed examples, eviction/recovery and three-socket overlap checks ran. The eight other integration files outside the weekly selector were covered by the separate unfiltered run.','source':'.github/workflows/property-seed.yml:97-137'},
        'fixed_state_machine_examples':preserved_fixed,
        'keepers':[{'area':'Worker state and acknowledgments','evidence':'The fixed example creates tempo 120, sends 150 over a WebSocket and requires its acknowledgement, GET at 150 and KV still at 120, followed by KV at 150 after the disconnect. Stateful commands compare real GET name/tempo/swing, direct KV values and socket readyState to the independent expected model. Checks and update logic are unchanged.','sources':['app/test/integration/state-machine-fuzz.test.ts:162,315,346,391,412']},
          {'area':'Peer state and convergence','evidence':'The unchanged overlap test starts all 32 expected cells from fixture inputs, toggles by sent parity, checks every sequence number on each of three sockets and reconciles snapshots and the REST GET. The native three-file and full Worker runs passed it. The single-client generated model itself makes a narrower delivery observation.','sources':['app/test/integration/overlap-fuzz.test.ts:218,254,277,303']},
          {'area':'Client save destination and in-flight edit','observed':client,'evidence':'The test records outgoing requests with a fetch double. The unchanged client test leaves the first save pending, releases its response and checks that the next outbound payload carries tempo 200.','source':'app/src/sync/session.persistence.test.ts:87-105'},
          {'area':'Audio timing','evidence':'The source counts PCM onsets and compares timing against step × 0.125 seconds at 120 BPM with a 0.010-second tolerance. The required native-render step passed in the pinned hosted Unit Tests receipt. This verification performed no native audio render.','sources':['app/src/audio/session-render-conservation.render.test.ts:87-100',audio['html_url']]}]},
      'other_reported_findings':[
        {'finding':'Historical macOS visual cancellation','historical_status':'Prior finding keyboardia-01, reported as open.','evidence_kind':'Archived hosted receipt and source.','run':hist[0]['id'],'mac_conclusion':mac['conclusion'],'steps':len(mac['steps']),'annotation':mac['annotations'][0]['message'],
         'source_contract':'The workflow requests macos-14 and Chromium, sets the mock API and calls populated-visual.spec.ts. The spec requires Darwin. The lane expects three named Holby results and zero skips.','cases':load(CANDIDATE/'app/e2e/lane-identities.json')['lanes']['visual-macos'],'linux_visual':linux['conclusion'],'stack_a_identity':identity['conclusion'],'identity_gate':'pull_request with audio or full verification scope, .github/workflows/ci.yml:166','sources':[mac['html_url'],linux['html_url'],identity['html_url'],'app/e2e/populated-visual.spec.ts:10','.github/workflows/ci.yml:649-681','app/e2e/lane-contracts.json:12']},
        {'finding':'Recorder waveform tests accept flat production peaks','historical_status':'Additional relative to the designated prior audit’s four reported findings and frozen controls. This sampled file is outside the purposeful anchor list. The submission reports an open finding. No global novelty claim follows.','evidence_kind':'EXPLORATORY independent native case pair on the candidate tree.','change':'Only the production Waveform.tsx assignments to mins[i] and maxs[i] are replaced by zeros. Recorder supplies the recorded buffer to Waveform, which draws from its production function and per-buffer/per-width cache. The four ordinary tests define a local function, import only Vitest, and never reach the production function or its WeakMap. All four pass on clean and flattened production. This establishes insensitivity of these four tests. Browser canvas output and the rest of the suite were not evaluated on this fault.','native':waveform,'sources':['app/src/components/waveform-peaks.test.ts:9-39','app/src/components/Waveform.tsx:29,53,99,106','app/src/components/Recorder.tsx:230']}],
      'submitted_evidence_and_scope':{
        'packet':'18 supplied attachments verified against the controller collection manifest. All recorded original mtimes precede the seal. These include 16 logs, one unit-file list and a 58-row survey. Submitted logs and independent post-candidate observations have separate provenance.',
        'survey':'The ledger matches all 58 frozen sampled paths and strata out of 370 conventional original test files. It marks 34 sampled unit files and eight sampled Worker files as run, and 16 source-only. It characterizes five full reads, 22 focused excerpts and 31 declaration/import/matcher/gate scans. The path and selection arithmetic are verifiable. The depth of each reading is self-described.',
        'submitted_log_counts':archived,
        'reported_obstacles':{'typecheck':'The supplied baseline and candidate Worker tsc logs are byte-identical, with six configuration diagnostics. This verification did not independently rerun tsc.','tsc_sha256':sha(tsc),'quality':'The supplied log reaches successful antipattern, linkage and dead-export checks, then its npx playwright test --list fails with ENOTCACHED in the slim offline setup. This is separate from the successful actual full Worker collector run.','quality_log':str(quality_source.relative_to(OUTPUT))},
        'scope':'The data support a repair to the registered Worker property-test workload, alongside inherited detection and replay. A valid run can still fail if it does not meet the four mandatory witnesses within the cap or exceeds the unchanged outer deadline. Exact performance across arbitrary seeds, full hosted CI, browser behavior, native audio and Darwin were not independently exercised. No production application change was submitted.'},
      'other_frozen_reference_results':{'provenance':'Unchanged pre-submission calibration. The participant’s patch targets the frozen Worker seed secondary matrix, not the named sync or discovery contracts. These numerical exits are earlier observations, without a new detection attributed to this submission.','sync':{case:{w:r['exit'] for w,r in observers.items()} for case,observers in prev_sync.items()},'discovery':{k:v['exit'] for k,v in prev_grader.items()},'sources':['preparation/keyboardia/evidence/final-sync-controls/results.json','preparation/keyboardia/evidence/grader-controls.json','preparation/keyboardia/evaluator/hidden-controls.md']},
    }
    save(OUTPUT/'behavior.json',record)
    print(OUTPUT/'behavior.json')


if __name__=='__main__':
    main()
