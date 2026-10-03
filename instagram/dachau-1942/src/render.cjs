// Screenshots every slide of slides.html into slides/slide-NN.png.
// Run from the project folder: NODE_PATH=$(npm root -g) node src/render.cjs [story]
// "story" writes 1080x1920 Story versions into story/ instead.
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const root = path.resolve(__dirname, '..');
  const browser = await chromium.launch();
  const story = process.argv[2] === 'story';
  const outDir = story ? 'story' : 'slides';
  const page = await browser.newPage({ viewport: { width: 1080, height: story ? 1920 : 1350 } });
  page.on('pageerror', e => { console.error(e.message); process.exitCode = 1; });
  await page.goto('file://' + path.join(root, 'slides.html') + (story ? '#story' : ''));
  await page.waitForSelector('body[data-ready="1"]');
  const sizes = await page.$$eval('.fit, .psfit', els => els.map(e => [e.closest('.slide').id, e.dataset.fs]));
  console.log('font sizes:', sizes.map(s => s.join('=')).join(' '));
  const overflow = await page.$$eval('.fit, .psfit', els => els
    .filter(e => e.querySelector('.inner').offsetHeight > e.clientHeight)
    .map(e => e.closest('.slide').id));
  if (overflow.length) { console.error('overflowing:', overflow.join(' ')); process.exitCode = 1; }
  const slides = await page.$$('section.slide');
  for (const [i, s] of slides.entries()) {
    await s.screenshot({ path: path.join(root, outDir, `slide-${String(i + 1).padStart(2, '0')}.png`) });
  }
  console.log(`${slides.length} slides written`);
  await browser.close();
})();
