import { test, expect } from '@playwright/test';

test('aws dropdown selection with reserved pricing', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByTestId('calculate-btn')).toBeVisible({ timeout: 15000 });
  await page.getByRole('button', { name: /aws/i }).click();
  await page.getByRole('button', { name: 'General Purpose' }).click();

  const familySelect = page.getByLabel('AWS family');
  await expect(familySelect.locator('option[value="m5"]')).toHaveCount(1, { timeout: 15000 });
  await familySelect.selectOption('m5');

  const skuSelect = page.getByLabel('AWS SKU');
  await expect(skuSelect.locator('option[value="m5.xlarge"]')).toHaveCount(1, { timeout: 15000 });
  await skuSelect.selectOption('m5.xlarge');
  await expect(page.getByLabel('Required vCPU per instance')).toHaveValue('2');
  await expect(page.getByLabel('Required RAM per instance (GB)')).toHaveValue('8');

  await page.getByRole('button', { name: /1-Yr Reserved/i }).click();
  await page.getByLabel('Monthly cross-region transfer (GB)').fill('100');
  await page.getByLabel('Source region').fill('us-east');
  await page.getByLabel('Destination region').fill('us-west');

  await page.getByTestId('calculate-btn').click();

  const awsCard = page.locator('[data-testid="card-aws"]').first();
  await expect(awsCard).toBeVisible({ timeout: 15000 });
  await expect(awsCard).toContainText('m5.xlarge');
  await expect(awsCard).toContainText('1-Yr Reserved');
  await expect(awsCard).toContainText('network_cross_region');
  await expect(page.getByText('Network egress', { exact: true }).first()).toBeVisible();
  await page.getByRole('button', { name: 'Annual', exact: true }).click();
  await expect(page.getByText('Estimated annual cost').first()).toBeVisible();
});

test('database estimate uses cached API rate units', async ({ page }) => {
  await page.route('**/api/database/catalog?*', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        provider: 'aws',
        service: 'rds',
        region: 'us-east-1',
        updated_at: '2026-10-01T00:00:00Z',
        provider_status: { status: 'current' },
        rates: [{
          rate_id: 'rds-compute-hourly',
          component: 'compute',
          sku: 'db.t3.medium',
          unit: 'Hrs',
          unit_price: 0.068,
          currency: 'USD',
          source: 'AWS Price List',
          effective_date: '2026-10-01',
        }],
      }),
    });
  });

  await page.route('**/api/database/calculate', async (route) => {
    const request = route.request().postDataJSON();
    expect(request.line_items).toEqual([{ rate_id: 'rds-compute-hourly', quantity: 730 }]);
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        provider: 'aws',
        service: 'rds',
        region: 'us-east-1',
        currency: 'USD',
        total: 49.64,
        line_items: [{
          rate_id: 'rds-compute-hourly',
          component: 'compute',
          sku: 'db.t3.medium',
          quantity: 730,
          unit: 'Hrs',
          unit_price: 0.068,
          subtotal: 49.64,
          source: 'AWS Price List',
          effective_date: '2026-10-01',
        }],
        price_status: { status: 'current' },
        prices_updated_at: '2026-10-01T00:00:00Z',
      }),
    });
  });

  await page.goto('/');
  await page.getByRole('button', { name: 'Load prices' }).click();
  await expect(page.getByRole('button', { name: 'Add cost line' })).toBeVisible();
  await page.getByRole('button', { name: 'Add cost line' }).click();
  await page.getByLabel('Quantity for database line 1').fill('730');
  await page.getByRole('button', { name: 'Calculate database cost' }).click();

  const estimate = page.getByTestId('database-estimate-result');
  await expect(estimate).toBeVisible();
  await expect(estimate).toContainText('$49.64');
  await expect(estimate).toContainText('db.t3.medium');
});

test('database panel explains missing GCP catalog credentials', async ({ page }) => {
  await page.route('**/api/database/catalog?*', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        provider: 'gcp',
        service: 'cloud_sql',
        region: 'us-central1',
        provider_status: { status: 'unavailable', error: 'GOOGLE_CLOUD_BILLING_API_KEY is required' },
        rates: [],
        rate_count: 0,
      }),
    });
  });

  await page.goto('/');
  await page.getByLabel('Provider').selectOption('gcp');
  await page.getByRole('button', { name: 'Load prices' }).click();
  await expect(page.locator('p[role="alert"]')).toContainText('GOOGLE_CLOUD_BILLING_API_KEY');
});

test('SEO metadata and discovery routes are production-ready', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/InfraCostIQ/);
  await expect(page.locator('link[rel="canonical"]')).toHaveAttribute('href', 'https://www.infracostiq.com');
  await expect(page.locator('meta[property="og:image"]')).toHaveAttribute('content', /^https:\/\/www\.infracostiq\.com\/opengraph-image/);
  await expect(page.locator('meta[name="twitter:card"]')).toHaveAttribute('content', 'summary_large_image');

  const robots = await page.request.get('/robots.txt');
  expect(robots.ok()).toBeTruthy();
  expect(await robots.text()).toContain('https://www.infracostiq.com/sitemap.xml');

  const sitemap = await page.request.get('/sitemap.xml');
  expect(sitemap.ok()).toBeTruthy();
  expect(await sitemap.text()).toContain('https://www.infracostiq.com/');

  const indexNowKey = await page.request.get('/indexnow-key.txt');
  expect(indexNowKey.ok()).toBeTruthy();
  expect((await indexNowKey.text()).trim()).toMatch(/^[a-f0-9]{32}$/);
});
