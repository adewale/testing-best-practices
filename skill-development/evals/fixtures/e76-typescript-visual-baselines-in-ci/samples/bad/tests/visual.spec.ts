import { test, expect } from '@playwright/test';

test.skip(!!process.env.CI, 'Visual tests skipped in CI (font rendering differs)');

test('site header', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('.site-header')).toHaveScreenshot('site-header.png');
});
