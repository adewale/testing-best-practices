import { test, expect } from 'vitest';

test.skip('registers plugin', () => {
  registry.register('alpha');
  expect(registry.names()).toContain('alpha');
});
