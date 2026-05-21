export function sanitizeUrl(raw) {
  const value = String(raw ?? '').trim();
  if (/^javascript:/i.test(value)) return '';
  return raw;
}
