import { writeFileSync } from 'node:fs'
import { renderMermaidSVG } from './src/index.ts'
import { renderMermaidPNG } from './src/agent/png.ts'
import { decodePng, inkColumns } from './src/__tests__/helpers/png-pixels.ts'
const label = 'Complete the extremely long registration questionnaire form'
const source = 'journey\n  title Onboarding\n  section Signup\n    ' + label + ': 3: User\n'
const tag = renderMermaidSVG(source, {embedFontImport:false}).match(/<rect\b[^>]*\bclass="journey-task-box"[^>]*>/)?.[0]
if (!tag) throw new Error('fixture has no task box')
const attr = (key: string) => Number(tag.match(new RegExp('\\b'+key+'="([^"]+)"'))?.[1])
const scale = 2
const [x,y,w,h] = ['x','y','width','height'].map(k=>attr(k)*scale)
if (![x,y,w,h].every(Number.isFinite)) throw new Error('no geometry')
const png = renderMermaidPNG(source,{scale})
writeFileSync(process.argv[2],png)
const decoded = decodePng(png)
const pad=3*scale
const inside = inkColumns(decoded,x+pad,x+w-pad,y+pad,y+h-pad)
const outside = inkColumns(decoded,x+w+pad,decoded.width,y+pad,y+h-pad)
console.log(JSON.stringify({label,boxPixels:{x,y,w,h},image:[decoded.width,decoded.height],interior:inside.length,exterior:outside.length,interiorColumnRange:[inside[0],inside.at(-1)]}))
