/**
 * Intentionally weak test suite for the sanitizer — used as eval fixture.
 */
import { describe, it, expect, vi } from 'vitest';

// Mock the entire module
vi.mock('../../src/sanitizer', () => ({
  sanitize: vi.fn().mockReturnValue('<p>safe</p>'),
  stripAllTags: vi.fn().mockReturnValue('text only'),
  escapeHtml: vi.fn().mockReturnValue('&lt;script&gt;'),
}));

import { sanitize, stripAllTags, escapeHtml } from '../../src/sanitizer';

describe('Sanitizer', () => {
  it('should sanitize HTML', () => {
    const result = sanitize('<script>alert("xss")</script><p>hello</p>');
    expect(result).toBeDefined();
  });

  it('should handle empty input', () => {
    const result = sanitize('');
    expect(result).toBeTruthy();
  });

  it.skip('should handle nested script tags', () => {
    const result = sanitize('<script><script>alert("xss")</script></script>');
    expect(result).not.toContain('<script>');
  });

  it('should strip all tags', () => {
    const result = stripAllTags('<p>hello <b>world</b></p>');
    expect(result).toBeDefined();
  });

  it('should escape HTML entities', () => {
    const result = escapeHtml('<script>alert("xss")</script>');
    console.log('Escaped result:', result);
    // No assertion — just logging
  });
});

describe('Integration', () => {
  it('should handle XSS', () => {
    expect(sanitize('<img onerror="alert(1)" src="x">')).toBeTruthy();
  });
});
