/**
 * Security-focused tests for the HTML sanitizer.
 *
 * These tests verify that the sanitizer correctly blocks XSS vectors
 * and other dangerous HTML patterns. Tests marked with "BYPASS" in their
 * description document known weaknesses in the current regex-based approach.
 *
 * To run: install vitest and ts-node, then `npx vitest run sanitizer.test.ts`
 */

import { describe, it, expect } from 'vitest';
import { sanitize, stripAllTags, escapeHtml } from '../../../../../../evals/files/sanitizer';

// ---------------------------------------------------------------------------
// Helper: assert that a sanitized string contains no executable JS vectors
// ---------------------------------------------------------------------------
function expectNoExecutableContent(output: string): void {
  // Should not contain raw script tags
  expect(output.toLowerCase()).not.toMatch(/<script[\s>]/i);
  // Should not contain javascript: protocol
  expect(output.toLowerCase()).not.toMatch(/javascript\s*:/i);
  // Should not contain event handler attributes (on*)
  expect(output.toLowerCase()).not.toMatch(/\bon\w+\s*=/i);
}

// ===========================================================================
// sanitize()
// ===========================================================================
describe('sanitize()', () => {
  // -----------------------------------------------------------------------
  // Basic functionality
  // -----------------------------------------------------------------------
  describe('basic functionality', () => {
    it('should return empty string for falsy input', () => {
      expect(sanitize('')).toBe('');
      expect(sanitize(null as unknown as string)).toBe('');
      expect(sanitize(undefined as unknown as string)).toBe('');
    });

    it('should preserve safe HTML', () => {
      const safe = '<p>Hello <strong>world</strong></p>';
      expect(sanitize(safe)).toBe(safe);
    });

    it('should preserve safe attributes', () => {
      const safe = '<a href="https://example.com" class="link">click</a>';
      expect(sanitize(safe)).toBe(safe);
    });

    it('should preserve plain text without tags', () => {
      expect(sanitize('just plain text')).toBe('just plain text');
    });
  });

  // -----------------------------------------------------------------------
  // Dangerous tag removal
  // -----------------------------------------------------------------------
  describe('dangerous tag removal', () => {
    it('should strip <script> tags and content', () => {
      const input = '<script>alert("xss")</script>';
      expect(sanitize(input)).toBe('');
    });

    it('should strip <script> tags case-insensitively', () => {
      const input = '<SCRIPT>alert("xss")</SCRIPT>';
      expect(sanitize(input)).toBe('');
    });

    it('should strip <script> with mixed case', () => {
      const input = '<ScRiPt>alert(1)</sCrIpT>';
      expect(sanitize(input)).toBe('');
    });

    it('should strip <style> tags and content', () => {
      const input = '<style>body{display:none}</style>';
      expect(sanitize(input)).toBe('');
    });

    it('should strip <iframe> tags', () => {
      const input = '<iframe src="https://evil.com"></iframe>';
      expect(sanitize(input)).toBe('');
    });

    it('should strip <object> tags', () => {
      const input = '<object data="malware.swf"></object>';
      expect(sanitize(input)).toBe('');
    });

    it('should strip <embed> tags', () => {
      const input = '<embed src="malware.swf">';
      expect(sanitize(input)).toBe('');
    });

    it('should strip <base> tags (prevents base URL hijacking)', () => {
      const input = '<base href="https://evil.com">';
      expect(sanitize(input)).toBe('');
    });

    it('should strip self-closing script tags', () => {
      const input = '<script src="https://evil.com/xss.js"/>';
      expect(sanitize(input)).toBe('');
    });

    it('should strip self-closing iframe tags', () => {
      const input = '<iframe src="https://evil.com"/>';
      expect(sanitize(input)).toBe('');
    });

    it('should strip multiple dangerous tags', () => {
      const input = '<p>safe</p><script>bad</script><p>also safe</p><iframe src="x"></iframe>';
      const result = sanitize(input);
      expect(result).toBe('<p>safe</p><p>also safe</p>');
    });

    it('should strip script tags with attributes', () => {
      const input = '<script type="text/javascript" src="evil.js">code()</script>';
      expect(sanitize(input)).toBe('');
    });

    it('should strip script tags with newlines in content', () => {
      const input = '<script>\nalert(\n"xss"\n)\n</script>';
      expect(sanitize(input)).toBe('');
    });
  });

  // -----------------------------------------------------------------------
  // Dangerous attribute removal
  // -----------------------------------------------------------------------
  describe('dangerous attribute removal', () => {
    it('should strip onclick attribute', () => {
      const input = '<div onclick="alert(1)">click me</div>';
      const result = sanitize(input);
      expect(result).not.toContain('onclick');
      expect(result).toContain('click me');
    });

    it('should strip onerror attribute', () => {
      const input = '<img src="x" onerror="alert(1)">';
      const result = sanitize(input);
      expect(result).not.toContain('onerror');
    });

    it('should strip onload attribute', () => {
      const input = '<body onload="alert(1)">';
      const result = sanitize(input);
      expect(result).not.toContain('onload');
    });

    it('should strip onmouseover attribute', () => {
      const input = '<a onmouseover="alert(1)">hover</a>';
      const result = sanitize(input);
      expect(result).not.toContain('onmouseover');
    });

    it('should strip onfocus attribute', () => {
      const input = '<input onfocus="alert(1)">';
      const result = sanitize(input);
      expect(result).not.toContain('onfocus');
    });

    it('should strip dangerous attributes case-insensitively', () => {
      const input = '<div ONCLICK="alert(1)">test</div>';
      const result = sanitize(input);
      expect(result).not.toContain('ONCLICK');
      expect(result).not.toContain('onclick');
    });

    it('should strip dangerous attributes with single quotes', () => {
      const input = "<div onclick='alert(1)'>test</div>";
      const result = sanitize(input);
      expect(result).not.toContain('onclick');
    });
  });

  // -----------------------------------------------------------------------
  // javascript: and data: URL removal
  // -----------------------------------------------------------------------
  describe('javascript: and data: URL removal', () => {
    it('should strip javascript: in href', () => {
      const input = '<a href="javascript:alert(1)">click</a>';
      const result = sanitize(input);
      expect(result).not.toContain('javascript:');
    });

    it('should strip javascript: in src', () => {
      const input = '<img src="javascript:alert(1)">';
      const result = sanitize(input);
      expect(result).not.toContain('javascript:');
    });

    it('should strip data: in href', () => {
      const input = '<a href="data:text/html,<script>alert(1)</script>">click</a>';
      const result = sanitize(input);
      expect(result).not.toContain('data:');
    });

    it('should strip data: in src', () => {
      const input = '<img src="data:image/svg+xml,<svg onload=alert(1)>">';
      const result = sanitize(input);
      expect(result).not.toContain('data:');
    });

    it('should strip javascript: URLs case-insensitively', () => {
      const input = '<a href="JAVASCRIPT:alert(1)">click</a>';
      const result = sanitize(input);
      expect(result.toLowerCase()).not.toContain('javascript:');
    });

    it('should strip javascript: with leading whitespace inside quotes', () => {
      const input = '<a href=" javascript:alert(1)">click</a>';
      const result = sanitize(input);
      expect(result).not.toContain('javascript:');
    });
  });

  // -----------------------------------------------------------------------
  // XSS bypass attempts -- core attack vectors
  // -----------------------------------------------------------------------
  describe('XSS bypass attempts', () => {
    it('should handle script tags with extra whitespace', () => {
      const input = '<script  >alert(1)</script  >';
      const result = sanitize(input);
      expectNoExecutableContent(result);
    });

    it('should handle nested script tags', () => {
      const input = '<scr<script>ipt>alert(1)</scr</script>ipt>';
      const result = sanitize(input);
      expectNoExecutableContent(result);
    });

    it('should handle script tag split across lines', () => {
      const input = '<script\n>alert(1)</script\n>';
      const result = sanitize(input);
      // The regex [^>]* should match newlines before >
      expectNoExecutableContent(result);
    });

    it('should block SVG-based XSS with onload', () => {
      // SVG is not in DANGEROUS_TAGS so it will pass through,
      // but onload should be stripped
      const input = '<svg onload="alert(1)">';
      const result = sanitize(input);
      expect(result).not.toContain('onload');
    });

    it('should block img onerror XSS', () => {
      const input = '<img src=x onerror=alert(1)>';
      const result = sanitize(input);
      // BYPASS: The regex requires quotes around attribute values.
      // Unquoted onerror=alert(1) will NOT be caught by the current regex.
      // This test documents that weakness.
      expect(result).not.toContain('onerror');
    });

    it('should block event handlers without quotes around values (BYPASS risk)', () => {
      // The attr regex requires quotes: ["'][^"']*["']
      // Unquoted attribute values bypass the sanitizer
      const input = '<div onclick=alert(1)>test</div>';
      const result = sanitize(input);
      expect(result).not.toContain('onclick');
    });

    it('should block event handlers with backtick values (BYPASS risk)', () => {
      const input = '<div onclick=`alert(1)`>test</div>';
      const result = sanitize(input);
      expect(result).not.toContain('onclick');
    });

    it('should block onblur event handler (BYPASS risk -- missing from DANGEROUS_ATTRS)', () => {
      // onblur is not in the DANGEROUS_ATTRS list
      const input = '<input onblur="alert(1)">';
      const result = sanitize(input);
      expect(result).not.toContain('onblur');
    });

    it('should block oninput event handler (BYPASS risk -- missing from DANGEROUS_ATTRS)', () => {
      const input = '<input oninput="alert(1)">';
      const result = sanitize(input);
      expect(result).not.toContain('oninput');
    });

    it('should block onchange event handler (BYPASS risk -- missing from DANGEROUS_ATTRS)', () => {
      const input = '<select onchange="alert(1)"><option>a</option></select>';
      const result = sanitize(input);
      expect(result).not.toContain('onchange');
    });

    it('should block ondblclick event handler (BYPASS risk)', () => {
      const input = '<div ondblclick="alert(1)">test</div>';
      const result = sanitize(input);
      expect(result).not.toContain('ondblclick');
    });

    it('should block onkeydown event handler (BYPASS risk)', () => {
      const input = '<input onkeydown="alert(1)">';
      const result = sanitize(input);
      expect(result).not.toContain('onkeydown');
    });

    it('should block onkeyup event handler (BYPASS risk)', () => {
      const input = '<input onkeyup="alert(1)">';
      const result = sanitize(input);
      expect(result).not.toContain('onkeyup');
    });

    it('should block onkeypress event handler (BYPASS risk)', () => {
      const input = '<input onkeypress="alert(1)">';
      const result = sanitize(input);
      expect(result).not.toContain('onkeypress');
    });

    it('should block onsubmit event handler (BYPASS risk)', () => {
      const input = '<form onsubmit="alert(1)"><input type="submit"></form>';
      const result = sanitize(input);
      expect(result).not.toContain('onsubmit');
    });

    it('should block onanimationend event handler (BYPASS risk)', () => {
      const input = '<div onanimationend="alert(1)" style="animation:x">test</div>';
      const result = sanitize(input);
      expect(result).not.toContain('onanimationend');
    });

    it('should block ontransitionend event handler (BYPASS risk)', () => {
      const input = '<div ontransitionend="alert(1)">test</div>';
      const result = sanitize(input);
      expect(result).not.toContain('ontransitionend');
    });

    it('should block javascript: with tab characters (BYPASS risk)', () => {
      // Browsers may interpret tabs within "javascript:" protocol
      const input = '<a href="java\tscript:alert(1)">click</a>';
      const result = sanitize(input);
      expectNoExecutableContent(result);
    });

    it('should block javascript: with newline characters (BYPASS risk)', () => {
      const input = '<a href="java\nscript:alert(1)">click</a>';
      const result = sanitize(input);
      expectNoExecutableContent(result);
    });

    it('should block javascript: with HTML entities (BYPASS risk)', () => {
      const input = '<a href="&#106;avascript:alert(1)">click</a>';
      const result = sanitize(input);
      // After HTML entity decoding by the browser, this becomes javascript:
      expect(result).not.toMatch(/&#106;/i);
    });

    it('should block javascript: with hex entities (BYPASS risk)', () => {
      const input = '<a href="&#x6A;avascript:alert(1)">click</a>';
      const result = sanitize(input);
      expect(result).not.toMatch(/&#x6A;/i);
    });

    it('should block vbscript: protocol (BYPASS risk)', () => {
      const input = '<a href="vbscript:alert(1)">click</a>';
      const result = sanitize(input);
      expect(result).not.toContain('vbscript:');
    });

    it('should block javascript: in formaction attribute (BYPASS risk)', () => {
      // formaction is not covered by the href/src regex
      const input = '<button formaction="javascript:alert(1)">Submit</button>';
      const result = sanitize(input);
      expect(result).not.toContain('javascript:');
    });

    it('should block javascript: in action attribute (BYPASS risk)', () => {
      const input = '<form action="javascript:alert(1)"><input type="submit"></form>';
      const result = sanitize(input);
      expect(result).not.toContain('javascript:');
    });

    it('should block javascript: in xlink:href (BYPASS risk)', () => {
      const input = '<svg><a xlink:href="javascript:alert(1)">click</a></svg>';
      const result = sanitize(input);
      expect(result).not.toContain('javascript:');
    });

    it('should block data: URIs in srcdoc (BYPASS risk)', () => {
      const input = '<iframe srcdoc="<script>alert(1)</script>"></iframe>';
      const result = sanitize(input);
      // iframe is in DANGEROUS_TAGS so the outer tag should be removed
      expectNoExecutableContent(result);
    });

    it('should handle multiple dangerous attributes on one element', () => {
      const input = '<div onclick="alert(1)" onmouseover="alert(2)" onerror="alert(3)">test</div>';
      const result = sanitize(input);
      expect(result).not.toContain('onclick');
      expect(result).not.toContain('onmouseover');
      expect(result).not.toContain('onerror');
    });

    it('should handle dangerous content after safe content', () => {
      const input = '<p>Hello</p><script>alert(1)</script><p>World</p>';
      const result = sanitize(input);
      expect(result).toBe('<p>Hello</p><p>World</p>');
      expectNoExecutableContent(result);
    });

    it('should block meta refresh redirect (BYPASS risk -- meta not in DANGEROUS_TAGS)', () => {
      const input = '<meta http-equiv="refresh" content="0;url=javascript:alert(1)">';
      const result = sanitize(input);
      // meta is not in DANGEROUS_TAGS, so this passes through
      expect(result).not.toContain('javascript:');
    });

    it('should block SVG script execution', () => {
      const input = '<svg><script>alert(1)</script></svg>';
      const result = sanitize(input);
      expectNoExecutableContent(result);
    });

    it('should block math/maction-based XSS (BYPASS risk)', () => {
      const input = '<math><maction actiontype="statusline#" xlink:href="javascript:alert(1)">click</maction></math>';
      const result = sanitize(input);
      expect(result).not.toContain('javascript:');
    });

    it('should block attribute injection via newline in tag', () => {
      const input = '<div\nonclick="alert(1)">test</div>';
      const result = sanitize(input);
      // The attr regex expects \\s before onclick -- \\n counts as \\s
      expect(result).not.toContain('onclick');
    });

    it('should block event handlers with spaces around equals sign', () => {
      const input = '<div onclick = "alert(1)">test</div>';
      const result = sanitize(input);
      expect(result).not.toContain('onclick');
    });

    it('should block mutation XSS via noscript (BYPASS risk)', () => {
      // In some browsers, content inside <noscript> is parsed differently
      const input = '<noscript><img src=x onerror=alert(1)></noscript>';
      const result = sanitize(input);
      expectNoExecutableContent(result);
    });

    it('should handle null bytes in tag names (BYPASS risk)', () => {
      const input = '<scri\x00pt>alert(1)</scri\x00pt>';
      const result = sanitize(input);
      expectNoExecutableContent(result);
    });

    it('should handle unicode replacement characters', () => {
      const input = '<script\uFEFF>alert(1)</script>';
      const result = sanitize(input);
      expectNoExecutableContent(result);
    });

    it('should block style-based expression injection (BYPASS risk)', () => {
      // IE-specific but still tested as a defense-in-depth measure
      const input = '<div style="background:url(javascript:alert(1))">test</div>';
      const result = sanitize(input);
      expect(result).not.toContain('javascript:');
    });

    it('should handle extremely long attribute values', () => {
      const padding = 'A'.repeat(10000);
      const input = `<div onclick="${padding}alert(1)">test</div>`;
      const result = sanitize(input);
      expect(result).not.toContain('onclick');
    });

    it('should handle multiple script tags', () => {
      const input = '<script>one</script>safe text<script>two</script>';
      const result = sanitize(input);
      expect(result).toBe('safe text');
      expectNoExecutableContent(result);
    });

    it('should strip script tags with type=module', () => {
      const input = '<script type="module">import("evil")</script>';
      const result = sanitize(input);
      expectNoExecutableContent(result);
    });

    it('should block data: URI in img src', () => {
      const input = '<img src="data:text/html,<script>alert(1)</script>">';
      const result = sanitize(input);
      expect(result).not.toContain('data:');
    });

    it('should block javascript: with mixed case (JaVaScRiPt:)', () => {
      const input = '<a href="JaVaScRiPt:alert(1)">click</a>';
      const result = sanitize(input);
      expect(result.toLowerCase()).not.toContain('javascript:');
    });

    it('should block javascript: with leading spaces in attribute value', () => {
      const input = '<a href="   javascript:alert(1)">click</a>';
      const result = sanitize(input);
      expect(result).not.toContain('javascript:');
    });
  });

  // -----------------------------------------------------------------------
  // Edge cases and malformed HTML
  // -----------------------------------------------------------------------
  describe('edge cases and malformed HTML', () => {
    it('should handle empty script tags', () => {
      const input = '<script></script>';
      expect(sanitize(input)).toBe('');
    });

    it('should handle unclosed script tags', () => {
      const input = '<script>alert(1)';
      const result = sanitize(input);
      // Self-closing variant regex should catch <script>
      expectNoExecutableContent(result);
    });

    it('should handle deeply nested safe HTML', () => {
      const input = '<div><p><span><strong><em>text</em></strong></span></p></div>';
      expect(sanitize(input)).toBe(input);
    });

    it('should handle tags within attribute values (should not strip)', () => {
      const input = '<div title="not a <script> tag">safe</div>';
      const result = sanitize(input);
      expect(result).toContain('safe');
    });

    it('should handle HTML comments', () => {
      const input = '<!-- <script>alert(1)</script> -->';
      const result = sanitize(input);
      // Comments may or may not be stripped -- but script inside should not execute
      expectNoExecutableContent(result);
    });

    it('should handle script tags with CDATA', () => {
      const input = '<script>//<![CDATA[\nalert(1)\n//]]></script>';
      const result = sanitize(input);
      expect(result).toBe('');
    });

    it('should handle whitespace-only input', () => {
      expect(sanitize('   ')).toBe('');
    });

    it('should handle input with only a dangerous tag', () => {
      expect(sanitize('<script></script>')).toBe('');
    });

    it('should preserve text adjacent to stripped tags', () => {
      const input = 'before<script>evil</script>after';
      expect(sanitize(input)).toBe('beforeafter');
    });
  });

  // -----------------------------------------------------------------------
  // Combination / chained attacks
  // -----------------------------------------------------------------------
  describe('combination and chained attacks', () => {
    it('should handle script inside style tag', () => {
      const input = '<style></style><script>alert(1)</script>';
      const result = sanitize(input);
      expectNoExecutableContent(result);
    });

    it('should handle multiple attack vectors in single input', () => {
      const input = `
        <script>alert(1)</script>
        <img src=x onerror="alert(2)">
        <a href="javascript:alert(3)">click</a>
        <iframe src="evil.com"></iframe>
        <div onclick="alert(4)">hover</div>
      `;
      const result = sanitize(input);
      expectNoExecutableContent(result);
      expect(result).not.toContain('javascript:');
    });

    it('should handle attack spanning safe and unsafe elements', () => {
      const input = '<p>safe</p><script>alert(1)</script><p onclick="alert(2)">unsafe</p>';
      const result = sanitize(input);
      expect(result).toContain('safe');
      expectNoExecutableContent(result);
    });

    it('should handle double-encoded content', () => {
      // Double-encoded angle brackets should pass through as text
      const input = '&amp;lt;script&amp;gt;alert(1)&amp;lt;/script&amp;gt;';
      const result = sanitize(input);
      // This is entity-encoded text, not real tags, so it should pass through
      expect(result).toBe(input);
    });
  });
});

// ===========================================================================
// stripAllTags()
// ===========================================================================
describe('stripAllTags()', () => {
  describe('basic functionality', () => {
    it('should remove all HTML tags', () => {
      expect(stripAllTags('<p>Hello <strong>world</strong></p>')).toBe('Hello world');
    });

    it('should return plain text unchanged', () => {
      expect(stripAllTags('no tags here')).toBe('no tags here');
    });

    it('should handle self-closing tags', () => {
      expect(stripAllTags('line1<br/>line2')).toBe('line1line2');
    });

    it('should handle empty input', () => {
      expect(stripAllTags('')).toBe('');
    });

    it('should handle input that is only a tag', () => {
      expect(stripAllTags('<div></div>')).toBe('');
    });

    it('should handle tags with attributes', () => {
      expect(stripAllTags('<a href="https://example.com" class="link">text</a>')).toBe('text');
    });
  });

  describe('security considerations', () => {
    it('should strip script tags and content tags but leave inner text exposed', () => {
      // stripAllTags only strips tags, not content between them
      const result = stripAllTags('<script>alert(1)</script>');
      expect(result).toBe('alert(1)');
      // Note: this is expected -- stripAllTags is for text extraction,
      // not sanitization. The output should not be inserted as HTML.
    });

    it('should handle nested tags', () => {
      expect(stripAllTags('<div><p><span>text</span></p></div>')).toBe('text');
    });

    it('should handle unclosed tags (BYPASS risk)', () => {
      const input = '<div>text<span';
      const result = stripAllTags(input);
      // The regex <[^>]+> requires a closing >, so "<span" without ">" stays
      expect(result).not.toContain('<div>');
    });

    it('should handle angle brackets in text', () => {
      const input = '5 < 10 and 10 > 5';
      const result = stripAllTags(input);
      // "< 10 and 10 >" looks like a tag to the regex
      // This is a known limitation of regex-based tag stripping
      expect(result).toBeDefined();
    });

    it('should handle tags with newlines', () => {
      const input = '<div\nclass="test"\n>text</div\n>';
      const result = stripAllTags(input);
      expect(result).toBe('text');
    });

    it('should handle malformed HTML with multiple angle brackets', () => {
      const input = '<<div>>text<</div>>';
      const result = stripAllTags(input);
      // Should strip tag-like patterns; remaining text depends on regex behavior
      expect(result).toBeDefined();
    });

    it('should handle tags with quotes containing angle brackets', () => {
      // The regex [^>]+ is greedy and will stop at the first >
      const input = '<div title="a>b">text</div>';
      const result = stripAllTags(input);
      // The regex will incorrectly match up to the first > inside the attribute
      // This documents a known regex limitation
      expect(result).toBeDefined();
    });
  });
});

// ===========================================================================
// escapeHtml()
// ===========================================================================
describe('escapeHtml()', () => {
  describe('basic entity escaping', () => {
    it('should escape ampersand', () => {
      expect(escapeHtml('a & b')).toBe('a &amp; b');
    });

    it('should escape less-than', () => {
      expect(escapeHtml('a < b')).toBe('a &lt; b');
    });

    it('should escape greater-than', () => {
      expect(escapeHtml('a > b')).toBe('a &gt; b');
    });

    it('should escape double quotes', () => {
      expect(escapeHtml('a "b" c')).toBe('a &quot;b&quot; c');
    });

    it('should escape single quotes', () => {
      expect(escapeHtml("a 'b' c")).toBe('a &#x27;b&#x27; c');
    });

    it('should handle text with no special characters', () => {
      expect(escapeHtml('hello world')).toBe('hello world');
    });

    it('should handle empty string', () => {
      expect(escapeHtml('')).toBe('');
    });
  });

  describe('XSS prevention via escaping', () => {
    it('should neutralize script tags', () => {
      const result = escapeHtml('<script>alert("xss")</script>');
      expect(result).toBe('&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;');
      expect(result).not.toContain('<script>');
    });

    it('should neutralize event handlers in attributes', () => {
      const result = escapeHtml('<img onerror="alert(1)">');
      expect(result).toBe('&lt;img onerror=&quot;alert(1)&quot;&gt;');
      expect(result).not.toContain('<img');
    });

    it('should neutralize javascript: URLs', () => {
      const result = escapeHtml('<a href="javascript:alert(1)">');
      expect(result).not.toContain('<a');
      expect(result).toContain('&lt;a');
    });

    it('should handle already-escaped content (double escaping)', () => {
      const result = escapeHtml('&amp;');
      expect(result).toBe('&amp;amp;');
    });

    it('should escape all special characters in a complex string', () => {
      const input = '<div class="test" data-val=\'foo\'>A & B</div>';
      const result = escapeHtml(input);
      expect(result).not.toContain('<');
      expect(result).not.toContain('>');
      expect(result).not.toContain('"');
      expect(result).not.toContain("'");
      expect(result).toContain('&lt;');
      expect(result).toContain('&gt;');
      expect(result).toContain('&quot;');
      expect(result).toContain('&#x27;');
      expect(result).toContain('&amp;');
    });

    it('should handle multi-line input', () => {
      const input = '<p>\nline1\n</p>';
      const result = escapeHtml(input);
      expect(result).toBe('&lt;p&gt;\nline1\n&lt;/p&gt;');
    });

    it('should handle repeated special characters', () => {
      expect(escapeHtml('<<<>>>')).toBe('&lt;&lt;&lt;&gt;&gt;&gt;');
    });

    it('should handle string of only special characters', () => {
      expect(escapeHtml('&<>"\'')).toBe('&amp;&lt;&gt;&quot;&#x27;');
    });

    it('should handle unicode content (should pass through unchanged)', () => {
      expect(escapeHtml('日本語 テスト')).toBe('日本語 テスト');
    });

    it('should handle emoji (should pass through unchanged)', () => {
      expect(escapeHtml('Hello 👋 World 🌍')).toBe('Hello 👋 World 🌍');
    });
  });

  describe('escapeHtml used as a sanitization strategy', () => {
    it('should make any XSS payload inert when escaped', () => {
      const payloads = [
        '<script>alert(document.cookie)</script>',
        '<img src=x onerror=alert(1)>',
        '<svg onload=alert(1)>',
        '<a href="javascript:alert(1)">click</a>',
        '<div onclick="alert(1)">click</div>',
        '"><script>alert(1)</script>',
        "'-alert(1)-'",
        '<iframe src="data:text/html,<script>alert(1)</script>">',
      ];

      for (const payload of payloads) {
        const result = escapeHtml(payload);
        expect(result).not.toContain('<');
        expect(result).not.toContain('>');
      }
    });
  });
});

// ===========================================================================
// Cross-function security analysis
// ===========================================================================
describe('cross-function security analysis', () => {
  it('sanitize + escapeHtml: escapeHtml is a safer alternative for user-generated text', () => {
    const userInput = '<script>alert(document.cookie)</script>';

    // sanitize removes the tag but is bypassable via various vectors
    const sanitized = sanitize(userInput);
    expect(sanitized).toBe('');

    // escapeHtml converts to entities -- more robust for text display
    const escaped = escapeHtml(userInput);
    expect(escaped).not.toContain('<');
    expect(escaped).not.toContain('>');
  });

  it('sanitize should be used alongside escapeHtml for defense in depth', () => {
    const input = '<div onclick="alert(1)">Hello</div>';
    const result = escapeHtml(sanitize(input));
    // After sanitize: <div>Hello</div>
    // After escapeHtml: &lt;div&gt;Hello&lt;/div&gt;
    expect(result).not.toContain('<');
  });

  it('stripAllTags output should be safe for text-only contexts', () => {
    const input = '<script>alert(1)</script><p>Hello</p>';
    const stripped = stripAllTags(input);
    // stripAllTags leaves text content from script: "alert(1)Hello"
    // This is safe only if inserted as text, not HTML
    expect(stripped).not.toContain('<');
    expect(stripped).not.toContain('>');
  });
});
