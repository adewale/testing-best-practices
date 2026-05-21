import { expect, test } from '@playwright/test';

test.describe('settings notifications', () => {
  test('shows the saved toast after saving changes', async ({ page }) => {
    await page.goto('/settings');

    const saveButton = page.getByRole('button', { name: /save/i });
    await expect(saveButton).toBeVisible();
    await expect(saveButton).toBeEnabled();

    await saveButton.click();

    const successToast = page.getByTestId('toast').filter({ hasText: /saved/i });
    await expect(successToast).toBeVisible({ timeout: 10_000 });
    await expect(successToast).toContainText(/saved/i);
  });
});
