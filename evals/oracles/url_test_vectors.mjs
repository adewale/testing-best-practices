/** Data-only check of proposed URL test vectors, never candidate code. */
import { readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

export function checkVectors(text) {
  const fences = [...text.matchAll(/```json\s*\n([\s\S]*?)```/gi)];
  if (fences.length !== 1) throw new Error('expected exactly one JSON code fence');
  const plan = JSON.parse(fences[0][1]);
  if (!plan || !Array.isArray(plan.cases) || plan.cases.length < 4 || plan.cases.length > 8) {
    throw new Error('expected 4 to 8 test vectors');
  }
  const fields = ['href', 'protocol', 'hostname', 'port', 'pathname', 'search', 'hash'];
  const inputs = new Set();
  let valid = 0, invalid = 0, relative = false;
  let path = false, query = false, fragment = false, normalized = false;
  for (const vector of plan.cases) {
    if (!vector || typeof vector.input !== 'string' || vector.input.length > 4096 || inputs.has(vector.input)) {
      throw new Error('each vector needs a distinct, bounded string input');
    }
    inputs.add(vector.input);
    let parsed;
    try { parsed = new URL(vector.input); } catch { /* Invalid is part of the contract. */ }
    if (!parsed) {
      if (vector.throws !== 'TypeError' || Object.hasOwn(vector, 'expected')) {
        throw new Error('invalid input must expect TypeError, not a result');
      }
      invalid++;
      relative ||= /^\/(?!\/)/.test(vector.input);
      continue;
    }
    if (Object.hasOwn(vector, 'throws') || !vector.expected || typeof vector.expected !== 'object') {
      throw new Error('valid input must have literal expected fields, not an exception');
    }
    for (const field of fields) {
      if (typeof vector.expected[field] !== 'string' || vector.expected[field] !== parsed[field]) {
        throw new Error(`incorrect literal ${field} expectation for ${JSON.stringify(vector.input)}`);
      }
    }
    valid++;
    path ||= parsed.pathname !== '' && parsed.pathname !== '/';
    query ||= parsed.search !== '';
    fragment ||= parsed.hash !== '';
    // Whitespace trimming alone is not the requested URL normalization case.
    normalized ||= parsed.href !== vector.input.trim();
  }
  if (valid < 2 || invalid < 2 || !relative || !path || !query || !fragment || !normalized) {
    throw new Error('missing valid/invalid, relative-path, path, query, fragment or normalization coverage');
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    if (process.argv.length !== 3) throw new Error('usage: url_test_vectors.mjs OUTPUT_DIR');
    const output = join(process.argv[2], 'output.md');
    if (statSync(output).size > 128 * 1024) throw new Error('output exceeds 128 KiB');
    checkVectors(readFileSync(output, 'utf8'));
    console.log('PASS: literal URL test vectors (data-only; candidate tests not executed)');
  } catch (error) {
    console.error(`FAIL: ${error.message}`);
    process.exitCode = 1;
  }
}
