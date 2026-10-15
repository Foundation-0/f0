/* Foundation0 · Writing page.
   1. The essay index: theme filter + search with a live count, rendered from data/writing.json
      and writing/annotations.json (our notes). The HTML ships a pre-rendered copy for no-JS readers.
   2. The theses map: essays -> themes -> pages on this site; hover, focus or pin a node to trace it.
      Roving tabindex, arrow keys, Enter to pin, Escape to clear. A list twin sits under it.
   3. Claims with a date: Subtractive Fragility's seven predictions on a 2026-2036 track, today marked.
   Colours come from tokens (CSS); nothing here animates on its own. */
(function () {
  'use strict';
  var F0 = window.F0;
  var esc = F0.esc;
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return [].slice.call((r || document).querySelectorAll(s)); }
  function slug(url) { return String(url).replace(/\/+$/, '').split('/').pop().replace(/\.html$/, ''); }
  function shortDate(s) { var p = s.split('-'); return (+p[2]) + ' ' + MON[+p[1] - 1]; }
  function plural(n, one, many) { return n + ' ' + (n === 1 ? one : (many || one + 's')); }

  /* ---------- 0. shape and shadow (Mahler, family 087): computed here, no data file ---------- */
  function gammaFn(z) { /* Lanczos, g = 7 */
    if (z < 0.5) return Math.PI / (Math.sin(Math.PI * z) * gammaFn(1 - z));
    z -= 1;
    var c = [0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313, -176.61502916214059, 12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7];
    var x = c[0]; for (var i = 1; i < 9; i++) x += c[i] / (z + i);
    var t = z + 7.5; return Math.sqrt(2 * Math.PI) * Math.pow(t, z + 0.5) * Math.exp(-t) * x;
  }
  function pArea(p) { return p === Infinity ? 4 : 4 * Math.pow(gammaFn(1 + 1 / p), 2) / gammaFn(1 + 2 / p); }
  function dual(p) { return p === 1 ? Infinity : p === Infinity ? 1 : p / (p - 1); }
  function pName(p) { return p === Infinity ? '∞' : (Math.round(p * 100) / 100).toString(); }
  function shapeAndShadow() {
    var host = $('#mh-stage'), read = $('#mh-read'), scale = $('#mh-scale'), range = $('#mh-p'), out = $('#mh-out'), triBtn = $('#mh-tri');
    if (!host) return;
    var NS = 'http://www.w3.org/2000/svg', p = 1, tri = false, svg = null, lw = 0;
    function mk(tag, a, parent) { var e = document.createElementNS(NS, tag); for (var k in a) e.setAttribute(k, a[k]); if (parent) parent.appendChild(e); return e; }
    function tOf(p) { return p === Infinity ? 100 : Math.min(99.5, 100 * Math.log2(p) / 6.5); }
    function pOf(t) { return t >= 100 ? Infinity : Math.pow(2, 6.5 * t / 100); }
    function boundary(p) {
      var pts = [];
      if (p === Infinity) return [[1, 1], [-1, 1], [-1, -1], [1, -1]];
      for (var i = 0; i < 240; i++) { var th = i / 240 * Math.PI * 2, c = Math.cos(th), s = Math.sin(th); pts.push([Math.sign(c) * Math.pow(Math.abs(c), 2 / p), Math.sign(s) * Math.pow(Math.abs(s), 2 / p)]); }
      return pts;
    }
    function triangle(r, up) { var pts = []; for (var k = 0; k < 3; k++) { var a = (up ? 90 : -90) + k * 120; pts.push([r * Math.cos(a * Math.PI / 180), r * Math.sin(a * Math.PI / 180)]); } return pts; }
    function state() {
      if (tri) { var A = 3 * Math.sqrt(3) / 2; return { K: triangle(Math.SQRT2, true), P: triangle(Math.SQRT2, false), a: A, b: A, label: 'an equilateral triangle, centred at its balance point' }; }
      var q = dual(p);
      return { K: boundary(p), P: boundary(q), a: pArea(p), b: pArea(q), label: 'p = ' + pName(p) + ', its polar is the q-shape with q = ' + pName(q) };
    }
    function draw() {
      var W = Math.round(host.getBoundingClientRect().width); if (!W) return; lw = W;
      var S = state(), size = Math.min(W, 420), R = 1.55, c = size / 2, k = (size / 2 - 10) / R;
      if (svg) svg.remove();
      svg = mk('svg', { viewBox: '0 0 ' + size + ' ' + size, width: size, height: size, role: 'img', 'aria-label': 'The shape ' + S.label + ' (gold) and its polar (cyan). Areas ' + S.a.toFixed(3) + ' and ' + S.b.toFixed(3) + '; product ' + (S.a * S.b).toFixed(3) + '.' }, host);
      [-1, 0, 1].forEach(function (v) {
        mk('line', { x1: c + v * k, x2: c + v * k, y1: 6, y2: size - 6, style: 'stroke:var(--grid)', 'stroke-width': v ? 1 : 1.2 }, svg);
        mk('line', { y1: c + v * k, y2: c + v * k, x1: 6, x2: size - 6, style: 'stroke:var(--grid)', 'stroke-width': v ? 1 : 1.2 }, svg);
      });
      function poly(pts, col, op) {
        var d = pts.map(function (q, i) { return (i ? 'L' : 'M') + (c + q[0] * k).toFixed(1) + ' ' + (c - q[1] * k).toFixed(1); }).join('') + 'Z';
        mk('path', { d: d, style: 'fill:' + col + ';fill-opacity:' + op + ';stroke:' + col, 'stroke-width': 2, 'stroke-linejoin': 'round' }, svg);
      }
      poly(S.P, 'var(--mark-dig)', 0.12); poly(S.K, 'var(--mark-bio)', 0.2);
      var t1 = mk('text', { x: c + 1 * k + 4, y: c - 6, 'font-size': 11, style: 'fill:var(--ink-3);font-family:var(--f-mono)' }, svg); t1.textContent = '1';
      var t2 = mk('text', { x: c + 4, y: c - 1 * k - 4, 'font-size': 11, style: 'fill:var(--ink-3);font-family:var(--f-mono)' }, svg); t2.textContent = '1';
    }
    function drawScale() {
      var W = Math.max(220, Math.round(scale.getBoundingClientRect().width)), H = 74, x0 = 10, x1 = W - 10, lo = 6.5, hi = 10.1;
      var X = function (v) { return x0 + (v - lo) / (hi - lo) * (x1 - x0); };
      var S = state(), prod = S.a * S.b;
      scale.innerHTML = '';
      var s = mk('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, 'aria-hidden': 'true' }, scale);
      mk('line', { x1: x0, x2: x1, y1: 30, y2: 30, style: 'stroke:var(--line-ui)', 'stroke-width': 1 }, s);
      [[27 / 4, '6.75', 'any shape'], [8, '8', 'symmetric'], [Math.PI * Math.PI, 'π²', 'circle']].forEach(function (m, i) {
        mk('line', { x1: X(m[0]), x2: X(m[0]), y1: 22, y2: 38, style: 'stroke:var(--ink-3)', 'stroke-width': 1 }, s);
        var a = mk('text', { x: X(m[0]), y: 52, 'text-anchor': i === 2 ? 'end' : i === 0 ? 'start' : 'middle', 'font-size': 11, style: 'fill:var(--ink-2);font-family:var(--f-mono)' }, s); a.textContent = m[1];
        var b = mk('text', { x: X(m[0]), y: 66, 'text-anchor': i === 2 ? 'end' : i === 0 ? 'start' : 'middle', 'font-size': 11, style: 'fill:var(--ink-3);font-family:var(--f-mono)' }, s); b.textContent = m[2];
      });
      mk('circle', { cx: X(prod), cy: 30, r: 6, style: 'fill:var(--ink);stroke:var(--bg-1)', 'stroke-width': 2 }, s);
      var lab = mk('text', { x: Math.max(x0 + 40, Math.min(x1 - 40, X(prod))), y: 14, 'text-anchor': 'middle', 'font-size': 11, 'font-weight': 600, style: 'fill:var(--ink);font-family:var(--f-mono)' }, s); lab.textContent = prod.toFixed(3);
    }
    function readout() {
      var S = state(), prod = S.a * S.b, note;
      if (tri) note = 'Exactly 27/4: the floor for any shape, reached by the triangle. It sits below 8 because a triangle is not symmetric.';
      else if (Math.abs(prod - 8) < 0.0005) note = 'Exactly 8: as small as a symmetric shape can go (' + (p === 1 ? 'a diamond and a square' : 'a square and a diamond') + ').';
      else if (Math.abs(p - 2) < 0.001) note = 'π² = 9.870: the circle, its own polar, gives the largest product of all.';
      else note = (prod - 8).toFixed(3) + ' above the floor of 8. Rounder shapes give more.';
      read.innerHTML = '<dl class="mh-dl"><div><dt><i class="k bio"></i>Area <span class="mh-v">K</span></dt><dd>' + S.a.toFixed(3) + '</dd></div><div><dt><i class="k dig"></i>Area <span class="mh-v">K°</span></dt><dd>' + S.b.toFixed(3) + '</dd></div><div class="prod"><dt>Product</dt><dd>' + prod.toFixed(3) + '</dd></div></dl><p class="mh-note">' + esc(note) + '</p>';
      out.textContent = tri ? '–' : pName(p);
      range.setAttribute('aria-valuetext', tri ? 'not used: triangle shown' : 'p = ' + pName(p) + ', product ' + prod.toFixed(3));
      $$('#mh-stops button').forEach(function (b) { var v = b.getAttribute('data-p') === 'Infinity' ? Infinity : +b.getAttribute('data-p'); b.setAttribute('aria-pressed', !tri && Math.abs(tOf(v) - tOf(p)) < 0.01 ? 'true' : 'false'); });
      triBtn.setAttribute('aria-pressed', tri ? 'true' : 'false');
    }
    function update() { draw(); drawScale(); readout(); }
    range.addEventListener('input', function () { tri = false; p = pOf(+range.value); if (Math.abs(p - Math.round(p)) < 0.03) p = Math.round(p); update(); });
    $$('#mh-stops button').forEach(function (b) { b.addEventListener('click', function () { tri = false; var v = b.getAttribute('data-p'); p = v === 'Infinity' ? Infinity : +v; range.value = tOf(p); update(); }); });
    triBtn.addEventListener('click', function () { tri = !tri; update(); });
    if ('ResizeObserver' in window) new ResizeObserver(function () { var w = Math.round(host.getBoundingClientRect().width); if (w && w !== lw) { draw(); drawScale(); } }).observe(host);
    var tb = $('#mh-table tbody');
    if (tb) tb.innerHTML = [1, 1.5, 2, 3, 4, 8, Infinity].map(function (v) { var a = pArea(v), b = pArea(dual(v)); return '<tr><th scope="row">p = ' + pName(v) + (v === 1 ? ' (diamond)' : v === 2 ? ' (circle)' : v === Infinity ? ' (square)' : '') + '</th><td class="n">' + a.toFixed(4) + '</td><td class="n">' + b.toFixed(4) + '</td><td class="n">' + (a * b).toFixed(4) + '</td></tr>'; }).join('') +
      '<tr><th scope="row">Equilateral triangle, at its centre</th><td class="n">' + (3 * Math.sqrt(3) / 2).toFixed(4) + '</td><td class="n">' + (3 * Math.sqrt(3) / 2).toFixed(4) + '</td><td class="n">6.7500</td></tr>';
    update();
  }
  shapeAndShadow();

  Promise.all([F0.json(F0.root + 'data/writing.json'), F0.json('annotations.json')])
    .then(function (r) { init(r[0], r[1]); })
    .catch(function (e) { console.error(e); });

  function init(W, A) {
    var posts = W.posts.slice().map(function (p, i) { p._i = i; p._a = A.essays[p.url] || {}; p._s = slug(p.url); return p; });
    posts.sort(function (a, b) { return a.date < b.date ? 1 : a.date > b.date ? -1 : a._i - b._i; });
    var TL = A.theme_labels || {};
    var themeOrder = (A.theme_order || []).slice();
    Object.keys(W.themes).forEach(function (k) { if (themeOrder.indexOf(k) < 0) themeOrder.push(k); });
    function tLabel(k) { return TL[k] || k.replace(/-/g, ' ').replace(/^./, function (c) { return c.toUpperCase(); }); }

    header(W, posts);
    var list = essayList(W, posts, themeOrder, tLabel);
    thesesMap(W, A, posts, themeOrder, tLabel, list);
    predictions(A.predictions);
  }

  /* ---------- hero numbers ---------- */
  function header(W, posts) {
    var dates = posts.map(function (p) { return p.date; }).sort();
    var a = dates[0], b = dates[dates.length - 1];
    var span = shortDate(a) + ' – ' + F0.fmtDate(b);
    $$('[data-wr="count"]').forEach(function (el) { el.textContent = posts.length; });
    $$('[data-wr="span"]').forEach(function (el) { el.textContent = span; });
    $$('[data-wr="stamp"]').forEach(function (el) { el.textContent = 'Writing updated ' + W.updated + ' · ' + plural(posts.length, 'essay'); });
  }

  /* ---------- 1. the essay index ---------- */
  function hl(text, words) {
    text = String(text == null ? '' : text);
    if (!words.length) return esc(text);
    var re = new RegExp('(' + words.map(function (w) { return w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }).join('|') + ')', 'gi');
    return text.split(re).map(function (part, i) { return i % 2 ? '<mark>' + esc(part) + '</mark>' : esc(part); }).join('');
  }

  function essayHTML(p, themeOrder, tLabel, words) {
    var a = p._a, feat = p._s === 'math-faster';
    return '<li class="essay' + (feat ? ' is-feat' : '') + '" id="e-' + esc(p._s) + '" data-themes="' + esc(p.themes.join(' ')) + '">' +
      '<div class="e-meta"><time datetime="' + esc(p.date) + '">' + esc(F0.fmtDate(p.date)) + '</time><span class="e-cat">' + esc(p.category) + '</span>' +
      '</div>' +
      '<div class="e-body">' +
      '<p class="e-type"><span>' + esc(a.type || 'Essay') + '</span>' + (feat ? '<span class="e-feat">Featured</span>' : '') + '</p>' +
      '<h3 class="e-title"><a href="' + esc(p.url) + '">' + hl(p.title, words) + '</a></h3>' +
      '<p class="e-sum">' + hl(p.summary, words) + '</p>' +
      '<p class="e-why"><b>Why it matters here</b>' + hl(a.why || p.relevance, words) + '</p>' +
      '<div class="e-foot"><ul class="e-tags" aria-label="Themes">' + p.themes.map(function (k) { return '<li>' + esc(tLabel(k)) + '</li>'; }).join('') + '</ul>' +
      (a.status ? '<span class="e-status">' + hl(a.status, words) + '</span>' : '') + '</div>' +
      '</div></li>';
  }

  function essayList(W, posts, themeOrder, tLabel) {
    var ol = $('#essay-list'), seg = $('#theme-seg'), q = $('#wr-q'), count = $('#wr-count'), desc = $('#theme-desc'), empty = $('#wr-empty');
    var state = { theme: 'all', words: [] };

    /* theme buttons, counted from the data */
    var counts = {};
    posts.forEach(function (p) { p.themes.forEach(function (k) { counts[k] = (counts[k] || 0) + 1; }); });
    seg.innerHTML = '<button type="button" data-theme-k="all" aria-pressed="true">All <span class="n">' + posts.length + '</span></button>' +
      themeOrder.filter(function (k) { return counts[k]; }).map(function (k) {
        return '<button type="button" data-theme-k="' + esc(k) + '" aria-pressed="false" title="' + esc(W.themes[k] || '') + '">' + esc(tLabel(k)) + ' <span class="n">' + counts[k] + '</span></button>';
      }).join('');

    function hay(p) { return [p.title, p.summary, p.category, p._a.why || p.relevance, p._a.type, p._a.status, p.themes.map(tLabel).join(' ')].join(' ').toLowerCase(); }
    posts.forEach(function (p) { p._hay = hay(p); });

    function render() {
      var shown = 0;
      ol.innerHTML = posts.map(function (p) {
        var ok = (state.theme === 'all' || p.themes.indexOf(state.theme) >= 0) && state.words.every(function (w) { return p._hay.indexOf(w) >= 0; });
        if (ok) shown++;
        return ok ? essayHTML(p, themeOrder, tLabel, state.words) : '';
      }).join('');
      empty.hidden = shown > 0;
      var bits = [];
      if (state.theme !== 'all') bits.push('theme ' + tLabel(state.theme));
      if (state.words.length) bits.push('matching “' + state.words.join(' ') + '”');
      count.textContent = (shown === posts.length && !bits.length ? 'Showing all ' + posts.length + ' essays.' : 'Showing ' + shown + ' of ' + posts.length + ' essays' + (bits.length ? ', ' + bits.join(', ') : '') + '.');
      desc.textContent = state.theme === 'all' ? '' : (W.themes[state.theme] || '') + '.';
      $$('button', seg).forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-theme-k') === state.theme ? 'true' : 'false'); });
    }
    function setTheme(k) { state.theme = k; render(); }
    function setQuery(s) { state.words = String(s || '').toLowerCase().split(/\s+/).filter(Boolean); render(); }

    seg.addEventListener('click', function (e) { var b = e.target.closest('button'); if (b) setTheme(b.getAttribute('data-theme-k')); });
    var t = 0;
    q.addEventListener('input', function () { clearTimeout(t); t = setTimeout(function () { setQuery(q.value); }, 90); });
    q.addEventListener('keydown', function (e) { if (e.key === 'Escape' && q.value) { q.value = ''; setQuery(''); } });
    $('#wr-clear').addEventListener('click', function () { q.value = ''; state.words = []; setTheme('all'); q.focus(); });
    render();
    return { setTheme: function (k) { q.value = ''; state.words = []; setTheme(k); } };
  }

  /* ---------- 2. the theses map ---------- */
  function thesesMap(W, A, posts, themeOrder, tLabel, list) {
    var host = $('#tmap'), svg = $('#tmap-edges'), panel = $('#tmap-panel');
    if (!host) return;
    var byUrl = {}; posts.forEach(function (p) { byUrl[p.url] = p; });
    var order = (A.map_order || []).filter(function (u) { return byUrl[u]; });
    posts.forEach(function (p) { if (order.indexOf(p.url) < 0) order.push(p.url); });
    var pages = A.pages || [];
    var pageBy = {}; pages.forEach(function (g) { pageBy[g.key] = g; });
    var themes = themeOrder.filter(function (k) { return posts.some(function (p) { return p.themes.indexOf(k) >= 0; }); });

    /* nodes: id = 'e:slug' | 't:key' | 'p:key' */
    var nodes = [], N = {};
    function add(n) { nodes.push(n); N[n.id] = n; n.adjE = []; return n; }
    order.forEach(function (u) { var p = byUrl[u]; add({ id: 'e:' + p._s, col: 0, kind: 'essay', post: p, label: p._a.short || p.title }); });
    themes.forEach(function (k) { add({ id: 't:' + k, col: 1, kind: 'theme', key: k, label: tLabel(k) }); });
    pages.forEach(function (g) { add({ id: 'p:' + g.key, col: 2, kind: 'page', page: g, label: g.label }); });

    /* edges */
    var edges = [], E = {};
    function edge(a, b, cls) { var id = a + '>' + b; if (!E[id] && N[a] && N[b]) { E[id] = { id: id, a: a, b: b, cls: cls }; edges.push(E[id]); } return E[id]; }
    order.forEach(function (u) {
      var p = byUrl[u], e = 'e:' + p._s;
      p.themes.forEach(function (k) { edge(e, 't:' + k, 'ea'); });
      (p._a.paths || []).forEach(function (tp) { edge('t:' + tp[0], 'p:' + tp[1], 'eb'); });
    });

    /* what lights up for each node */
    function reach(id) {
      var n = N[id], on = {}, ed = {};
      on[id] = 1;
      function lit(a, b) { var x = E[a + '>' + b]; if (x) { ed[x.id] = 1; on[a] = 1; on[b] = 1; } }
      if (n.kind === 'essay') {
        n.post.themes.forEach(function (k) { lit(id, 't:' + k); });
        (n.post._a.paths || []).forEach(function (tp) { lit('t:' + tp[0], 'p:' + tp[1]); });
      } else if (n.kind === 'theme') {
        edges.forEach(function (x) { if (x.b === id || x.a === id) lit(x.a, x.b); });
      } else {
        order.forEach(function (u) {
          var p = byUrl[u];
          (p._a.paths || []).forEach(function (tp) { if ('p:' + tp[1] === id) { lit('e:' + p._s, 't:' + tp[0]); lit('t:' + tp[0], id); } });
        });
      }
      return { on: on, ed: ed };
    }

    /* render node buttons */
    var cols = [$('#tmap-c0'), $('#tmap-c1'), $('#tmap-c2')];
    nodes.forEach(function (n) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'nd nd-' + n.kind; b.setAttribute('data-id', n.id); b.tabIndex = -1;
      b.setAttribute('aria-pressed', 'false');
      if (n.kind === 'essay') {
        b.innerHTML = '<span class="nd-d">' + esc(shortDate(n.post.date)) + '</span><span class="nd-t">' + esc(n.label) + '</span><span class="port r"></span>';
        b.setAttribute('aria-label', n.label + ', essay, ' + F0.fmtDate(n.post.date) + '. Serves ' + n.post.themes.map(tLabel).join(' and ') + '.');
      } else if (n.kind === 'theme') {
        var c = posts.filter(function (p) { return p.themes.indexOf(n.key) >= 0; }).length;
        b.innerHTML = '<span class="port l"></span><span class="nd-t">' + esc(n.label) + '</span><span class="nd-n">' + plural(c, 'essay') + '</span><span class="port r"></span>';
        b.setAttribute('aria-label', n.label + ', theme, ' + plural(c, 'essay') + '.');
      } else {
        b.innerHTML = '<span class="port l"></span><span class="nd-t">' + esc(n.label) + '</span><span class="nd-n">' + esc(n.page.path) + '</span>';
        b.setAttribute('aria-label', n.label + ', page on this site.');
      }
      b.setAttribute('aria-describedby', 'tmap-how');
      cols[n.col].appendChild(b);
      n.el = b;
    });

    /* edges as SVG paths, laid out from the buttons' boxes */
    var NS = 'http://www.w3.org/2000/svg';
    edges.forEach(function (x) { var p = document.createElementNS(NS, 'path'); p.setAttribute('class', 'edge ' + x.cls); svg.appendChild(p); x.el = p; });
    function layout() {
      var box = host.getBoundingClientRect();
      if (!box.width) return;
      svg.setAttribute('width', box.width); svg.setAttribute('height', box.height);
      svg.setAttribute('viewBox', '0 0 ' + box.width + ' ' + box.height);
      var pt = {};
      nodes.forEach(function (n) {
        var r = n.el.getBoundingClientRect();
        pt[n.id] = { l: r.left - box.left, r: r.right - box.left, y: r.top - box.top + r.height / 2 };
      });
      edges.forEach(function (x) {
        var a = pt[x.a], b = pt[x.b], x1 = a.r, x2 = b.l, dx = Math.max(12, (x2 - x1) * 0.55);
        x.el.setAttribute('d', 'M' + x1.toFixed(1) + ' ' + a.y.toFixed(1) + 'C' + (x1 + dx).toFixed(1) + ' ' + a.y.toFixed(1) + ' ' + (x2 - dx).toFixed(1) + ' ' + b.y.toFixed(1) + ' ' + x2.toFixed(1) + ' ' + b.y.toFixed(1));
      });
    }
    if ('ResizeObserver' in window) new ResizeObserver(layout).observe(host); else window.addEventListener('resize', layout);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(layout);

    /* highlight + panel */
    var pinned = 'e:math-faster', shown = null, panelFor = undefined;
    function show(id) {
      shown = id;
      var R = id ? reach(id) : null;
      host.classList.toggle('has-active', !!R);
      nodes.forEach(function (n) {
        n.el.classList.toggle('on', !!(R && R.on[n.id]));
        n.el.classList.toggle('dim', !!(R && !R.on[n.id]));
        n.el.classList.toggle('cur', n.id === id);
        n.el.setAttribute('aria-pressed', n.id === pinned ? 'true' : 'false');
      });
      edges.forEach(function (x) { x.el.classList.toggle('on', !!(R && R.ed[x.id])); });
      if (panelFor === id) return; /* same node: keep the panel's DOM, so a click inside it still lands */
      panelFor = id;
      panel.innerHTML = id ? panelHTML(N[id], R) : '<p class="tp-empty">Select an essay, a theme or a page to trace its links.</p>';
    }
    function link(path, text) { return '<a href="../' + esc(path) + '">' + esc(text) + '</a>'; }
    function panelHTML(n, R) {
      var h = '';
      if (n.kind === 'essay') {
        var p = n.post, a = p._a;
        var pathsByPage = {};
        (a.paths || []).forEach(function (tp) { (pathsByPage[tp[1]] = pathsByPage[tp[1]] || []).push(tLabel(tp[0])); });
        h += '<p class="tp-k">Essay &middot; ' + esc(F0.fmtDate(p.date)) + ' &middot; ' + esc(a.type || 'Essay') + '</p>';
        h += '<h3 class="tp-t"><a href="' + esc(p.url) + '">' + esc(p.title) + '</a></h3>';
        h += '<p class="tp-p">' + esc(a.why || p.relevance) + '</p>';
        h += '<p class="tp-h">Serves</p><ul class="tp-chips">' + p.themes.map(function (k) { return '<li><button type="button" data-go="t:' + esc(k) + '">' + esc(tLabel(k)) + '</button></li>'; }).join('') + '</ul>';
        var keys = Object.keys(pathsByPage);
        h += '<p class="tp-h">Leads to</p>' + (keys.length ? '<ul class="tp-links">' + keys.map(function (k) { var g = pageBy[k]; return '<li>' + link(g.path, g.label) + '<span>via ' + esc(pathsByPage[k].join(', ')) + '</span></li>'; }).join('') + '</ul>'
          : '<p class="tp-p tp-none">No page on this site: a dated snapshot, kept for the record.</p>');
      } else if (n.kind === 'theme') {
        var es = posts.filter(function (p) { return p.themes.indexOf(n.key) >= 0; });
        var ps = pages.filter(function (g) { return R.on['p:' + g.key]; });
        h += '<p class="tp-k">Theme &middot; ' + plural(es.length, 'essay') + '</p>';
        h += '<h3 class="tp-t">' + esc(n.label) + '</h3>';
        h += '<p class="tp-p">' + esc(W.themes[n.key] || '') + '.</p>';
        h += '<p class="tp-h">Essays</p><ul class="tp-links">' + es.map(function (p) { return '<li><a href="' + esc(p.url) + '">' + esc(p.title) + '</a><span>' + esc(F0.fmtDate(p.date)) + '</span></li>'; }).join('') + '</ul>';
        h += '<p class="tp-h">Becomes work on</p>' + (ps.length ? '<ul class="tp-links">' + ps.map(function (g) { return '<li>' + link(g.path, g.label) + '</li>'; }).join('') + '</ul>' : '<p class="tp-p tp-none">No page on this site. Market analysis is dated and kept for the record.</p>');
        h += '<button class="tbtn tp-go" type="button" data-filter="' + esc(n.key) + '">Show these essays in the list</button>';
      } else {
        var g = n.page;
        var from = posts.filter(function (p) { return R.on['e:' + p._s]; });
        h += '<p class="tp-k">Page on this site</p>';
        h += '<h3 class="tp-t">' + link(g.path, g.label) + '</h3>';
        h += '<p class="tp-p">' + esc(g.what) + '</p>';
        h += '<p class="tp-h">Reached from</p><ul class="tp-links">' + from.map(function (p) {
          var via = (p._a.paths || []).filter(function (tp) { return tp[1] === g.key; }).map(function (tp) { return tLabel(tp[0]); });
          return '<li><a href="' + esc(p.url) + '">' + esc(p.title) + '</a><span>via ' + esc(via.join(', ')) + '</span></li>';
        }).join('') + '</ul>';
      }
      return h;
    }

    /* roving focus + keys */
    var cur = N[pinned] || nodes[0];
    function rove(n, focus) {
      nodes.forEach(function (m) { m.el.tabIndex = -1; });
      n.el.tabIndex = 0; cur = n;
      if (focus) n.el.focus();
    }
    rove(cur, false);
    function colNodes(c) { return nodes.filter(function (m) { return m.col === c; }); }
    function across(n, dir) {
      var c = n.col + dir; if (c < 0 || c > 2) return null;
      var cand = colNodes(c), R = reach(n.id);
      var linked = cand.filter(function (m) { return R.on[m.id]; });
      var pool = linked.length ? linked : cand;
      var y = n.el.getBoundingClientRect().top;
      pool.sort(function (a, b) { return Math.abs(a.el.getBoundingClientRect().top - y) - Math.abs(b.el.getBoundingClientRect().top - y); });
      return pool[0];
    }
    host.addEventListener('keydown', function (e) {
      var b = e.target.closest('.nd'); if (!b) return;
      var n = N[b.getAttribute('data-id')], list = colNodes(n.col), i = list.indexOf(n), next = null;
      if (e.key === 'ArrowDown') next = list[Math.min(list.length - 1, i + 1)];
      else if (e.key === 'ArrowUp') next = list[Math.max(0, i - 1)];
      else if (e.key === 'ArrowRight') next = across(n, 1);
      else if (e.key === 'ArrowLeft') next = across(n, -1);
      else if (e.key === 'Home') next = list[0];
      else if (e.key === 'End') next = list[list.length - 1];
      else if (e.key === 'Escape') { pinned = null; show(n.id); e.preventDefault(); return; }
      if (next) { e.preventDefault(); rove(next, true); }
    });
    host.addEventListener('focusin', function (e) { var b = e.target.closest('.nd'); if (b) { rove(N[b.getAttribute('data-id')], false); show(b.getAttribute('data-id')); } });
    host.addEventListener('focusout', function (e) { if (!host.contains(e.relatedTarget)) show(pinned); });
    host.addEventListener('click', function (e) {
      var b = e.target.closest('.nd'); if (!b) return;
      var id = b.getAttribute('data-id');
      pinned = pinned === id ? null : id;
      rove(N[id], false); show(id);
    });
    host.addEventListener('pointerover', function (e) { var b = e.target.closest('.nd'); if (b && e.pointerType !== 'touch') show(b.getAttribute('data-id')); });
    host.addEventListener('pointerleave', function (e) { if (e.pointerType !== 'touch' && !host.contains(document.activeElement)) show(pinned); });
    panel.addEventListener('click', function (e) {
      var go = e.target.closest('[data-go]');
      if (go) { var id = go.getAttribute('data-go'); pinned = id; rove(N[id], true); show(id); return; }
      var f = e.target.closest('[data-filter]');
      if (f) { list.setTheme(f.getAttribute('data-filter')); var sec = $('#essays'); if (sec) sec.scrollIntoView({ block: 'start' }); var btn = $('#theme-seg button[aria-pressed="true"]'); if (btn) btn.focus({ preventScroll: true }); }
    });

    layout();
    show(pinned);

    /* narrow screens: the map becomes a list, theme -> essays -> pages (CSS swaps it in below 600px) */
    var narrow = document.createElement('div');
    narrow.className = 'tmap-list'; narrow.id = 'tmap-list';
    narrow.innerHTML = '<ol class="tl-themes">' + themes.map(function (k) {
      var es = posts.filter(function (p) { return p.themes.indexOf(k) >= 0; });
      var R = reach('t:' + k), ps = pages.filter(function (g) { return R.on['p:' + g.key]; });
      return '<li class="tl-theme"><p class="tl-h"><span class="tl-t">' + esc(tLabel(k)) + '</span><span class="tl-n">' + plural(es.length, 'essay') + '</span></p>' +
        '<p class="tl-d">' + esc(W.themes[k] || '') + '.</p>' +
        '<ul class="tl-es">' + es.map(function (p) { return '<li><a href="' + esc(p.url) + '">' + esc(p._a.short || p.title) + '</a><span>' + esc(shortDate(p.date)) + '</span></li>'; }).join('') + '</ul>' +
        '<p class="tl-k">Becomes work on</p>' + (ps.length ? '<ul class="tl-ps">' + ps.map(function (g) { return '<li>' + link(g.path, g.label) + '</li>'; }).join('') + '</ul>' : '<p class="tl-none">No page on this site: dated analysis, kept for the record.</p>') +
        '</li>';
    }).join('') + '</ol>';
    host.parentNode.parentNode.insertBefore(narrow, host.parentNode.nextSibling);

    /* list twin */
    var twin = $('#map .twin .table-wrap');
    if (twin) {
      twin.innerHTML = '<table class="tbl"><caption>Every link in the map</caption><thead><tr><th scope="col">Essay</th><th scope="col">Themes it serves</th><th scope="col">Pages on this site, and why</th></tr></thead><tbody>' +
        order.map(function (u) {
          var p = byUrl[u];
          var pg = (p._a.paths || []).map(function (tp) { var g = pageBy[tp[1]]; return link(g.path, g.label) + ' (via ' + esc(tLabel(tp[0])) + ')'; });
          return '<tr><th scope="row"><a href="' + esc(p.url) + '">' + esc(p.title) + '</a></th><td>' + esc(p.themes.map(tLabel).join(', ')) + '</td><td>' + (pg.length ? pg.join('<br>') : 'None: a dated snapshot') + '</td></tr>';
        }).join('') + '</tbody></table>';
    }
  }

  /* ---------- 3. claims with a date ---------- */
  function predictions(P) {
    var rowsEl = $('#pv-rows'), axis = $('#pv-axis'), panel = $('#pv-panel');
    if (!P || !rowsEl) return;
    var Y0 = 2026, Y1 = 2036;
    function dec(s) { var p = s.split('-').map(Number); return p.length === 3 ? F0.decYear(s) : p[0] + p[1] / 12; } /* a target month is scored at its end */
    function pct(y) { return Math.max(0, Math.min(100, (y - Y0) / (Y1 - Y0) * 100)); }
    var now = new Date(), todayS = now.toISOString().slice(0, 10), today = F0.decYear(todayS);
    var start = dec(P.published);

    /* axis: one tick per year */
    var ticks = '';
    for (var y = Y0; y <= Y1; y += 1) ticks += '<span class="pv-tick' + (y % 2 ? ' odd' : '') + '" style="left:' + pct(y) + '%"><i>' + y + '</i></span>';
    /* today's label: two short lines beside the line, so it never runs across the year columns */
    axis.innerHTML = '<span class="pv-al"></span><span class="pv-at">' + ticks + '<span class="pv-now-l" style="left:' + pct(today) + '%"><b>Today</b>' + esc(F0.fmtDate(todayS)) + '</span></span>';

    function left(it) {
      var m = Math.round((dec(it.target) - today) * 12);
      if (m <= 0) return 'due now';
      var yr = Math.floor(m / 12), mo = m % 12;
      return 'in ' + (yr ? plural(yr, 'year') : '') + (yr && mo ? ' ' : '') + (mo ? plural(mo, 'month') : '');
    }
    rowsEl.innerHTML = P.items.map(function (it, i) {
      var a = pct(start), b = pct(dec(it.target)), t = pct(today);
      return '<li><button type="button" class="pv-row' + (it.thesis ? ' thesis' : '') + '" data-i="' + i + '" aria-pressed="' + (i === 0) + '">' +
        '<span class="pv-l"><span class="pv-n">' + it.n + '</span><span class="pv-c">' + esc(it.claim) + '</span>' + (it.thesis ? '<span class="pv-th">Thesis</span>' : '') + '</span>' +
        '<span class="pv-track" aria-hidden="true"><span class="pv-seg" style="left:' + a + '%;width:' + (b - a) + '%"></span><span class="pv-done" style="left:' + a + '%;width:' + Math.max(0, Math.min(b, t) - a) + '%"></span><span class="pv-now" style="left:' + t + '%"></span><span class="pv-ring" style="left:' + b + '%"></span><span class="pv-date' + (b > 88 ? ' end' : '') + '" style="left:' + b + '%">' + esc(it.label) + '</span></span>' +
        '<span class="sr-only">Scored ' + esc(it.label) + ', ' + left(it) + '. Status: pending.</span>' +
        '</button></li>';
    }).join('');

    var rows = $$('.pv-row', rowsEl), sel = 0;
    function pick(i, focus) {
      sel = i;
      rows.forEach(function (r, j) { r.setAttribute('aria-pressed', j === i ? 'true' : 'false'); r.tabIndex = j === i ? 0 : -1; });
      if (focus) rows[i].focus();
      var it = P.items[i];
      panel.innerHTML =
        '<p class="tp-k">Prediction ' + it.n + ' &middot; Movement ' + esc(it.movement) + (it.thesis ? ' &middot; <span class="pv-thk">carries the thesis</span>' : '') + '</p>' +
        '<p class="pv-when"><span class="v">' + esc(it.label) + '</span><span class="k">scored ' + left(it) + '</span></p>' +
        '<p class="pv-status"><span class="badge sealed">Pending &middot; not yet scored</span><span class="badge n">Confidence: ' + esc(it.confidence) + '</span></p>' +
        '<p class="tp-p pv-claim">' + esc(it.claim) + '</p>' +
        '<dl class="kv pv-kv"><dt>Fails if</dt><dd>' + esc(it.fails) + '</dd><dt>Started from</dt><dd>' + esc(it.baseline) + '</dd></dl>' +
        '<p class="pv-src"><a href="' + esc(P.essay) + '">The essay&rsquo;s tracker</a> &middot; confidence and status are its own</p>';
    }
    rowsEl.addEventListener('click', function (e) { var b = e.target.closest('.pv-row'); if (b) pick(+b.getAttribute('data-i'), false); });
    rowsEl.addEventListener('keydown', function (e) {
      var k = e.key, i = sel;
      if (k === 'ArrowDown') i = Math.min(rows.length - 1, sel + 1); else if (k === 'ArrowUp') i = Math.max(0, sel - 1);
      else if (k === 'Home') i = 0; else if (k === 'End') i = rows.length - 1; else return;
      e.preventDefault(); pick(i, true);
    });
    pick(0, false);

    var first = P.items.slice().sort(function (a, b) { return dec(a.target) - dec(b.target); })[0];
    var nx = $('#pv-next');
    if (nx) nx.textContent = 'Next to be scored: no. ' + first.n + ', ' + first.label + ', ' + left(first) + '. The two that carry the thesis, 5 and 7, are scored in 2032 and 2035.';

    var twin = $('#dated .twin .table-wrap');
    if (twin) twin.innerHTML = '<table class="tbl"><caption>The seven predictions, as of ' + esc(F0.fmtDate(P.checked)) + '</caption><thead><tr><th scope="col" class="n">No.</th><th scope="col">Scored</th><th scope="col">Claim</th><th scope="col">Fails if</th><th scope="col">Started from</th><th scope="col">Confidence</th><th scope="col">Status</th></tr></thead><tbody>' +
      P.items.map(function (it) { return '<tr><td class="n">' + it.n + '</td><td>' + esc(it.label) + '</td><td>' + esc(it.claim) + (it.thesis ? ' <b>(thesis)</b>' : '') + '</td><td>' + esc(it.fails) + '</td><td>' + esc(it.baseline) + '</td><td>' + esc(it.confidence) + '</td><td>Pending</td></tr>'; }).join('') +
      '</tbody></table>';
  }
})();
