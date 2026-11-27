from pathlib import Path
import json,re,sys
lane=Path(__file__).resolve().parents[1]
data=json.loads((lane/'findings.json').read_text())
reads=json.loads((lane/'read-ledger.json').read_text())
commands=json.loads((lane/'command-ledger.json').read_text())
assert len(data)==len({r['id'] for r in data})==4
assert all((lane/f).is_file() for row in data for f in row['artifacts'])
for row in reads['files']:
 path=lane/'repo'/row['path'] if row['origin']=='target' else lane.parent/'openclaw'/row['path']
 assert path.is_file(),path
 assert all(1<=i<=j<=row['file_lines'] for i,j in row['reviewed_line_ranges'])
assert len(commands)==len({r['id'] for r in commands})
for row in commands:
 assert isinstance(row['exit_code'],int) and row['elapsed_seconds']>=0
 assert (lane/row['artifact']).is_file(),row['artifact']
report=(lane/'report.md').read_text()
targets=re.findall(r'\]\(([^)]+)\)',report)
for url in targets:
 if not url.startswith('https://'): assert (lane/url).is_file(),url
assert 'OC-1' in report and 'OC-2' in report and 'OC-3' in report and 'OC-4' in report
print(json.dumps({'findings':len(data),'read_counts':reads['counts'],'command_records_prior_to_this_validation':len(commands),'report_link_targets':len(targets),'missing':[]},indent=2))
