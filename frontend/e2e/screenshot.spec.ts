import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

test('take overview screenshot after calculate', async ({ page }) => {
  await page.goto('/');
  await page.getByTestId('calculate-btn').click();
  // wait for any card to render
  await page.locator('[data-testid^="card-"]').first().waitFor({ state: 'visible', timeout: 10000 });

  // ensure screenshots directory
  const dir = path.resolve(__dirname, '..', 'screenshots');
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

  const main = page.locator('div.page-root');
  await main.screenshot({ path: path.join(dir, 'overview.png'), animations: 'disabled' });
  expect(fs.existsSync(path.join(dir, 'overview.png'))).toBeTruthy();
});
