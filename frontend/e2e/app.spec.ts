import { test, expect } from '@playwright/test';

test('aws dropdown selection with reserved pricing', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByTestId('calculate-btn')).toBeVisible({ timeout: 15000 });
  await page.getByRole('button', { name: /aws/i }).click();
  await page.getByRole('button', { name: 'General Purpose' }).click();

  const familySelect = page.getByLabel('AWS family');
  await expect(familySelect.locator('option[value="m6i"]')).toHaveCount(1, { timeout: 15000 });
  await familySelect.selectOption('m6i');

  const skuSelect = page.getByLabel('AWS SKU');
  await expect(skuSelect.locator('option[value="m6i.xlarge"]')).toHaveCount(1, { timeout: 15000 });
  await skuSelect.selectOption('m6i.xlarge');

  await page.getByRole('button', { name: /1-Yr Reserved/i }).click();

  await page.getByTestId('calculate-btn').click();

  const awsCard = page.locator('[data-testid="card-aws"]').first();
  await expect(awsCard).toBeVisible({ timeout: 15000 });
  await expect(awsCard).toContainText('m6i.xlarge');
  await expect(awsCard).toContainText('1-Yr Reserved');
});
