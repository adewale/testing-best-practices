import { resolve } from 'node:path'
import { strict as assert } from 'node:assert'
const { bundleEdgePaths } = await import(resolve('src/layout/passes/edge-bundling.ts'))
const { resolveRenderStyle } = await import(resolve('src/styles.ts'))
const n = (id: string, x: number, y: number) => ({ id, label: id, shape: 'rectangle', x, y, width: 40, height: 40 })
const style = resolveRenderStyle()
const nodes = [n('A', 40, 0), n('B', 40, 100), n('C', 140, 100)]
const header = { id: 'G', label: 'G', x: 60.1, y: 45, width: 6, height: 4, headerHeight: 4, children: [] }
const edges = ['B', 'C'].map(target => ({
  source: 'A', target,
  points: [{ x: 80, y: 20 }, { x: 110, y: 20 }, { x: 110, y: 120 }, { x: target === 'B' ? 80 : 140, y: 120 }],
  style: 'solid', hasArrowStart: false, hasArrowEnd: false,
}))
const before = structuredClone(edges.map(e => e.points))
const claimed = [...bundleEdgePaths(edges, nodes, [header], 'TB', style)].length
const after = edges.map(e => e.points)
const hits = edges.flatMap(edge => edge.points.slice(1).flatMap((b, i) => {
  const a = edge.points[i]!
  if (a.x !== b.x) return []
  const half = style.lineWidth / 2
  return a.x + half > header.x && a.x - half < header.x + header.width &&
    Math.max(a.y, b.y) > header.y && Math.min(a.y,b.y) < header.y + header.height
      ? [{from: edge.source, to: edge.target, a, b}] : []
}))
console.log(JSON.stringify({ claimed, lineWidth: style.lineWidth, header, hazardousVerticalSegments: hits, before, after }, null, 2))
assert.equal(claimed, 0)
assert.deepEqual(hits, [], 'excluded candidate ink overlaps the header')
assert.deepEqual(after, before, 'excluded candidate must leave both authored fixture routes intact')
