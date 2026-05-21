import { describe, expect, it } from 'vitest';
import { sanitizeUrl } from '../src/sanitizer';

describe('sanitizeUrl', () => {
  it.each([
    'javascript:alert(1)',
    'JavaScript:alert(1)',
    '  javascript:alert(1)',
    '\n\tjavascript:alert(document.cookie)',
  ])('rejects/removes dangerous javascript URLs: %s', (url) => {
    const sanitized = sanitizeUrl(url);
    const rendered = String(sanitized ?? '').toLowerCase();

    expect(sanitized).not.toBe(url);
    expect(rendered).not.toContain('javascript:');
    expect(rendered).not.toContain('alert(');
  });

  it.each([
    'https://example.com/docs?lang=en#intro',
    'http://example.com/assets/logo.png',
    '/docs/getting-started?tab=install#npm',
    'mailto:security@example.com',
  ])('preserves safe URLs: %s', (url) => {
    const sanitized = sanitizeUrl(url);

    expect(sanitized).toBe(url);
    expect(String(sanitized)).toContain(url.split(/[?#]/)[0]);
    expect(String(sanitized).toLowerCase()).not.toContain('javascript:');
  });
});
