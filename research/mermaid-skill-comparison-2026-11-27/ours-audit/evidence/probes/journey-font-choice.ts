import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { renderMermaidSVG } from './src/index.ts'
import { renderMermaidPNG } from './src/agent/png.ts'
import { decodePng } from './src/__tests__/helpers/png-pixels.ts'
const source='journey\n  title Onboarding\n  section Signup\n    Complete the extremely long registration questionnaire form: 3: User\n'
const masks: string[] = []
for (const font of [undefined,'Inter','Inter, serif','DejaVu Sans']) {
  const style=font===undefined?{}:{font}
  const svg=renderMermaidSVG(source,{...style,embedFontImport:false})
  const tag=svg.match(/<rect\b[^>]*\bclass="journey-task-box"[^>]*>/)?.[0]
  if (!tag) throw new Error('missing task box')
  const attr=(name:string)=>Number(tag.match(new RegExp('\\b'+name+'="([^"]+)"'))?.[1])
  const scale=2,pad=3*scale
  const x0=Math.ceil(scale*attr('x')+pad),x1=Math.floor(scale*(attr('x')+attr('width'))-pad)
  const y0=Math.ceil(scale*attr('y')+pad),y1=Math.floor(scale*(attr('y')+attr('height'))-pad)
  const img=decodePng(renderMermaidPNG(source,{...style,scale}))
  const mask=createHash('sha256')
  for (let y=y0;y<y1;y++) mask.update(img.rgba.subarray((y*img.width+x0)*4,(y*img.width+x1)*4))
  const digest = mask.digest('hex')
  masks.push(digest)
  console.log(JSON.stringify({font:font??'default',region:[x0,x1,y0,y1],digest}))
}
assert.equal(masks[0],masks[1],'the default draws Inter for Latin text')
assert.equal(masks[1],masks[2],'the fallback after a covering first face can change')
assert.notEqual(masks[1],masks[3],'two covering but differently shaped faces must draw different task glyphs')
