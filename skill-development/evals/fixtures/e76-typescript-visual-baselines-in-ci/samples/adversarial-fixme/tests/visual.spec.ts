import { test, expect } from '@playwright/test';

test.fixme(!!process.env.CI, 'baselines are darwin-only');

test('site header', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('.site-header')).toHaveScreenshot('site-header.png');
});
