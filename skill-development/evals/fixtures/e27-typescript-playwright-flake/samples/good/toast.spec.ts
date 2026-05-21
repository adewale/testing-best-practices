import { test, expect } from '@playwright/test';

test('shows saved toast after saving settings', async ({ page }) => {
  await page.goto('/settings');
  await page.getByRole('button', { name: 'Save settings' }).click();
  await expect(page.getByRole('status', { name: /saved/i })).toBeVisible();
  await expect(page.getByRole('status')).toContainText('Saved');
});
