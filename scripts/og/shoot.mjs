#!/usr/bin/env node
/*
 * scripts/og/shoot.mjs: render the site's 1200x630 share image, docs/assets/og.png, from docs/data/ledger.json.
 *
 *     node scripts/og/shoot.mjs              writes docs/assets/og.png
 *     node scripts/og/shoot.mjs out.png      writes somewhere else (to compare first)
 *
 * The card shows the Radiant (every milestone as a mark) and no counts, so it stays true as the ledger grows;
 * re-run it when the Radiant's look changes (CI may also run it on ledger changes).
 *
 * How: serves docs/ from a Node http server on a free 127.0.0.1 port, adds og.html (next to this script) at
 * /__og.html so it loads the site's own assets/f0.css, assets/f0.js, assets/radiant.js and data/ledger.json, and
 * screenshots it at 1200x630 in headless Chromium with motion off. The only outside requests allowed are Google
 * Fonts (the card is set in Geist and Newsreader); everything else is refused. It exits 1, writing nothing, if the
 * page throws, the ledger does not load, or the fonts do not load (a card in fallback fonts is worse than an old one).
 *
 * The PNG is then reduced to a 256-colour palette with Python's Pillow when it is installed (about 190 KB instead
 * of 500 KB; some chat apps skip large preview images); pass --full to keep the full-colour screenshot.
 *
 * Playwright and the browser are found as in scripts/prerender.mjs: PLAYWRIGHT_MODULE or `playwright`
 * (npm i --no-save playwright@1.56.1); PRERENDER_CHROMIUM=playwright for Playwright's own Chromium, or a path.
 */
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..', '..');
const DOCS = path.join(ROOT, 'docs');
const ARGS = process.argv.slice(2);
const FULL = ARGS.includes('--full');
const OUT = path.resolve(ARGS.filter((a) => !a.startsWith('--'))[0] || path.join(DOCS, 'assets', 'og.png'));
/* 256-colour palette with Floyd-Steinberg dithering; reads PNG bytes on stdin, writes the result to argv[1] */
const QUANTIZE = "import sys,io\nfrom PIL import Image\nim=Image.open(io.BytesIO(sys.stdin.buffer.read())).convert('RGB')\n" +
  "im.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.FLOYDSTEINBERG).save(sys.argv[1],optimize=True)";
const LOCAL_CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.svg': 'image/svg+xml', '.png': 'image/png', '.woff2': 'font/woff2' };

function serve() {
  const card = fs.readFileSync(path.join(HERE, 'og.html'));
  return http.createServer((req, res) => {
    const u = new URL(req.url, 'http://localhost');
    if (u.pathname === '/__og.html') { res.writeHead(200, { 'Content-Type': TYPES['.html'] }).end(card); return; }
    const file = path.join(DOCS, decodeURIComponent(u.pathname));
    if (!file.startsWith(DOCS + path.sep)) { res.writeHead(403).end(); return; }
    fs.readFile(file, (err, body) => {
      if (err) { res.writeHead(404).end('not found'); return; }
      res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-store' }).end(body);
    });
  });
}
async function loadPlaywright() {
  for (const t of [process.env.PLAYWRIGHT_MODULE, 'playwright', '/opt/node22/lib/node_modules/playwright/index.mjs'].filter(Boolean)) {
    try { return await import(path.isAbsolute(t) ? pathToFileURL(t).href : t); } catch { /* next */ }
  }
  throw new Error('Playwright not found: run `npm i --no-save playwright@1.56.1` (or set PLAYWRIGHT_MODULE)');
}
function launchOptions() {
  const v = process.env.PRERENDER_CHROMIUM;
  if (v === 'playwright' || v === 'default') return {};
  if (v) return { executablePath: v };
  return fs.existsSync(LOCAL_CHROME) ? { executablePath: LOCAL_CHROME } : {};
}

async function main() {
  const server = serve();
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  const origin = 'http://127.0.0.1:' + server.address().port;
  const { chromium } = await loadPlaywright();
  const browser = await chromium.launch(launchOptions());
  try {
    const ctx = await browser.newContext({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1, colorScheme: 'dark', reducedMotion: 'reduce' });
    await ctx.route('**/*', (route) => {
      const u = route.request().url();
      return u.startsWith(origin + '/') || /^https:\/\/fonts\.(googleapis|gstatic)\.com\//.test(u) ? route.continue() : route.abort('blockedbyclient');
    });
    const page = await ctx.newPage();
    const errs = [];
    page.on('pageerror', (e) => errs.push('uncaught ' + e.message));
    page.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
    await page.goto(origin + '/__og.html', { waitUntil: 'networkidle', timeout: 60000 });
    await page.waitForFunction(() => window.__ready === true || window.__error, null, { timeout: 30000 });
    const st = await page.evaluate(() => ({
      error: window.__error || null, count: window.__count,
      fonts: ['600 88px Geist', '500 15px "Geist Mono"', '400 31px Newsreader'].map((f) => [f, document.fonts.check(f)])
    }));
    if (st.error) throw new Error('ledger: ' + st.error);
    const missing = st.fonts.filter((f) => !f[1]).map((f) => f[0]);
    if (missing.length) throw new Error('fonts did not load (' + missing.join(', ') + '); is fonts.googleapis.com reachable?');
    if (errs.length) throw new Error(errs.join('; '));
    await page.waitForTimeout(400);
    const png = await page.screenshot({ type: 'png' });
    let how = 'full colour';
    const q = FULL ? null : spawnSync('python3', ['-I', '-c', QUANTIZE, OUT], { input: png });
    if (q && q.status === 0) how = '256-colour palette';
    else {
      if (q) console.warn('og: Pillow not available or failed; writing the full-colour PNG');
      fs.writeFileSync(OUT, png);
    }
    console.log(`${OUT}: 1200x630, ${st.count} milestones from docs/data/ledger.json, ${how}, ${fs.statSync(OUT).size} bytes`);
  } finally {
    await browser.close();
    server.close();
  }
}

main().catch((e) => { console.error('og:', e.message); process.exit(1); });
