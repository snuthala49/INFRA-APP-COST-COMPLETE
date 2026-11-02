import { readFile } from 'node:fs/promises';

const siteUrl = new URL(process.env.INDEXNOW_SITE_URL || 'https://www.infracostiq.com');
if (siteUrl.protocol !== 'https:') {
  throw new Error('INDEXNOW_SITE_URL must use HTTPS');
}

const key = (await readFile(new URL('../public/indexnow-key.txt', import.meta.url), 'utf8')).trim();
const submittedUrls = (process.env.INDEXNOW_URLS || `${siteUrl.origin}/`)
  .split(',')
  .map((url) => url.trim())
  .filter(Boolean);

if (!submittedUrls.length || submittedUrls.some((url) => new URL(url).host !== siteUrl.host)) {
  throw new Error('Submit at least one URL, and all URLs must belong to INDEXNOW_SITE_URL');
}

const response = await fetch('https://api.indexnow.org/indexnow', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json; charset=utf-8' },
  body: JSON.stringify({
    host: siteUrl.host,
    key,
    keyLocation: `${siteUrl.origin}/indexnow-key.txt`,
    urlList: submittedUrls,
  }),
});

if (![200, 202].includes(response.status)) {
  const details = await response.text();
  throw new Error(`IndexNow request failed (${response.status}): ${details}`);
}

console.log(`IndexNow accepted ${submittedUrls.length} URL(s) for ${siteUrl.host}.`);