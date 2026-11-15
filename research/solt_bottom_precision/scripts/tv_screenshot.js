const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1 });
  const fails = new Set();
  page.on('requestfailed', r => { try { fails.add(new URL(r.url()).host); } catch(e){} });
  const sym = process.argv[2] || 'BINANCE:SOLUSDT', itv = process.argv[3] || '30', out = process.argv[4] || 'charts/tv.png';
  await page.goto(`https://www.tradingview.com/chart/?symbol=${encodeURIComponent(sym)}&interval=${itv}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(15000);
  await page.screenshot({ path: out });
  console.log('title:', await page.title());
  console.log('failed hosts:', [...fails].join(', '));
  await browser.close();
})();
