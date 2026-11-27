import { createHash } from 'node:crypto'
import { resolve } from 'node:path'
import { strict as assert } from 'node:assert'
const { renderMermaidSVGWithReceipt } = await import(resolve('src/index.ts'))
const { layoutMermaidWithReceipt } = await import(resolve('src/agent/index.ts'))
const samples = [
 { name:'parallel fan', source:'flowchart TD\n A[Entry] --> B[First]\n A --> B\n A --> C[Second]\n A --> D[Third]', pairs:['A>B','A>B','A>C','A>D'] },
 { name:'parallel fan with label', source:'flowchart LR\n A[Entry] -->|one| B[First]\n A -->|two| B\n C[Second] --> B\n D[Third] --> B', pairs:['A>B','A>B','C>B','D>B'] },
]
const hash=(value:string) => createHash('sha256').update(value).digest('hex')
const observations=[]
for(const {name,source,pairs} of samples) {
 const svg=renderMermaidSVGWithReceipt(source)
 const {layout}=layoutMermaidWithReceipt(source)
 const seen=layout.edges.map((e:any) => e.from+'>'+e.to)
 assert.deepEqual(seen,pairs)
 for (const label of ['Entry','First','Second','Third']) assert.ok(svg.svg.includes(label))
 observations.push({name,pairs:seen,svgSha256:hash(svg.svg),layoutSha256:hash(JSON.stringify(layout)),size:svg.svg.length})
}
console.log(JSON.stringify(observations,null,2))
