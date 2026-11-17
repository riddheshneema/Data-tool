const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const b = await chromium.launch();
  for (const j of jobs) {
    const t = fs.readFileSync(j.svg, 'utf8');
    const m = t.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/);
    const w = Math.round(+m[1]), h = Math.round(+m[2]);
    const scale = Math.min(2400 / w, 2400 / h, 2.5);
    const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: scale });
    await p.goto('file://' + j.svg);
    await p.waitForTimeout(300);
    await p.screenshot({ path: j.png });
    await p.close();
  }
  await b.close(); console.log('rendered', jobs.length);
})();
