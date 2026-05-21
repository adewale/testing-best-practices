import { expect, test } from '@playwright/test';

test('shows a success toast after saving changes', async ({ page }) => {
  await page.goto('/settings');

  await page.getByRole('button', { name: /save/i }).click();

  const successToast = page.getByRole('status').filter({ hasText: /saved/i });
  await expect(successToast).toBeVisible({ timeout: 10_000 });
  await expect(successToast).toContainText(/saved/i);
});
