/**
 * Simple HTML sanitizer that strips dangerous tags and attributes.
 * Used as eval fixture for test-writing prompts.
 */

const DANGEROUS_TAGS = ['script', 'style', 'iframe', 'object', 'embed', 'base'];
const DANGEROUS_ATTRS = ['onclick', 'onerror', 'onload', 'onmouseover', 'onfocus'];

export function sanitize(html: string): string {
  if (!html) return '';

  let result = html;

  // Remove dangerous tags and their content
  for (const tag of DANGEROUS_TAGS) {
    const regex = new RegExp(`<${tag}[^>]*>[\\s\\S]*?<\\/${tag}>`, 'gi');
    result = result.replace(regex, '');
    // Also remove self-closing variants
    const selfClosing = new RegExp(`<${tag}[^>]*\\/?>`, 'gi');
    result = result.replace(selfClosing, '');
  }

  // Remove dangerous attributes
  for (const attr of DANGEROUS_ATTRS) {
    const regex = new RegExp(`\\s${attr}\\s*=\\s*["'][^"']*["']`, 'gi');
    result = result.replace(regex, '');
  }

  // Remove javascript: and data: URLs from href/src
  result = result.replace(/\s(href|src)\s*=\s*["']\s*(javascript|data):[^"']*["']/gi, '');

  return result.trim();
}

export function stripAllTags(html: string): string {
  return html.replace(/<[^>]+>/g, '').trim();
}

export function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
  };
  return text.replace(/[&<>"']/g, (char) => map[char]);
}
