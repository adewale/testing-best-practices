from pathlib import Path
import json,subprocess,tempfile
with tempfile.TemporaryDirectory() as d:
 root=Path(d)
 a=root/'first.mmd'; b=root/'second.mmd'
 a.write_text('flowchart LR\n A --> B'); b.write_text('flowchart LR\n C --> D')
 for count, inputs in ((1,[a]),(2,[a,b])):
  destination=root/f'{count}.txt'
  argv=['bun','run','bin/am.ts','render',*[str(f) for f in inputs],'--format','ascii','--output',str(destination),'--json']
  r=subprocess.run(argv,capture_output=True,text=True,timeout=30)
  receipt=json.loads(r.stdout)
  print(json.dumps({'argv':argv,'input_count':count,'exit':r.returncode,'stderr':r.stderr,'destination_exists':destination.exists(),'stdout_keys':list(receipt),'file_rows':len(receipt.get('files',[])),'reported_path':receipt.get('path')},indent=2))
