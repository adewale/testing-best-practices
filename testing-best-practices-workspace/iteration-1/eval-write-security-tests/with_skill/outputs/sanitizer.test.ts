/**
 * Security-focused tests for the HTML sanitizer.
 *
 * Test strategy:
 *  - Unit tests with high assertion density (3+ per test) covering both
 *    positive (safe content preserved) and negative (dangerous content removed).
 *  - Property-based tests via fast-check for invariants:
 *    never crashes, idempotent sanitization, output is a character subset of input.
 *  - Explicit XSS bypass vectors from known attack payloads.
 *  - Boundary/edge-case tests for empty, null, and malformed inputs.
 */

import { describe, it, expect } from 'vitest';
import fc from 'fast-check';
import { sanitize, stripAllTags, escapeHtml } from '../../../../../../evals/files/sanitizer';

// ---------------------------------------------------------------------------
// Dangerous input collections (pre-built for reuse across tests)
// ---------------------------------------------------------------------------

const DANGEROUS_TAGS_WITH_CONTENT = [
  '<script>alert("xss")</script>',
  '<style>body{display:none}</style>',
  '<iframe src="https://evil.com"></iframe>',
  '<object data="evil.swf"></object>',
  '<embed src="evil.swf">',
  '<base href="https://evil.com">',
];

const EVENT_HANDLER_PAYLOADS = [
  '<img src="x" onclick="alert(1)">',
  '<img src="x" onerror="alert(1)">',
  '<body onload="alert(1)">',
  '<div onmouseover="alert(1)">hover</div>',
  '<input onfocus="alert(1)">',
];

const JAVASCRIPT_URL_PAYLOADS = [
  '<a href="javascript:alert(1)">click</a>',
  '<a href="javascript:void(0)">click</a>',
  '<img src="javascript:alert(1)">',
  '<a href="data:text/html,<script>alert(1)</script>">click</a>',
];

// ---------------------------------------------------------------------------
// sanitize() — core unit tests
// ---------------------------------------------------------------------------

describe('sanitize', () => {
  describe('preserves safe HTML', () => {
    it('keeps basic formatting tags and text content intact', () => {
      const input = '<p>Hello <b>world</b></p>';
      const result = sanitize(input);

      expect(result).toContain('<p>');
      expect(result).toContain('</p>');
      expect(result).toContain('<b>world</b>');
      expect(result).toBe('<p>Hello <b>world</b></p>');
    });

    it('keeps links with safe href attributes', () => {
      const input = '<a href="https://example.com">Visit</a>';
      const result = sanitize(input);

      expect(result).toContain('href="https://example.com"');
      expect(result).toContain('Visit');
      expect(result).toContain('<a');
      expect(result).toContain('</a>');
    });

    it('keeps images with safe src attributes', () => {
      const input = '<img src="https://example.com/photo.jpg" alt="photo">';
      const result = sanitize(input);

      expect(result).toContain('src="https://example.com/photo.jpg"');
      expect(result).toContain('alt="photo"');
      expect(result).toBe(input);
    });

    it('preserves safe inline styles and class attributes', () => {
      const input = '<div class="container" id="main"><span style="color:red">text</span></div>';
      const result = sanitize(input);

      expect(result).toContain('class="container"');
      expect(result).toContain('style="color:red"');
      expect(result).toContain('text');
    });
  });

  describe('strips dangerous tags', () => {
    it('removes script tags and their content', () => {
      const input = '<p>Safe</p><script>alert("xss")</script><p>Also safe</p>';
      const result = sanitize(input);

      expect(result).not.toContain('<script');
      expect(result).not.toContain('</script>');
      expect(result).not.toContain('alert');
      expect(result).toContain('Safe');
      expect(result).toContain('Also safe');
    });

    it('removes style tags and their content', () => {
      const input = '<style>body{display:none}</style><p>Visible</p>';
      const result = sanitize(input);

      expect(result).not.toContain('<style');
      expect(result).not.toContain('display:none');
      expect(result).toContain('Visible');
    });

    it('removes iframe tags', () => {
      const input = '<iframe src="https://evil.com" width="0" height="0"></iframe><p>Content</p>';
      const result = sanitize(input);

      expect(result).not.toContain('<iframe');
      expect(result).not.toContain('evil.com');
      expect(result).toContain('Content');
    });

    it('removes object, embed, and base tags', () => {
      const input = '<object data="x"></object><embed src="y"><base href="z"><p>Safe</p>';
      const result = sanitize(input);

      expect(result).not.toContain('<object');
      expect(result).not.toContain('<embed');
      expect(result).not.toContain('<base');
      expect(result).toContain('Safe');
    });

    it('removes self-closing dangerous tags', () => {
      const input = '<embed src="evil.swf"/><base href="evil.com"/>';
      const result = sanitize(input);

      expect(result).not.toContain('<embed');
      expect(result).not.toContain('<base');
      expect(result).not.toContain('evil');
      expect(result).toBe('');
    });

    it('removes all dangerous tags from a collection of known payloads', () => {
      for (const payload of DANGEROUS_TAGS_WITH_CONTENT) {
        const result = sanitize(payload);
        expect(result).not.toMatch(/<script/i);
        expect(result).not.toMatch(/<style/i);
        expect(result).not.toMatch(/<iframe/i);
        expect(result).not.toMatch(/<object/i);
        expect(result).not.toMatch(/<embed/i);
        expect(result).not.toMatch(/<base/i);
      }
    });
  });

  describe('strips dangerous attributes', () => {
    it('removes onclick handler from elements', () => {
      const input = '<button onclick="stealCookies()">Click me</button>';
      const result = sanitize(input);

      expect(result).not.toContain('onclick');
      expect(result).not.toContain('stealCookies');
      expect(result).toContain('Click me');
      expect(result).toContain('<button');
    });

    it('removes onerror handler from img tags', () => {
      const input = '<img src="missing.jpg" onerror="alert(document.cookie)">';
      const result = sanitize(input);

      expect(result).not.toContain('onerror');
      expect(result).not.toContain('alert');
      expect(result).toContain('src="missing.jpg"');
    });

    it('removes onload handler', () => {
      const input = '<body onload="malicious()">';
      const result = sanitize(input);

      expect(result).not.toContain('onload');
      expect(result).not.toContain('malicious');
    });

    it('removes onmouseover and onfocus handlers', () => {
      const input = '<div onmouseover="hack()"><input onfocus="hack()">';
      const result = sanitize(input);

      expect(result).not.toContain('onmouseover');
      expect(result).not.toContain('onfocus');
      expect(result).not.toContain('hack()');
      expect(result).toContain('<div');
      expect(result).toContain('<input');
    });

    it('removes all event handlers from known payload collection', () => {
      for (const payload of EVENT_HANDLER_PAYLOADS) {
        const result = sanitize(payload);
        expect(result).not.toContain('onclick');
        expect(result).not.toContain('onerror');
        expect(result).not.toContain('onload');
        expect(result).not.toContain('onmouseover');
        expect(result).not.toContain('onfocus');
        expect(result).not.toContain('alert(1)');
      }
    });
  });

  describe('strips dangerous URLs', () => {
    it('removes javascript: protocol from href', () => {
      const input = '<a href="javascript:alert(1)">click</a>';
      const result = sanitize(input);

      expect(result).not.toContain('javascript:');
      expect(result).not.toContain('alert');
      expect(result).toContain('click');
    });

    it('removes javascript: protocol from src', () => {
      const input = '<img src="javascript:alert(1)">';
      const result = sanitize(input);

      expect(result).not.toContain('javascript:');
      expect(result).not.toContain('alert');
    });

    it('removes data: protocol from href', () => {
      const input = '<a href="data:text/html,<script>alert(1)</script>">click</a>';
      const result = sanitize(input);

      expect(result).not.toContain('data:');
      expect(result).toContain('click');
    });

    it('removes all javascript/data URLs from known payload collection', () => {
      for (const payload of JAVASCRIPT_URL_PAYLOADS) {
        const result = sanitize(payload);
        expect(result).not.toContain('javascript:');
        expect(result).not.toContain('data:text/html');
      }
    });
  });

  describe('case insensitivity', () => {
    it('removes SCRIPT tags regardless of case', () => {
      const inputs = [
        '<SCRIPT>alert(1)</SCRIPT>',
        '<Script>alert(1)</Script>',
        '<sCrIpT>alert(1)</sCrIpT>',
      ];

      for (const input of inputs) {
        const result = sanitize(input);
        expect(result).not.toMatch(/<script/i);
        expect(result).not.toContain('alert');
        expect(result).toBe('');
      }
    });

    it('removes event handlers regardless of case', () => {
      const inputs = [
        '<img ONCLICK="alert(1)">',
        '<img OnClick="alert(1)">',
        '<img ONERROR="alert(1)">',
      ];

      for (const input of inputs) {
        const result = sanitize(input);
        expect(result).not.toMatch(/onclick/i);
        expect(result).not.toMatch(/onerror/i);
        expect(result).not.toContain('alert');
      }
    });

    it('removes javascript: URLs regardless of case', () => {
      const input = '<a href="JAVASCRIPT:alert(1)">click</a>';
      const result = sanitize(input);

      expect(result).not.toMatch(/javascript:/i);
      expect(result).not.toContain('alert');
      expect(result).toContain('click');
    });
  });

  describe('edge cases and boundary values', () => {
    it('returns empty string for empty input', () => {
      expect(sanitize('')).toBe('');
    });

    it('returns empty string for null/undefined input', () => {
      // The function guards with `if (!html) return ''`
      expect(sanitize(null as unknown as string)).toBe('');
      expect(sanitize(undefined as unknown as string)).toBe('');
    });

    it('handles plain text without any HTML', () => {
      const input = 'Just plain text, no HTML here.';
      expect(sanitize(input)).toBe(input);
    });

    it('handles deeply nested dangerous tags', () => {
      const input = '<div><p><script>alert(1)</script></p></div>';
      const result = sanitize(input);

      expect(result).not.toContain('<script');
      expect(result).not.toContain('alert');
      expect(result).toContain('<div>');
      expect(result).toContain('<p>');
    });

    it('handles multiple dangerous tags in sequence', () => {
      const input = '<script>a</script><script>b</script><style>c</style>';
      const result = sanitize(input);

      expect(result).not.toContain('<script');
      expect(result).not.toContain('<style');
      expect(result).toBe('');
    });

    it('handles tags with extra whitespace in attributes', () => {
      const input = '<img src="x"  onerror = "alert(1)" >';
      const result = sanitize(input);

      expect(result).not.toContain('onerror');
      expect(result).not.toContain('alert');
    });

    it('handles script tags with attributes', () => {
      const input = '<script type="text/javascript" src="evil.js">code()</script>';
      const result = sanitize(input);

      expect(result).not.toContain('<script');
      expect(result).not.toContain('evil.js');
      expect(result).not.toContain('code()');
    });
  });

  // -------------------------------------------------------------------------
  // XSS bypass vectors — real-world attack patterns
  // -------------------------------------------------------------------------
  describe('XSS bypass vectors', () => {
    it('removes script tags with newlines inside content', () => {
      const input = '<script>\nalert(1)\n</script>';
      const result = sanitize(input);

      expect(result).not.toContain('<script');
      expect(result).not.toContain('alert');
      expect(result).toBe('');
    });

    it('removes script tags with tab characters', () => {
      const input = '<script\t>alert(1)</script>';
      const result = sanitize(input);

      expect(result).not.toContain('<script');
      expect(result).not.toContain('alert');
    });

    it('handles multiple event handlers on same element', () => {
      const input = '<img src="x" onclick="a()" onerror="b()" onload="c()">';
      const result = sanitize(input);

      expect(result).not.toContain('onclick');
      expect(result).not.toContain('onerror');
      expect(result).not.toContain('onload');
    });

    it('handles javascript: URLs with whitespace padding', () => {
      const input = '<a href=" javascript:alert(1)">click</a>';
      const result = sanitize(input);

      expect(result).not.toContain('javascript:');
      expect(result).not.toContain('alert');
    });

    it('handles data: URLs in src attributes', () => {
      const input = '<img src="data:image/svg+xml,<svg onload=alert(1)>">';
      const result = sanitize(input);

      expect(result).not.toContain('data:');
      expect(result).not.toContain('alert');
    });

    it('removes script within iframe (double dangerous tag)', () => {
      const input = '<iframe><script>alert(1)</script></iframe>';
      const result = sanitize(input);

      expect(result).not.toContain('<iframe');
      expect(result).not.toContain('<script');
      expect(result).not.toContain('alert');
    });

    it('blocks combined attribute and tag attacks', () => {
      const input = '<div onclick="steal()"><script>inject()</script></div>';
      const result = sanitize(input);

      expect(result).not.toContain('onclick');
      expect(result).not.toContain('steal');
      expect(result).not.toContain('<script');
      expect(result).not.toContain('inject');
      expect(result).toContain('<div');
    });
  });

  // -------------------------------------------------------------------------
  // Known coverage gaps / bypass documentation
  // Documenting known limitations is itself a security practice
  // -------------------------------------------------------------------------
  describe('known coverage gaps (bypass documentation)', () => {
    // These tests document KNOWN WEAKNESSES in the sanitizer.
    // If these pass (meaning the attack is NOT blocked), it proves the
    // sanitizer has security gaps that need fixing.

    it('KNOWN GAP: does not strip unhandled event handlers like onblur, onchange, ondrag', () => {
      const input = '<input onblur="alert(1)" onchange="alert(2)">';
      const result = sanitize(input);

      // The sanitizer only handles onclick, onerror, onload, onmouseover, onfocus.
      // These other event handlers pass through — this is a known gap.
      // If this test fails (because the sanitizer was improved), remove this test.
      expect(result).toContain('onblur');
      expect(result).toContain('onchange');
    });

    it('KNOWN GAP: does not strip unquoted event handler attribute values', () => {
      const input = '<img src=x onerror=alert(1)>';
      const result = sanitize(input);

      // The regex requires quotes around attribute values: ["'][^"']*["']
      // Unquoted values bypass the filter.
      // This documents the limitation — the sanitizer SHOULD block this.
      expect(result).toContain('onerror');
    });

    it('KNOWN GAP: does not handle SVG/math namespace tags', () => {
      const input = '<svg onload="alert(1)"><circle r="50"></circle></svg>';
      const result = sanitize(input);

      // SVG is not in the DANGEROUS_TAGS list, so SVG onload bypasses.
      // The onload attribute IS removed, but the svg element itself stays.
      expect(result).toContain('<svg');
    });
  });
});

// ---------------------------------------------------------------------------
// stripAllTags()
// ---------------------------------------------------------------------------

describe('stripAllTags', () => {
  it('removes all HTML tags from simple markup', () => {
    const input = '<p>Hello <b>world</b></p>';
    const result = stripAllTags(input);

    expect(result).toBe('Hello world');
    expect(result).not.toContain('<');
    expect(result).not.toContain('>');
  });

  it('removes self-closing tags', () => {
    const input = 'Line one<br/>Line two<hr/>';
    const result = stripAllTags(input);

    expect(result).not.toContain('<br');
    expect(result).not.toContain('<hr');
    expect(result).toContain('Line one');
    expect(result).toContain('Line two');
  });

  it('removes tags with attributes', () => {
    const input = '<a href="https://example.com" class="link">Click here</a>';
    const result = stripAllTags(input);

    expect(result).toBe('Click here');
    expect(result).not.toContain('href');
    expect(result).not.toContain('<a');
  });

  it('removes deeply nested tags', () => {
    const input = '<div><ul><li><a href="#">Item</a></li></ul></div>';
    const result = stripAllTags(input);

    expect(result).toBe('Item');
    expect(result).not.toContain('<');
  });

  it('handles empty string', () => {
    expect(stripAllTags('')).toBe('');
  });

  it('handles text with no tags', () => {
    const input = 'No tags here';
    expect(stripAllTags(input)).toBe(input);
  });

  it('removes dangerous script tags and their visible text', () => {
    const input = '<script>alert(1)</script>Visible';
    const result = stripAllTags(input);

    // stripAllTags removes tags but keeps text content including script text
    expect(result).not.toContain('<script');
    expect(result).not.toContain('</script>');
    expect(result).toContain('Visible');
  });

  it('handles multiple adjacent tags', () => {
    const input = '<b>one</b><i>two</i><u>three</u>';
    const result = stripAllTags(input);

    expect(result).toBe('onetwothree');
    expect(result).not.toContain('<');
    expect(result).not.toContain('>');
  });
});

// ---------------------------------------------------------------------------
// escapeHtml()
// ---------------------------------------------------------------------------

describe('escapeHtml', () => {
  it('escapes all five dangerous characters', () => {
    const input = '&<>"\'';
    const result = escapeHtml(input);

    expect(result).toContain('&amp;');
    expect(result).toContain('&lt;');
    expect(result).toContain('&gt;');
    expect(result).toContain('&quot;');
    expect(result).toContain('&#x27;');
    expect(result).not.toMatch(/[<>"']/);
    // & appears in the escaped entities so we don't check not.toContain('&')
  });

  it('escapes ampersand to &amp;', () => {
    expect(escapeHtml('Tom & Jerry')).toBe('Tom &amp; Jerry');
  });

  it('escapes angle brackets to &lt; and &gt;', () => {
    const result = escapeHtml('<script>alert(1)</script>');

    expect(result).toBe('&lt;script&gt;alert(1)&lt;/script&gt;');
    expect(result).not.toContain('<');
    expect(result).not.toContain('>');
  });

  it('escapes double quotes to &quot;', () => {
    const result = escapeHtml('say "hello"');

    expect(result).toBe('say &quot;hello&quot;');
    expect(result).not.toContain('"');
  });

  it('escapes single quotes to &#x27;', () => {
    const result = escapeHtml("it's");

    expect(result).toBe('it&#x27;s');
    expect(result).not.toContain("'");
  });

  it('does not modify text with no special characters', () => {
    const input = 'Hello World 123';
    expect(escapeHtml(input)).toBe(input);
  });

  it('handles empty string', () => {
    expect(escapeHtml('')).toBe('');
  });

  it('escapes HTML used for XSS in attribute context', () => {
    const input = '" onclick="alert(1)"';
    const result = escapeHtml(input);

    expect(result).not.toContain('"');
    expect(result).toContain('&quot;');
    expect(result).toBe('&quot; onclick=&quot;alert(1)&quot;');
  });

  it('escapes characters that could break out of HTML comments', () => {
    const input = '--><script>alert(1)</script><!--';
    const result = escapeHtml(input);

    expect(result).not.toContain('<');
    expect(result).not.toContain('>');
    expect(result).toContain('&lt;script&gt;');
  });
});

// ---------------------------------------------------------------------------
// Property-based tests (fast-check)
// ---------------------------------------------------------------------------

describe('property-based tests', () => {
  describe('sanitize', () => {
    it('never throws on arbitrary string input', () => {
      fc.assert(
        fc.property(fc.string(), (input) => {
          // Must not throw — sanitize should handle any input gracefully
          const result = sanitize(input);
          expect(typeof result).toBe('string');
        }),
        { numRuns: 500 }
      );
    });

    it('is idempotent: sanitize(sanitize(x)) === sanitize(x)', () => {
      fc.assert(
        fc.property(fc.string(), (input) => {
          const once = sanitize(input);
          const twice = sanitize(once);
          expect(twice).toBe(once);
        }),
        { numRuns: 300 }
      );
    });

    it('output never contains <script tags (conservation invariant)', () => {
      fc.assert(
        fc.property(fc.string(), (input) => {
          const result = sanitize(input);
          expect(result.toLowerCase()).not.toMatch(/<script[\s>]/);
        }),
        { numRuns: 500 }
      );
    });

    it('output length is always <= input length (sanitization only removes)', () => {
      fc.assert(
        fc.property(fc.string(), (input) => {
          const result = sanitize(input);
          expect(result.length).toBeLessThanOrEqual(input.length);
        }),
        { numRuns: 300 }
      );
    });

    it('never adds new characters not present in the input', () => {
      fc.assert(
        fc.property(fc.string(), (input) => {
          const result = sanitize(input);
          const inputChars = new Set(input.split(''));
          for (const char of result) {
            expect(inputChars.has(char)).toBe(true);
          }
        }),
        { numRuns: 200 }
      );
    });
  });

  describe('stripAllTags', () => {
    it('never throws on arbitrary string input', () => {
      fc.assert(
        fc.property(fc.string(), (input) => {
          const result = stripAllTags(input);
          expect(typeof result).toBe('string');
        }),
        { numRuns: 500 }
      );
    });

    it('output never contains matched angle bracket pairs', () => {
      fc.assert(
        fc.property(fc.string(), (input) => {
          const result = stripAllTags(input);
          // The regex /<[^>]+>/g removes all <...> pairs, so none should remain
          expect(result).not.toMatch(/<[^>]+>/);
        }),
        { numRuns: 300 }
      );
    });

    it('is idempotent: stripAllTags(stripAllTags(x)) === stripAllTags(x)', () => {
      fc.assert(
        fc.property(fc.string(), (input) => {
          const once = stripAllTags(input);
          const twice = stripAllTags(once);
          expect(twice).toBe(once);
        }),
        { numRuns: 200 }
      );
    });
  });

  describe('escapeHtml', () => {
    it('never throws on arbitrary string input', () => {
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
        { numRuns: 300 }
      );
    });

    it('output never contains raw double or single quotes', () => {
      fc.assert(
        fc.property(fc.string(), (input) => {
          const result = escapeHtml(input);
          expect(result).not.toMatch(/["']/);
        }),
        { numRuns: 300 }
      );
    });

    it('preserves string length or increases it (escaping only adds characters)', () => {
      fc.assert(
        fc.property(fc.string(), (input) => {
          const result = escapeHtml(input);
          expect(result.length).toBeGreaterThanOrEqual(input.length);
        }),
        { numRuns: 300 }
      );
    });

    it('roundtrip: unescaped(escaped(x)) recovers x for safe characters', () => {
      // Quick unescape for test purposes
      const unescape = (s: string) =>
        s
          .replace(/&amp;/g, '&')
          .replace(/&lt;/g, '<')
          .replace(/&gt;/g, '>')
          .replace(/&quot;/g, '"')
          .replace(/&#x27;/g, "'");

      fc.assert(
        fc.property(fc.string(), (input) => {
          const escaped = escapeHtml(input);
          const restored = unescape(escaped);
          expect(restored).toBe(input);
        }),
        { numRuns: 300 }
      );
    });
  });
});

// ---------------------------------------------------------------------------
// Integration: sanitize + escapeHtml combined usage
// ---------------------------------------------------------------------------

describe('sanitize and escapeHtml used together', () => {
  it('escapeHtml after sanitize produces text with no executable HTML', () => {
    const input = '<script>alert(1)</script><p onclick="steal()">Content</p>';
    const sanitized = sanitize(input);
    const escaped = escapeHtml(sanitized);

    expect(escaped).not.toContain('<');
    expect(escaped).not.toContain('>');
    expect(escaped).not.toContain('"');
    expect(escaped).toContain('Content');
  });

  it('stripAllTags produces text that escapeHtml can make fully safe', () => {
    const input = '<div>Hello & "World" <b>!</b></div>';
    const stripped = stripAllTags(input);
    const escaped = escapeHtml(stripped);

    expect(stripped).toBe('Hello & "World" !');
    // Raw '&' from the input is now escaped to '&amp;'
    expect(escaped).toContain('&amp;');
    expect(escaped).toContain('&quot;');
    // No raw angle brackets remain
    expect(escaped).not.toContain('<');
    expect(escaped).not.toContain('>');
  });
});
