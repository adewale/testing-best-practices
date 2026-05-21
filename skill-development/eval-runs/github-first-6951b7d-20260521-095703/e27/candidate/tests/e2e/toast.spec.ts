import { expect, test, type Page } from '@playwright/test';

const TOAST_SELECTOR = '[role="status"], [role="alert"], [data-testid="toast"], [data-test="toast"]';
const SAVE_SUCCESS = /saved/i;

function toastMessages(page: Page) {
  return page.locator(TOAST_SELECTOR);
}

test.describe('settings save toast', () => {
  test('shows the success toast after saving changes', async ({ page }) => {
    await page.goto('/settings');

    await page.getByRole('button', { name: /^save$/i }).click();

    const successToast = toastMessages(page).filter({ hasText: SAVE_SUCCESS }).first();

    await expect(successToast).toBeVisible({ timeout: 10_000 });
    await expect(successToast).toContainText(SAVE_SUCCESS);
    await expect(toastMessages(page).filter({ hasText: /error|failed/i })).toHaveCount(0);
  });
});
