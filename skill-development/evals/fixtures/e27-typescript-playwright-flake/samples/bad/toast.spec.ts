import { test, expect } from '@playwright/test';

test.only('shows saved toast', async ({ page }) => {
  await page.goto('/settings');
  await page.locator('.save').click();
  await page.waitForTimeout(5000);
  expect(await page.locator('.toast').textContent()).toBeTruthy();
});
