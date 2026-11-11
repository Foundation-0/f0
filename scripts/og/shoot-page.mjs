#!/usr/bin/env node
/*
 * scripts/og/shoot-page.mjs: render a 1200x630 section share card from scripts/og/cards/*.html.
 *
 *     node scripts/og/shoot-page.mjs commons
 *     node scripts/og/shoot-page.mjs instruments
 *     node scripts/og/shoot-page.mjs commons /tmp/out.png   optional output path
 *
 * Serves docs/ for site CSS and scripts/og/ for the card HTML/CSS, then screenshots at 1200x630
 * in headless Chromium (same Playwright setup as shoot.mjs). Pass --full to skip PNG quantisation.
 */
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..', '..');
const DOCS = path.join(ROOT, 'docs');
const CARDS = path.join(HERE, 'cards');
const PAGES = {
  commons: { html: 'commons.html', out: path.join(DOCS, 'assets', 'og-commons.png') },
  instruments: { html: 'instruments.html', out: path.join(DOCS, 'assets', 'og-instruments.png') },
};
const ARGS = process.argv.slice(2);
const FULL = ARGS.includes('--full');
const positional = ARGS.filter((a) => !a.startsWith('--'));
const PAGE = positional[0];
const SPEC = PAGES[PAGE];
if (!SPEC) {
  console.error('Usage: node scripts/og/shoot-page.mjs <commons|instruments> [out.png] [--full]');
  process.exit(1);
}
const OUT = path.resolve(positional[1] || SPEC.out);
const QUANTIZE = "import sys,io\nfrom PIL import Image\nim=Image.open(io.BytesIO(sys.stdin.buffer.read())).convert('RGB')\n" +
  "im.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.FLOYDSTEINBERG).save(sys.argv[1],optimize=True)";
const LOCAL_CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.svg': 'image/svg+xml', '.png': 'image/png', '.woff2': 'font/woff2' };

function serve() {
  return http.createServer((req, res) => {
    const u = new URL(req.url, 'http://localhost');
    if (u.pathname === '/__og/page-card.css') {
      res.writeHead(200, { 'Content-Type': TYPES['.css'] }).end(fs.readFileSync(path.join(HERE, 'page-card.css')));
      return;
    }
    if (u.pathname === '/__card.html') {
      res.writeHead(200, { 'Content-Type': TYPES['.html'] }).end(fs.readFileSync(path.join(CARDS, SPEC.html)));
      return;
    }
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
    await page.goto(origin + '/__card.html', { waitUntil: 'networkidle', timeout: 60000 });
    await page.waitForFunction(() => window.__ready === true || window.__error, null, { timeout: 30000 });
    const st = await page.evaluate(() => ({
      error: window.__error || null,
      fonts: ['600 38px Geist', '400 17px Newsreader', '500 13px "Geist Mono"', '500 11px "Geist Mono"'].map((f) => [f, document.fonts.check(f)]),
    }));
    if (st.error) throw new Error(st.error);
    const missing = st.fonts.filter((f) => !f[1]).map((f) => f[0]);
    if (missing.length) throw new Error('fonts did not load (' + missing.join(', ') + ')');
    if (errs.length) throw new Error(errs.join('; '));
    await page.waitForTimeout(400);
    const png = await page.screenshot({ type: 'png' });
    let how = 'full colour';
    const q = FULL ? null : spawnSync('python3', ['-c', QUANTIZE, OUT], { input: png });
    if (q && q.status === 0) how = '256-colour palette';
    else {
      if (q) console.warn('shoot-page: Pillow not available or failed; writing full-colour PNG');
      fs.writeFileSync(OUT, png);
    }
    console.log(`${OUT}: 1200x630, page ${PAGE}, ${how}, ${fs.statSync(OUT).size} bytes`);
  } finally {
    await browser.close();
    server.close();
  }
}

main().catch((e) => { console.error('shoot-page:', e.message); process.exit(1); });
