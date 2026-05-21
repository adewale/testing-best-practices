import { describe, expect, it } from 'vitest';
import { sanitizeUrl } from '../src/sanitizer';

describe('sanitizeUrl', () => {
  it('removes dangerous javascript URLs while preserving safe URLs', () => {
    const dangerousUrls = [
      'javascript:alert(1)',
      'JavaScript:alert(1)',
      ' javascript:alert(1)',
      '\tjavascript:alert(1)',
    ];

    for (const url of dangerousUrls) {
      const sanitized = sanitizeUrl(url);
      expect(sanitized, `${url} should be removed`).toBe('');
      expect(sanitized).not.toContain('alert(1)');
      expect(sanitized).not.toMatch(/^\s*javascript:/i);
    }

    const safeUrls = [
      'https://example.com/docs?query=test#intro',
      'http://example.com/assets/logo.png',
      '/relative/path?next=/dashboard',
      './local-page.html',
    ];

    for (const url of safeUrls) {
      expect(sanitizeUrl(url)).toBe(url);
    }
  });
});
