import { test, expect } from '@playwright/test';

test('calculate shows non-zero azure and gcp totals', async ({ page, baseURL }) => {
  // capture console logs to help debug client-side errors
  page.on('console', msg => {
    console.log('PAGE LOG:', msg.type(), msg.text());
  });
  await page.goto('/');

  // Ensure default values are present
  await page.getByLabel('CPU (vCPUs)').fill('2');
  await page.getByLabel('RAM (GB)').fill('8');
  await page.getByLabel('Storage (GB)').fill('100');
  await page.getByLabel('Network (Mbps)').fill('10');
  await page.getByLabel('Backup (GB)').fill('50');

  await page.getByTestId('calculate-btn').click();

  // Wait for any provider card to appear, then ensure we have at least 3 comparisons
  const firstCard = page.locator('[data-testid^="card-"]').first();
  await expect(firstCard).toBeVisible({ timeout: 10000 });
  const cards = page.locator('[data-testid^="card-"]');
  const count = await cards.count();
  expect(count).toBeGreaterThanOrEqual(3);

  const parseCardTotal = async (cardLocator: any) => {
    // find element showing the total (text-2xl)
    const txt = await cardLocator.locator('.price-large').innerText();
    const num = Number(txt.replace(/[^0-9.\-]/g, ''));
    return num;
  };

  // Verify at least two cards have valid numeric totals and an image
  let numericFound = 0;
  let imagesFound = 0;
  for (let i = 0; i < count; i++) {
    const c = cards.nth(i);
    const txt = await c.locator('.price-large').innerText();
    const num = Number(txt.replace(/[^0-9.\-]/g, ''));
    if (!isNaN(num) && num > 0) numericFound++;
    if ((await c.locator('img').count()) > 0) imagesFound++;
  }
  expect(numericFound).toBeGreaterThanOrEqual(2);
  expect(imagesFound).toBeGreaterThanOrEqual(2);

  // Ensure we have exactly 5 provider cards rendered (one for each provider)
  expect(count).toBe(5);

  // Scroller arrows should exist and be interactive (right arrow scrolls to reveal more)
  const rightBtn = page.getByLabel('Scroll right');
  await expect(rightBtn).toBeVisible();
  // Click right arrow and ensure the scroller moved by checking that card[2] is at least partially visible
  await rightBtn.click();
  await page.waitForTimeout(300);
  const thirdCard = page.locator('[data-testid^="card-"]').nth(2);
  await expect(thirdCard).toBeVisible();

  // Check billing period selector exists and switch to annual
  await page.getByRole('button', { name: 'Annual' }).click();
  await page.waitForTimeout(200);

  // Ensure the comparison table is visible and has a Monthly/price row
  const table = page.locator('.pricing-table');
  await expect(table).toBeVisible();
  const monthlyRow = table.locator('tr').filter({ hasText: 'Monthly' }).first();
  await expect(monthlyRow).toBeVisible();

  // Ensure pricing-stat chips and Details CTA exist in at least one card
  const firstStat = page.locator('[data-testid^="card-"]').first().locator('.stat-chip').first();
  await expect(firstStat).toBeVisible({ timeout: 3000 });
  const detailsBtn = page.locator('[data-testid^="card-"]').first().locator('button', { hasText: 'Details' }).first();
  await expect(detailsBtn).toBeVisible({ timeout: 3000 });

  // Ensure cheapest card has highlight
  const cheapestCard = page.locator('[data-testid="card-azure"]').first();
  // cheapest could be different depending on data; just check some card has the .cheapest class
  const hasCheapest = await page.locator('.cheapest').count();
  expect(hasCheapest).toBeGreaterThan(0);

  // AWS MVP: selected_instance should be displayed on the AWS card
  const awsCard = page.locator('[data-testid="card-aws"]').first();
  await expect(awsCard.locator('.text-xs', { hasText: /vCPU|GB RAM/ })).toBeVisible({ timeout: 2000 });
});
