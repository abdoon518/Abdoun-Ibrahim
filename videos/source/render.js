const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [,, html, outDir, mode] = process.argv;
(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await pg.goto('file://' + path.resolve(html));
  await pg.evaluate(() => document.fonts.ready);
  fs.mkdirSync(outDir, { recursive: true });
  const times = mode === 'stills' ? [1.5, 5.3, 6.5, 10.2, 13.0, 14.9] : Array.from({ length: 450 }, (_, i) => i / 30);
  for (let i = 0; i < times.length; i++) {
    await pg.evaluate(t => window.seek(t), times[i]);
    const name = mode === 'stills' ? `still_${times[i]}.png` : `f_${String(i).padStart(4, '0')}.png`;
    await pg.screenshot({ path: path.join(outDir, name) });
  }
  await b.close();
})();
