// Execute the maintained worked example, not an LLM candidate or a prose score.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {createRequire} from 'node:module';
const reference=new URL('../../testing-best-practices/references/exhaustive-testing.md',import.meta.url);
const fences=[...fs.readFileSync(reference,'utf8').matchAll(/```javascript\n([\s\S]*?)```/g)];
assert.equal(fences.length,1,'Keep one complete runnable JavaScript example');
const verify=vm.runInNewContext(`${fences[0][1]}\nverify`,{require:createRequire(import.meta.url)},{timeout:1000});

function fixture(mode='clean'){
  let calls=0;
  const members=Object.fromEntries(['alpha','beta','gamma','auto-1','auto-2'].map(name=>[name,{name}]));
  const contexts=['one','two','three','four','five','six','seven'];
  const input={members,contexts,maxCalls:100,
    resolve(spec){
      const name=typeof spec==='string'?spec:spec.name;
      if(typeof spec==='string'&&name.startsWith('auto-'))return undefined;
      if(mode==='value-undefined'&&typeof spec!=='string'&&name==='alpha')return undefined;
      return {tone:mode==='unequal-but-equivalent'&&typeof spec!=='string'&&name==='gamma'?'alternate':name};
    },
    produce(spec,context){
      calls++;
      const name=typeof spec==='string'?spec:spec.name;
      if(mode==='dispatch'&&typeof spec!=='string'&&name==='beta')return 'incorrect';
      if(mode==='late-residue'&&typeof spec!=='string'&&name==='auto-2'&&context==='seven')return 'incorrect';
      return `${name}:${context}`;
    }};
  return {input,calls:()=>calls};
}
const clean=fixture();verify(clean.input);
assert.equal(clean.calls(),34,'Three witnesses and two complete seven-context sweeps');
for(const mode of ['dispatch','late-residue'])assert.throws(()=>verify(fixture(mode).input));
for(const mode of ['value-undefined','unequal-but-equivalent']){
  const check=fixture(mode);verify(check.input);
  assert.equal(check.calls(),46,'An inconclusive member needs every context, not rejection or sampling');
}
const overBudget=fixture();overBudget.input.maxCalls=33;
assert.throws(()=>verify(overBudget.input),/Complete verification needs/);
assert.equal(overBudget.calls(),0,'Explain an insufficient budget before expensive work');
const reordered=fixture();reordered.input.members=Object.fromEntries(Object.entries(reordered.input.members).reverse());
verify(reordered.input);assert.equal(reordered.calls(),34);
const extension=fixture();extension.input.members['auto-3']={name:'auto-3'};
verify(extension.input);assert.equal(extension.calls(),48,'Registry extension expands the derived residue');
for(const empty of [{members:{}},{contexts:[]}])assert.throws(()=>verify({...fixture().input,...empty}));
console.log('OK: worked example preserves witnesses, full dynamic residue, value equality and budget');
