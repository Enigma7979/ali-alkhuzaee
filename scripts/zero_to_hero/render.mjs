// Render a book HTML file to PDF (tagged, with bookmarks) and optional per-page PNGs, and report overflow.
import { createRequire } from 'module';
// node render.mjs BOOK.html OUT.pdf [PNG_DIR] [SCALE]
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const [, , html, pdf, pngDir, scale = '1.5'] = process.argv;
const browser = await chromium.launch();
const page = await browser.newPage({ deviceScaleFactor: Number(scale) });
await page.goto('file://' + html, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(300);
// Overflow: any element whose box escapes its page frame, or a frame whose content is taller than the frame.
const report = await page.evaluate(() => {
  const out = [];
  document.querySelectorAll('.page').forEach((pg, i) => {
    const pr = pg.getBoundingClientRect();
    const fr = pg.querySelector(':scope>.frame');
    if (fr && fr.scrollHeight > fr.clientHeight + 1) out.push({ page: i + 1, issue: 'frame overflow', by: fr.scrollHeight - fr.clientHeight });
    pg.querySelectorAll('.frame *').forEach(el => {
      const r = el.getBoundingClientRect();
      if (!r.width || !r.height) return;
      const f = fr.getBoundingClientRect();
      if (r.bottom > f.bottom + 1.5 || r.left < f.left - 1.5 || r.right > f.right + 1.5) out.push({ page: i + 1, issue: 'escapes frame', el: el.tagName + '.' + el.className, text: (el.textContent || '').trim().slice(0, 40) });
    });
  });
  const fonts = [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight);
  return { overflow: out.slice(0, 60), pages: document.querySelectorAll('.page').length, fonts: [...new Set(fonts)] };
});
if (pdf !== '-') await page.pdf({ path: pdf, preferCSSPageSize: true, printBackground: true, outline: true, tagged: true });
if (pngDir) {
  const pages = await page.$$('.page');
  for (let i = 0; i < pages.length; i++) await pages[i].screenshot({ path: `${pngDir}/p${String(i + 1).padStart(2, '0')}.png` });
}
console.log(JSON.stringify(report));
await browser.close();
