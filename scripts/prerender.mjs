#!/usr/bin/env node
/*
 * scripts/prerender.mjs: bake the no-JavaScript copy of every data-rendered part of the site into the HTML.
 *
 *     After changing docs/data (or a page script that renders from it), run:
 *         node scripts/prerender.mjs
 *     and commit the changed docs/**\/*.html with the data. CI does the same on main
 *     (.github/workflows/prerender.yml).
 *
 * Why. Pages draw their lists, cards and counts from docs/data/*.json in the browser. Each such part also
 * ships a static copy inside the HTML, so the page reads without JavaScript (and before the data arrives).
 * This script keeps every static copy identical to what the page's own JavaScript renders from the data,
 * so a number on the page never goes stale when the data changes.
 *
 * Markers. A static copy sits between two comments that are the ONLY content of the element the page
 * script writes into (its template, the element with its attributes, stays in the page itself):
 *
 *     <ol class="members" id="members-list"><!--prerender:members--> ...copy... <!--/prerender:members--></ol>
 *     <dd class="v" data-stat="count"><!--prerender:stat-count-->341<!--/prerender:stat-count--></dd>
 *
 * NAME is unique within its page and uses a-z, 0-9 and "-". Markers cannot nest, and do not work inside
 * <noscript>, <script>, <template> or attribute values (the browser does not see them as comments there).
 *
 * How it works:
 *   1. Find every docs/**\/*.html with markers and check them (paired, unique, not nested).
 *   2. Serve docs/ from a Node http server on a free 127.0.0.1 port. Pages with markers are served with the
 *      content between each marker pair emptied, so whatever appears there afterwards came from the script.
 *   3. Open each page as <page>?motion=off in headless Chromium (1440x900, light colour scheme). Every
 *      request that leaves that server is refused: raw.githubusercontent.com and api.github.com (the live
 *      kappa file and pull-request lookups) fall back to the repository's own files, fonts and other
 *      third parties cannot change the result, and the run needs no network.
 *   4. Wait until the page's scripts have rewritten every marked element, the network is idle, and the
 *      marked content has stopped changing.
 *   5. Copy each element's rendered innerHTML (canvas width, height and style removed) back between its
 *      markers, in place. When an element's children are all block-level (list items, cards, table rows)
 *      each child goes on its own line, indented, so diffs stay readable.
 * Running it twice gives identical files: the page sees the same emptied input both times.
 *
 * It writes nothing and exits 1 when a marker is malformed, a page throws or logs an error, a local file
 * is missing (404), or a marked element is never rewritten by its page script (its copy would otherwise
 * go stale without anyone noticing).
 *
 * Usage:
 *   node scripts/prerender.mjs                     every page under docs/ that has markers
 *   node scripts/prerender.mjs docs/ledger/index.html   only these pages
 *   node scripts/prerender.mjs --check             render and compare only; exit 1 if any file would change
 *
 * Needs Playwright (npm i --no-save playwright@1.56.1, or PLAYWRIGHT_MODULE=/path/to/playwright/index.mjs)
 * and a Chromium. PRERENDER_CHROMIUM=playwright uses Playwright's own download (npx playwright install
 * chromium; this is what CI sets); PRERENDER_CHROMIUM=/path/to/chrome uses that binary; unset, the script
 * uses /opt/pw-browsers/chromium-1194/chrome-linux/chrome when it exists, else Playwright's own.
 */
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DOCS = path.join(ROOT, 'docs');
const LOCAL_CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const VIEWPORT = { width: 1440, height: 900 };
const TIMEOUT = 30000; // ms per page, for each wait
const MARK = /<!--(\/?)prerender:([a-z0-9][a-z0-9-]*)-->/g;
const LOOSE = /<!--\s*\/?\s*prerender\s*:[^>]*-->/gi;
const TYPES = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8', '.svg': 'image/svg+xml',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif',
  '.ico': 'image/x-icon', '.woff2': 'font/woff2', '.woff': 'font/woff', '.txt': 'text/plain; charset=utf-8',
  '.csv': 'text/csv; charset=utf-8', '.pdf': 'application/pdf', '.xml': 'application/xml'
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const relOf = (file) => path.relative(DOCS, file).split(path.sep).join('/');

/* ---------- markers in the source ---------- */
function parseMarkers(src, rel) {
  const regions = [], seen = new Set();
  let cur = null, m;
  MARK.lastIndex = 0;
  while ((m = MARK.exec(src))) {
    const [all, slash, name] = m;
    if (!slash) {
      if (cur) throw new Error(`${rel}: <!--prerender:${name}--> opens inside "${cur.name}" (markers cannot nest)`);
      if (seen.has(name)) throw new Error(`${rel}: marker name "${name}" is used twice`);
      seen.add(name);
      cur = { name, open: m.index, from: m.index + all.length };
    } else {
      if (!cur || cur.name !== name) throw new Error(`${rel}: <!--/prerender:${name}--> has no matching <!--prerender:${name}-->`);
      cur.to = m.index;
      const ls = src.lastIndexOf('\n', cur.open - 1) + 1;
      cur.indent = /^[ \t]*/.exec(src.slice(ls, cur.open))[0];
      regions.push(cur);
      cur = null;
    }
  }
  if (cur) throw new Error(`${rel}: <!--prerender:${cur.name}--> is never closed`);
  const loose = (src.match(LOOSE) || []).length;
  if (loose !== regions.length * 2) throw new Error(`${rel}: a prerender marker is malformed (write <!--prerender:name--> and <!--/prerender:name-->, name in a-z 0-9 -)`);
  return regions;
}
function blank(src, regions) {
  let out = '', i = 0;
  for (const r of regions) { out += src.slice(i, r.from); i = r.to; }
  return out + src.slice(i);
}
function fill(src, regions, parts) {
  let out = '', i = 0;
  for (const r of regions) {
    const p = parts[r.name];
    const body = p.lines ? '\n' + p.lines.map((l) => r.indent + '  ' + l).join('\n') + '\n' + r.indent : p.html;
    out += src.slice(i, r.from) + body;
    i = r.to;
  }
  return out + src.slice(i);
}
function htmlFiles(dir) {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true }).sort((a, b) => (a.name < b.name ? -1 : 1))) {
    const f = path.join(dir, e.name);
    if (e.isDirectory()) out.push(...htmlFiles(f));
    else if (e.name.endsWith('.html')) out.push(f);
  }
  return out;
}

/* ---------- the local server: docs/ as GitHub Pages serves it, marked regions emptied ---------- */
function serve(emptied) {
  return http.createServer((req, res) => {
    const u = new URL(req.url, 'http://localhost');
    let file;
    try { file = path.join(DOCS, decodeURIComponent(u.pathname)); } catch { res.writeHead(400).end(); return; }
    if (file !== DOCS && !file.startsWith(DOCS + path.sep)) { res.writeHead(403).end(); return; }
    let st = null;
    try { st = fs.statSync(file); } catch { /* missing */ }
    if (st && st.isDirectory()) {
      if (!u.pathname.endsWith('/')) { res.writeHead(301, { Location: u.pathname + '/' + u.search }).end(); return; }
      file = path.join(file, 'index.html');
    }
    const key = relOf(file);
    let body;
    if (emptied.has(key)) body = Buffer.from(emptied.get(key), 'utf8');
    else {
      try { body = fs.readFileSync(file); } catch { res.writeHead(404, { 'Content-Type': 'text/plain' }).end('not found'); return; }
    }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(file).toLowerCase()] || 'application/octet-stream', 'Cache-Control': 'no-store' });
    res.end(body);
  });
}

/* ---------- runs inside each page, before its own scripts ---------- */
function inPage() {
  const R = { found: null, error: null };
  function scan() {
    const found = [], errs = [], open = [];
    const w = document.createTreeWalker(document.documentElement, NodeFilter.SHOW_COMMENT);
    for (let n = w.nextNode(); n; n = w.nextNode()) {
      const m = /^(\/?)prerender:([a-z0-9][a-z0-9-]*)$/.exec(n.data);
      if (!m) continue;
      if (!m[1]) { open.push({ name: m[2], start: n }); continue; }
      const o = open.pop();
      if (!o || o.name !== m[2]) { errs.push('unmatched <!--/prerender:' + m[2] + '-->'); continue; }
      const el = o.start.parentNode;
      if (!el || el.nodeType !== 1 || n.parentNode !== el) { errs.push(m[2] + ': both markers must be children of one element'); continue; }
      const label = '<' + el.localName + (el.id ? ' id="' + el.id + '"' : '') + '>';
      const stray = [].slice.call(el.childNodes).filter(function (k) { return k !== o.start && k !== n && !(k.nodeType === 3 && !k.data.trim()); });
      if (stray.length) { errs.push(m[2] + ': the markers must be the only content of ' + label + ' (move the other content outside it)'); continue; }
      found.push({ name: m[2], start: o.start, el: el, id: el.id || '' });
    }
    if (open.length) errs.push('unclosed marker(s): ' + open.map(function (o) { return o.name; }).join(', '));
    R.found = found;
    R.error = errs.length ? errs.join('; ') : null;
  }
  document.addEventListener('readystatechange', function () { if (document.readyState === 'interactive' && !R.found) scan(); });
  function holder(f) { return f.el.isConnected ? f.el : (f.id && document.getElementById(f.id)) || null; }
  function cleaned(node) {
    const c = node.cloneNode(true);
    if (c.nodeType === 1) {
      [c].concat([].slice.call(c.querySelectorAll('canvas'))).forEach(function (cv) {
        if (cv.localName !== 'canvas') return;
        cv.removeAttribute('width'); cv.removeAttribute('height'); cv.removeAttribute('style');
      });
    }
    return c;
  }
  const BLOCK = /^(block|list-item|flex|grid|table|table-row|table-row-group|table-header-group|table-footer-group|table-caption|none)$/;
  Object.defineProperty(window, '__f0prerender', {
    value: {
      state: function () {
        if (!R.found) return { ready: false };
        return { ready: true, error: R.error, names: R.found.map(function (f) { return f.name; }), pending: R.found.filter(function (f) { return f.start.isConnected; }).map(function (f) { return f.name; }) };
      },
      snapshot: function () {
        return (R.found || []).map(function (f) { const h = holder(f); return h ? h.innerHTML : '(detached)'; }).join('\u0001');
      },
      extract: function () {
        const out = {};
        R.found.forEach(function (f) {
          const el = holder(f);
          if (!el) { out[f.name] = { error: 'its element was replaced by the page script and has no id to find it again' }; return; }
          const kids = [].slice.call(el.childNodes).filter(function (k) { return !(k.nodeType === 3 && !k.data.trim()); });
          const flexy = /(^|-)(flex|grid)$/.test(getComputedStyle(el).display);
          const blocky = kids.length > 1 && kids.every(function (k) { return k.nodeType === 1 && (flexy || BLOCK.test(getComputedStyle(k).display)); });
          if (blocky) { out[f.name] = { lines: kids.map(function (k) { return cleaned(k).outerHTML; }) }; return; }
          const box = el.cloneNode(false);
          [].slice.call(el.childNodes).forEach(function (k) { box.appendChild(cleaned(k)); });
          out[f.name] = { html: box.innerHTML };
        });
        return out;
      }
    }
  });
}

/* ---------- one page ---------- */
async function render(browser, origin, pg) {
  const ctx = await browser.newContext({ viewport: VIEWPORT, colorScheme: 'light', reducedMotion: 'reduce', serviceWorkers: 'block' });
  const problems = [];
  try {
    await ctx.route('**/*', (route) => (route.request().url().startsWith(origin + '/') ? route.continue() : route.abort('blockedbyclient')));
    const page = await ctx.newPage();
    page.on('pageerror', (e) => problems.push('uncaught ' + (e && e.message)));
    page.on('console', (m) => { if (m.type() === 'error' && !/^Failed to load resource/.test(m.text())) problems.push('console.error: ' + m.text()); });
    page.on('response', (r) => { if (r.url().startsWith(origin + '/') && r.status() >= 400) problems.push(r.status() + ' for ' + r.url().slice(origin.length)); });
    await page.addInitScript(inPage);
    await page.goto(origin + '/' + pg.rel + '?motion=off', { waitUntil: 'load', timeout: TIMEOUT });

    const t0 = Date.now();
    let s;
    for (;;) {
      s = await page.evaluate(() => window.__f0prerender && window.__f0prerender.state());
      if (problems.length) throw new Error(problems.join('; '));
      if (s && s.ready) {
        if (s.error) throw new Error(s.error);
        const missing = pg.regions.map((r) => r.name).filter((n) => !s.names.includes(n));
        if (missing.length) throw new Error('markers not seen as comments in the parsed page (inside <noscript>, <script>, <template> or an attribute?): ' + missing.join(', '));
        if (!s.pending.length) break;
      }
      if (Date.now() - t0 > TIMEOUT) throw new Error(s && s.ready ? 'never rewritten by the page script: ' + s.pending.join(', ') : 'the page never finished parsing');
      await sleep(100);
    }
    await page.waitForLoadState('networkidle', { timeout: TIMEOUT }).catch(() => {});
    let last = null, same = 0;
    const t1 = Date.now();
    while (same < 3) {
      await sleep(250);
      const snap = await page.evaluate(() => window.__f0prerender.snapshot());
      if (snap === last) same++; else { same = 0; last = snap; }
      if (Date.now() - t1 > TIMEOUT) throw new Error('the marked content never stopped changing');
    }
    if (problems.length) throw new Error(problems.join('; '));
    const parts = await page.evaluate(() => window.__f0prerender.extract());
    for (const r of pg.regions) {
      const p = parts[r.name];
      if (!p) throw new Error(r.name + ': nothing extracted');
      if (p.error) throw new Error(r.name + ': ' + p.error);
      const text = p.lines ? p.lines.join('\n') : p.html;
      if (/<!--\/?prerender:/.test(text)) throw new Error(r.name + ': the rendered content contains prerender markers');
    }
    return parts;
  } finally {
    await ctx.close();
  }
}

async function loadPlaywright() {
  const tries = [process.env.PLAYWRIGHT_MODULE, 'playwright', '/opt/node22/lib/node_modules/playwright/index.mjs'].filter(Boolean);
  for (const t of tries) {
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
  const args = process.argv.slice(2);
  const check = args.includes('--check');
  const named = args.filter((a) => !a.startsWith('--')).map((a) => path.resolve(a));
  const files = named.length ? named : htmlFiles(DOCS);
  const pages = [];
  for (const file of files) {
    const rel = relOf(file);
    if (rel.startsWith('..')) throw new Error(`${file} is not inside docs/`);
    const src = fs.readFileSync(file, 'utf8');
    const regions = parseMarkers(src, rel);
    if (regions.length) pages.push({ file, rel, src, regions });
  }
  if (!pages.length) { console.log('prerender: no page has <!--prerender:...--> markers'); return; }

  const server = serve(new Map(pages.map((p) => [p.rel, blank(p.src, p.regions)])));
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const origin = 'http://127.0.0.1:' + server.address().port;
  const { chromium } = await loadPlaywright();
  const browser = await chromium.launch(launchOptions());
  const done = [];
  let failed = 0;
  try {
    for (const pg of pages) {
      try { done.push({ pg, parts: await render(browser, origin, pg) }); }
      catch (e) { failed++; console.error(`FAIL ${pg.rel}: ${e.message}`); }
    }
  } finally {
    await browser.close();
    server.close();
  }
  if (failed) { console.error(`prerender: ${failed} page(s) failed; no file written`); process.exit(1); }

  let changed = 0;
  for (const { pg, parts } of done) {
    const out = fill(pg.src, pg.regions, parts);
    const n = pg.regions.length + ' marked part' + (pg.regions.length === 1 ? '' : 's');
    if (out === pg.src) { console.log(`unchanged     docs/${pg.rel} (${n})`); continue; }
    changed++;
    if (check) console.log(`would change  docs/${pg.rel} (${n})`);
    else { fs.writeFileSync(pg.file, out); console.log(`updated       docs/${pg.rel} (${n})`); }
  }
  console.log(`prerender: ${done.length} page(s), ${changed} ${check ? 'out of date' : 'updated'}`);
  if (check && changed) process.exit(1);
}

main().catch((e) => { console.error('prerender:', e.message); process.exit(1); });
