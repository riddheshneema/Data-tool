const { chromium } = require('playwright');
(async () => {
  const [svg, png, w] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: +w, height: 800 }, deviceScaleFactor: 1 });
  await p.setContent(`<html><body style="margin:0"><img src="data:image/svg+xml;base64,${require('fs').readFileSync(svg).toString('base64')}" style="width:${w}px;display:block"></body></html>`);
  await p.waitForTimeout(300);
  await p.screenshot({ path: png, fullPage: true });
  await b.close();
})();
