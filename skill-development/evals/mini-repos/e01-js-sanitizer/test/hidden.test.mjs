import assert from 'node:assert/strict';
import test from 'node:test';

const impl = process.env.IMPL === 'mutant' ? '../mutant/sanitizer.mjs' : '../good/sanitizer.mjs';
const { sanitizeUrl } = await import(impl);

test('removes dangerous javascript URLs', () => {
  for (const url of ['javascript:alert(1)', ' JaVaScRiPt:alert(document.cookie)']) {
    const got = sanitizeUrl(url);
    assert.equal(got, '');
    assert.equal(String(got).toLowerCase().includes('javascript:'), false);
  }
});

test('preserves safe URLs', () => {
  for (const url of ['https://example.com/a', '/docs/start', 'mailto:a@example.com']) {
    assert.equal(sanitizeUrl(url), url);
  }
});
