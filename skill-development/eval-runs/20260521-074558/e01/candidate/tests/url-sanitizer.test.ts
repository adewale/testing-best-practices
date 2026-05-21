import { describe, expect, it } from 'vitest';
import { sanitizeUrl } from '../src/sanitizer';

describe('sanitizeUrl', () => {
  it.each([
    'javascript:alert(1)',
    'JavaScript:alert(1)',
    '  javascript:alert(1)',
    '\n\tjavascript:alert(1)',
  ])('removes dangerous javascript URL %j', (url) => {
    expect(sanitizeUrl(url)).toBe('');
  });

  it.each([
    'https://example.com/path?name=value#section',
    'http://example.com',
    '/docs/getting-started',
    '#content',
  ])('preserves safe URL %j', (url) => {
    expect(sanitizeUrl(url)).toBe(url);
  });
});
