const { chromium } = require('playwright');
(async () => {
  const html = process.argv[2], pdf = process.argv[3], shots = process.argv[4];
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 794, height: 1123 } });
  await p.goto('file://' + html, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(500);
  await p.pdf({ path: pdf, printBackground: true, preferCSSPageSize: true });
  const pages = await p.$$('.page');
  for (let i = 0; i < pages.length; i++) {
    await pages[i].screenshot({ path: shots + '_p' + (i + 1) + '.png' });
  }
  await b.close();
  console.log('pages', pages.length);
})();
