import { afterEach, expect, test } from 'vitest';
import { pluginRegistry } from '../src/registry';

afterEach(() => {
  pluginRegistry.reset(); // cleanup shared global registry pollution between tests
});

test('registers plugin without leaking order-dependent state', () => {
  pluginRegistry.register('alpha');
  expect(pluginRegistry.names()).toEqual(['alpha']);
});
