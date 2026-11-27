const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const { createRequire } = require('node:module')
const { chromium } = createRequire(path.resolve('package.json'))('playwright')
const read = (f) => fs.readFileSync(f, 'utf8')
;(async () => {
  const browser = await chromium.launch({ executablePath: '/usr/bin/chromium', headless: true })
  try {
    const page = await browser.newPage({ colorScheme: 'light', forcedColors: 'none' })
    await page.route('**/*', route => route.abort())
    // The production HTML supplies the actual selectors; use its masthead before
    // the shader is attached. Website generation prepends font faces to this CSS.
    const home = read('website/source/pages/home.html').match(/<header\b[\s\S]*?<\/header>/)[0]
    const editor = read('editor/html/topbar.html')
    const results = {}
    for (const [side, html, files, selector] of [
      ['site', home, ['website/source/assets/styles.css'], '.brand .mark'],
      ['editor', editor, ['editor/css/variables.css', 'editor/css/topbar.css'], '.app-mark']
    ]) {
      await page.setContent('<!doctype html><html><body>'+html+'</body></html>')
      for (const file of files) await page.addStyleTag({ content: read(file) })
      results[side] = await page.locator(selector).evaluate(mark => ({
        background: getComputedStyle(mark).backgroundColor,
        foreground: getComputedStyle(mark).color
      }))
    }
    const expected = { background: 'rgb(111, 194, 162)', foreground: 'rgb(10, 68, 52)' } // DESIGN.md:8–9
    console.log(JSON.stringify({ engine: browser.version(), expected, ...results }, null, 2))
    assert.deepEqual(results.site, expected)
    assert.deepEqual(results.editor, expected)
  } finally { await browser.close() }
})().catch(err => { console.error(err.message); process.exitCode = 1 })
