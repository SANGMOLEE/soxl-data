const { chromium } = require('playwright');
// 트레이딩뷰 차트를 특정 날짜로 이동해 캡처
// 사용: node tv_goto.js SYMBOL INTERVAL YYYY-MM-DD HH:MM out.png
(async () => {
  const [sym, itv, date, time, out] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1500, height: 820 }, deviceScaleFactor: 1, timezoneId: 'UTC' });
  await page.goto(`https://www.tradingview.com/chart/?symbol=${encodeURIComponent(sym)}&interval=${itv}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(12000);
  await page.mouse.click(600, 400);
  await page.keyboard.press('Alt+KeyG');
  await page.waitForTimeout(2500);
  const inputs = await page.locator('[data-name="go-to-date-dialog"] input').all();
  console.log('inputs:', inputs.length);
  if (inputs.length >= 1) {
    await inputs[0].click({ clickCount: 3 });
    await inputs[0].fill(date);
    if (inputs.length >= 2 && time) {
      try { await inputs[1].click({ clickCount: 3, timeout: 2000 }); await inputs[1].fill(time, { timeout: 2000 }); } catch (e) { console.log('time input skipped'); }
    }
    await page.keyboard.press('Enter');
    const btn = page.locator('[data-name="go-to-date-dialog"] button[data-name="submit-button"]');
    if (await btn.count()) await btn.first().click();
  }
  await page.waitForTimeout(6000);
  // 안내 팝업 닫기
  for (let k = 0; k < 4; k++) {
    const got = page.getByRole('button', { name: /Got it/i });
    if (await got.count()) { await got.first().click().catch(() => {}); await page.waitForTimeout(500); }
  }
  await page.keyboard.press('Escape');
  await page.mouse.move(5, 5);
  await page.waitForTimeout(2000);
  await page.screenshot({ path: out });
  await browser.close();
})();
