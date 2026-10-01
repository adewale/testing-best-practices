import { test, expect } from '@playwright/test';

test('site header renders consistently', async ({ page }) => {
  await page.goto('/');
  await page.evaluate(() => document.fonts.ready);
  await expect(page.locator('.site-header')).toHaveScreenshot('site-header.png', {
    animations: 'disabled',
    maxDiffPixelRatio: 0.01,
  });
});
