import * as assert from 'node:assert/strict'
import { applyOps } from './src/agent/apply.ts'
const operation={kind:'set_label',target:'A',label:'Bravo'}
const cases=[
  ['LF','flowchart LR\n  A[Alpha] --> B\n  %% keep comment\n  C[Charlie] --> D\n'],
  ['CRLF','flowchart LR\r\n  A[Alpha] --> B\r\n  %% keep comment\r\n  C[Charlie] --> D\r\n'],
  ['mixed','flowchart LR\r\n  A[Alpha] --> B\n  %% keep comment\r\n  C[Charlie] --> D\n'],
]
let failures=0
for (const [kind,source] of cases) {
  const result=applyOps({source,ops:[operation],mode:'source-preserving'})
  const expected=source.replace('Alpha','Bravo')
  const actual=result.ok ? result.source : result.error
  console.log(JSON.stringify({kind,method:result.ok?result.preservation?.method:null,expected,actual}))
  if (result.ok && result.preservation?.method==='local' && actual===expected) continue
  failures++
}
assert.equal(failures,0,'every accepted local edit must retain the original bytes around the changed label')
