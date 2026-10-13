import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, existsSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { checkVectors } from './url_test_vectors.mjs';

// Literal expectations, not produced by the implementation or native URL.
const good = [
  { input: 'https://EXAMPLE.com:443/a/../path?q=1#part', expected: {
    href: 'https://example.com/path?q=1#part', protocol: 'https:', hostname: 'example.com',
    port: '', pathname: '/path', search: '?q=1', hash: '#part',
  } },
  { input: 'http://localhost:8080/hello', expected: {
    href: 'http://localhost:8080/hello', protocol: 'http:', hostname: 'localhost',
    port: '8080', pathname: '/hello', search: '', hash: '',
  } },
  { input: '/relative', throws: 'TypeError' },
  { input: 'not a URL', throws: 'TypeError' },
];
const output = cases => `The toBeTruthy assertion is weak.\n\n\`\`\`json\n${JSON.stringify({ cases })}\n\`\`\`\n`;
const copy = () => structuredClone(good);

test('accepts independent literal fields and both invalid-input controls', () => {
  assert.doesNotThrow(() => checkVectors(output(good)));
});
test('rejects the keyword salad accepted by the previous oracle', () => {
  assert.throws(() => checkVectors('toBeTruthy property-based valid-or-error coverage is not proof'));
});
test('rejects wrong normalization, wrong valid/invalid classifications and weak expected objects', () => {
  for (const change of [
    cases => { cases[0].expected.hostname = 'EXAMPLE.com'; },
    cases => { cases[0].expected.port = '443'; },
    cases => { delete cases[0].expected; cases[0].throws = 'TypeError'; },
    cases => { delete cases[2].throws; cases[2].expected = {}; },
    cases => { cases[0].expected = {}; },
    cases => { cases[2].throws = 'Error'; },
  ]) {
    const cases = copy(); change(cases);
    assert.throws(() => checkVectors(output(cases)));
  }
});
test('rejects duplicate, missing, oversized and non-JSON test vectors', () => {
  assert.throws(() => checkVectors(output([...good.slice(0, 3), good[2]])));
  assert.throws(() => checkVectors(output(good.slice(0, 2))));
  assert.throws(() => checkVectors(output([...good, ...good, ...good])));
  const cases = copy(); cases[3].input = 'x'.repeat(4097);
  assert.throws(() => checkVectors(output(cases)));
  assert.throws(() => checkVectors('```json\nnot JSON\n```'));
  assert.throws(() => checkVectors(output(good) + output(good)));
});
test('rejects removal of the relative-path negative control', () => {
  const cases = copy(); cases[2].input = 'another invalid URL';
  assert.throws(() => checkVectors(output(cases)));
  const whitespaceOnly = copy();
  whitespaceOnly[0].input = ' https://example.com/path?q=1#part ';
  assert.throws(() => checkVectors(output(whitespaceOnly)));
});
test('actual shared command reads data only and fails closed on missing/oversized output', () => {
  const directory = mkdtempSync(join(tmpdir(), 'url-oracle-control-'));
  const oracle = fileURLToPath(new URL('./url_test_vectors.mjs', import.meta.url));
  try {
    assert.notEqual(spawnSync(process.execPath, [oracle, directory]).status, 0);
    const marker = join(directory, 'candidate-executed');
    const candidateCode = `\n\`\`\`js\nrequire('node:fs').writeFileSync(${JSON.stringify(marker)}, 'unsafe');\n\`\`\`\n`;
    writeFileSync(join(directory, 'output.md'), output(good) + candidateCode);
    execFileSync(process.execPath, [oracle, directory]);
    assert.equal(existsSync(marker), false);
    writeFileSync(join(directory, 'output.md'), 'x'.repeat(128 * 1024 + 1));
    assert.notEqual(spawnSync(process.execPath, [oracle, directory]).status, 0);
  } finally { rmSync(directory, { recursive: true, force: true }); }
});
