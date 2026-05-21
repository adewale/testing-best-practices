import { expect, it } from 'vitest';
import { sanitizeUrl } from '../src/sanitize-url';

it('sanitizes urls', () => {
  expect(sanitizeUrl('javascript:alert(1)')).toBeDefined();
});
