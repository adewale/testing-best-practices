import { describe, expect, it } from 'vitest';
import { sanitizeUrl } from '../src/sanitize-url';

describe('sanitizeUrl', () => {
  it('removes javascript URLs while preserving safe URLs', () => {
    expect(sanitizeUrl('javascript:alert(document.cookie)')).toEqual('');
    expect(sanitizeUrl('JaVaScRiPt:alert(1)')).not.toContain('javascript:');
    expect(sanitizeUrl('https://example.com/path?q=1')).toBe('https://example.com/path?q=1');
    expect(sanitizeUrl('/safe/relative')).toBe('/safe/relative');
  });
});
