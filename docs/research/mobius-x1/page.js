/* mobius-x1 page (research/mobius-x1): seven figures, all computed in the browser.
   Pascal mod 2 (hero), the transform grid + Yates' butterfly, the eight-row gadget, the parity ring,
   the crossover chart, the best-gadget-size chart and the h = 11 overlap histogram.
   Vanilla JS. Colours come from tokens (CSS classes on SVG; F0.css on canvas, redrawn on F0.onTheme).
   Formulas re-computed from Swapnil Jain's mobius-x1 (Apache-2.0); this file is new code. */
(function () {
  'use strict';
  var F0 = window.F0, D = document, NS = 'http://www.w3.org/2000/svg';
  if (!F0) return;
  function $(s, r) { return (r || D).querySelector(s); }
  function $$(s, r) { return [].slice.call((r || D).querySelectorAll(s)); }
  function el(tag, attrs, parent, text) {
    var e = D.createElementNS(NS, tag);
    if (attrs) for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    if (parent) parent.appendChild(e);
    return e;
  }
  function fmt(n) { return Number(n).toLocaleString('en-US'); }
  var SUP = { '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹', '-': '⁻' };
  function supU(n) { return String(n).split('').map(function (c) { return SUP[c] || c; }).join(''); }
  /* scientific notation: html (with <sup>) or unicode text */
  function sci(x, sig, html) {
    if (x === 0) return '0';
    var e = Math.floor(Math.log10(Math.abs(x))), m = x / Math.pow(10, e);
    var ms = m.toFixed(sig == null ? 2 : sig);
    if (+ms >= 10) { e += 1; ms = (m / 10).toFixed(sig == null ? 2 : sig); }
    if (e === 0) return ms;
    return ms + ' × 10' + (html ? '<sup>' + String(e).replace('-', '−') + '</sup>' : supU(e));
  }
  function pow10txt(e, html) { if (e === 0) return '1'; if (e === 1) return '10'; return '10' + (html ? '<sup>' + String(e).replace('-', '−') + '</sup>' : supU(e)); }
  function setPressed(group, attr, val) { $$('button', group).forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute(attr) === String(val))); }); }
  function tipAt(html, node) { var r = node.getBoundingClientRect(); F0.tip.show(html, r.left + r.width / 2, r.top + r.height / 2); }
  function fitSvg(svg, draw) {
    var st = svg.parentNode, last = '';
    function go() {
      var r = st.getBoundingClientRect(), w = Math.max(200, Math.round(r.width)), h = Math.max(120, Math.round(r.height));
      var key = w + 'x' + h; if (key === last) return; last = key;
      svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h); draw(w, h);
    }
    if ('ResizeObserver' in window) new ResizeObserver(go).observe(st); else window.addEventListener('resize', go);
    go();
    return function () { last = ''; go(); };
  }
  var LET = 'abcdef';
  function subsetName(i) { if (!i) return '∅'; var s = ''; for (var b = 0; b < 6; b++) if (i >> b & 1) s += LET[b]; return s; }
  function subsetLong(i) { return i ? subsetName(i) : 'none (∅)'; }
  /* tiny seeded generator so the first frame is the same on every load */
  function rng(seed) { var s = seed >>> 0; return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
  function binomBig(n, r) { if (r < 0 || r > n) return 0n; var a = 1n; for (var i = 0; i < r; i++) a = a * BigInt(n - i) / BigInt(i + 1); return a; }
  function binom(n, r) { if (r < 0 || r > n) return 0; var a = 1; for (var i = 0; i < r; i++) a = a * (n - i) / (i + 1); return Math.round(a); }

  /* =========================================================================
     HERO: Pascal's triangle, odd entries lit
     ========================================================================= */
  (function pascal() {
    var cv = $('#px-cv'); if (!cv) return;
    var C = F0.canvas(cv), ctx = C.ctx;
    var rows = 64, shown = 64, cur = null, hov = null, playing = false, visible = true;
    var out = $('#px-out'), cap = $('#px-cap'), playBtn = $('#px-play'), seg = $('#px-rows');
    function geom() {
      var w = C.w, h = C.h, padX = 14, padY = 34;
      var cs = Math.min((w - 2 * padX) / rows, (h - padY - 18) / (rows * 0.866));
      var ch = cs * 0.866, top = padY + Math.max(0, (h - padY - 18 - rows * ch) / 2);
      return { cs: cs, ch: ch, top: top, cx: w / 2 };
    }
    function cellXY(g, n, r) { return { x: g.cx + (r - n / 2) * g.cs, y: g.top + n * g.ch + g.ch / 2 }; }
    function draw() {
      var g = geom(), mk = F0.css('--mk'), grid = F0.css('--grid'), ink = F0.css('--ink');
      ctx.clearRect(0, 0, C.w, C.h);
      var lim = Math.min(rows, Math.ceil(shown));
      var rad = g.cs * 0.44;
      for (var n = 0; n < lim; n++) {
        for (var r = 0; r <= n; r++) {
          var p = cellXY(g, n, r);
          if ((r & n) === r) {
            ctx.fillStyle = mk;
            if (g.cs >= 7) { ctx.beginPath(); ctx.arc(p.x, p.y, rad, 0, 6.2832); ctx.fill(); }
            else ctx.fillRect(p.x - g.cs * 0.46, p.y - g.ch * 0.5, g.cs * 0.92, g.ch * 0.96);
          } else if (g.cs >= 4) {
            ctx.fillStyle = grid; ctx.beginPath(); ctx.arc(p.x, p.y, Math.max(0.8, g.cs * 0.09), 0, 6.2832); ctx.fill();
          }
        }
      }
      var m = hov || cur;
      if (m && m.n < lim) {
        var q = cellXY(g, m.n, m.r);
        ctx.strokeStyle = ink; ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.arc(q.x, q.y, Math.max(4, g.cs * 0.62), 0, 6.2832); ctx.stroke();
      }
      out.textContent = lim < rows ? 'row ' + (lim - 1) + ' of ' + rows : (m ? 'row ' + m.n + ' · r ' + m.r : rows + ' rows');
    }
    function bin(x, w) { var s = x.toString(2); while (s.length < w) s = '0' + s; return s; }
    function describe(m, html) {
      var v = binomBig(m.n, m.r), odd = (m.r & m.n) === m.r, w = Math.max(1, m.n.toString(2).length);
      var vs = v.toString(); if (vs.length > 15) vs = vs.slice(0, 4) + '…' + ' (' + vs.length + ' digits)';
      if (html) {
        return '<div class="tip-k">Row ' + m.n + ', position ' + m.r + '</div><div class="tip-t">C(' + m.n + ', ' + m.r + ') = ' + F0.esc(vs) + '</div>' +
          '<div class="tip-rows"><div class="tip-row">r = ' + bin(m.r, w) + '</div><div class="tip-row">n = ' + bin(m.n, w) + '</div></div>' +
          '<div class="tip-note">' + (odd ? 'Odd: every 1 in r sits under a 1 in n.' : 'Even: some 1 in r has a 0 above it in n.') + '</div>';
      }
      return 'Row ' + m.n + ', position ' + m.r + ': C(' + m.n + ', ' + m.r + ') = ' + vs + ', ' + (odd ? 'odd' : 'even') + '. In binary r = ' + bin(m.r, w) + ' and n = ' + bin(m.n, w) + (odd ? ': every 1 in r sits under a 1 in n.' : ': some 1 in r has a 0 above it.');
    }
    function pick(ev) {
      var b = cv.getBoundingClientRect(), x = ev.clientX - b.left, y = ev.clientY - b.top, g = geom();
      var n = Math.floor((y - g.top) / g.ch); if (n < 0 || n >= Math.min(rows, Math.ceil(shown))) return null;
      var r = Math.round((x - g.cx) / g.cs + n / 2); if (r < 0 || r > n) return null;
      return { n: n, r: r };
    }
    cv.addEventListener('pointermove', function (ev) {
      var m = pick(ev); hov = m; draw();
      if (m) F0.tip.show(describe(m, true), ev.clientX, ev.clientY); else F0.tip.hide();
    });
    cv.addEventListener('pointerleave', function () { hov = null; F0.tip.hide(); draw(); });
    function showCur() {
      draw(); cap.textContent = describe(cur, false);
      var g = geom(), p = cellXY(g, cur.n, cur.r), b = cv.getBoundingClientRect();
      F0.tip.show(describe(cur, true), b.left + p.x, b.top + p.y);
    }
    cv.addEventListener('focus', function () { if (!cur) cur = { n: Math.min(rows - 1, 13), r: 5 }; showCur(); });
    cv.addEventListener('blur', function () { F0.tip.hide(); cur = null; draw(); });
    cv.addEventListener('keydown', function (e) {
      if (!cur) return;
      var k = e.key, n = cur.n, r = cur.r;
      if (k === 'ArrowUp') n = Math.max(0, n - 1); else if (k === 'ArrowDown') n = Math.min(rows - 1, n + 1);
      else if (k === 'ArrowLeft') r = r - 1; else if (k === 'ArrowRight') r = r + 1;
      else if (k === 'Home') r = 0; else if (k === 'End') r = n; else return;
      e.preventDefault(); r = Math.max(0, Math.min(n, r)); cur = { n: n, r: r }; showCur();
    });
    seg.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      rows = +b.getAttribute('data-rows'); shown = rows; stop(); setPressed(seg, 'data-rows', rows); cur = null;
      cv.setAttribute('aria-label', "Pascal's triangle with " + rows + ' rows, odd entries lit. The lit cells form the Sierpinski triangle: three half-size copies of the whole, around an empty middle.');
      cap.textContent = 'Each doubling of the rows repeats the picture three times around a hole: the Sierpinski triangle.';
      draw();
    });
    var loop = F0.loop(function () {
      shown = Math.min(rows, shown + Math.max(0.25, rows / 110));
      draw();
      if (shown >= rows) stop();
    });
    function stop() { playing = false; loop.stop(); playBtn.setAttribute('aria-pressed', 'false'); }
    playBtn.addEventListener('click', function () {
      if (!F0.motion()) { /* motion off: step by doubling, a still frame each time */
        shown = shown >= rows ? 1 : Math.min(rows, Math.max(2, shown * 2));
        cap.textContent = Math.round(shown) + (Math.round(shown) === 1 ? ' row' : ' rows') + ' shown. Press again to double.'; draw(); return;
      }
      if (playing) { stop(); return; }
      if (shown >= rows) shown = 1;
      playing = true; playBtn.setAttribute('aria-pressed', 'true'); if (visible) loop.start();
    });
    F0.whenVisible(cv, function () { visible = true; if (playing) loop.start(); }, function () { visible = false; loop.stop(); });
    F0.onMotion(function (on) { if (!on && playing) { stop(); shown = rows; draw(); } });
    C.resize(draw); F0.onTheme(draw); draw();
  })();

  /* =========================================================================
     FIGURE A: the grid and Yates' butterfly
     ========================================================================= */
  (function figA() {
    var mat = $('#fa-mat'), bf = $('#fa-bf'); if (!mat || !bf) return;
    var C = F0.canvas(mat), ctx = C.ctx;
    var rand = rng(1937);
    var k = 3, N = 8, x = [], L = [], pass = 3, playing = false, rowCur = -1, rowHov = -1, acc = 0, lastT = 0;
    var kSeg = $('#fa-k'), bitsRow = $('#fa-bits-row'), bits = $('#fa-bits'), cap = $('#fa-cap'), passOut = $('#fa-pass');
    var playBtn = $('#fa-play'), back = $('#fa-back'), fwd = $('#fa-fwd'), count = $('#fa-count'), matLab = $('#fa-mat-lab');
    function newInputs(r) { x = []; for (var i = 0; i < N; i++) x.push(r() < 0.5 ? 1 : 0); if (x.every(function (v) { return !v; })) x[N - 1] = 1; }
    function compute() {
      L = [x.slice()];
      for (var t = 1; t <= k; t++) {
        var prev = L[t - 1], nx = prev.slice(), bit = 1 << (t - 1);
        for (var i = 0; i < N; i++) if (i & bit) nx[i] = prev[i] ^ prev[i ^ bit];
        L.push(nx);
      }
    }
    function yDirect(i) { var s = 0; for (var j = 0; j < N; j++) if ((j & i) === j) s ^= x[j]; return s; }
    /* ---- grid (canvas) ---- */
    function mgeom() {
      var w = C.w, h = C.h, side = Math.min(w, h - 34) - 10;
      var cs = side / (N + 1.6), tot = (N + 1.6) * cs;
      var ox = (w - tot) / 2, oy = 32 + (h - 34 - tot) / 2;
      return { cs: cs, mx: ox, my: oy + 1.6 * cs, xs: oy, ys: ox + (N + 0.6) * cs };
    }
    function drawMat() {
      var g = mgeom(), cs = g.cs, mk = F0.css('--mk'), ink = F0.css('--ink'), ink3 = F0.css('--ink-3'), grid = F0.css('--grid'), bg3 = F0.css('--bg-3');
      ctx.clearRect(0, 0, C.w, C.h);
      var hr = rowHov >= 0 ? rowHov : rowCur;
      if (hr >= 0) { ctx.fillStyle = bg3; ctx.fillRect(g.mx - 3, g.my + hr * cs, N * cs + 6 + (g.ys - g.mx - N * cs) + cs, cs); }
      var gap = Math.max(0.5, cs * 0.08);
      for (var i = 0; i < N; i++) for (var j = 0; j < N; j++) {
        var px = g.mx + j * cs, py = g.my + i * cs;
        if ((j & i) === j) {
          ctx.globalAlpha = x[j] ? 1 : 0.24; ctx.fillStyle = mk;
          ctx.fillRect(px + gap, py + gap, cs - 2 * gap, cs - 2 * gap); ctx.globalAlpha = 1;
        } else if (cs >= 9) {
          ctx.fillStyle = grid; ctx.fillRect(px + cs / 2 - 0.75, py + cs / 2 - 0.75, 1.5, 1.5);
        }
      }
      /* input strip (top) and output strip (right): filled = 1, hollow = 0 */
      function bitCell(px, py, v) {
        var s = cs - 2 * gap - Math.max(1, cs * 0.12);
        var ox = px + (cs - s) / 2, oy = py + (cs - s) / 2;
        if (v) { ctx.fillStyle = ink; ctx.fillRect(ox, oy, s, s); }
        else { ctx.strokeStyle = ink3; ctx.lineWidth = 1; ctx.strokeRect(ox + 0.5, oy + 0.5, s - 1, s - 1); }
      }
      for (var jj = 0; jj < N; jj++) bitCell(g.mx + jj * cs, g.xs, x[jj]);
      var yv = L[k];
      for (var ii = 0; ii < N; ii++) bitCell(g.ys, g.my + ii * cs, pass === k ? yv[ii] : 0);
      if (pass < k) { ctx.fillStyle = ink3; ctx.font = '500 ' + Math.max(9, Math.min(12, cs * 0.7)) + 'px ' + F0.css('--f-mono'); ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; for (var i2 = 0; i2 < N; i2 += Math.max(1, N / 8)) ctx.fillText('?', g.ys + cs / 2, g.my + i2 * cs + cs / 2); }
      ctx.fillStyle = ink3; ctx.font = '500 11px ' + F0.css('--f-mono'); ctx.textBaseline = 'middle';
      ctx.textAlign = 'right'; ctx.fillText('x', g.mx - 6, g.xs + cs / 2);
      ctx.textAlign = 'center'; ctx.fillText('y', g.ys + cs / 2, g.xs + cs / 2);
    }
    function matPick(ev) {
      var b = mat.getBoundingClientRect(), px = ev.clientX - b.left, py = ev.clientY - b.top, g = mgeom();
      var j = Math.floor((px - g.mx) / g.cs), i = Math.floor((py - g.my) / g.cs);
      if (py >= g.xs && py < g.xs + g.cs && j >= 0 && j < N) return { input: j };
      if (i >= 0 && i < N && px >= g.mx && px < g.ys + g.cs) return { row: i, col: (j >= 0 && j < N) ? j : -1 };
      return null;
    }
    function rowHTML(i) {
      var terms = [], s = 0;
      for (var j = 0; j < N; j++) if ((j & i) === j) { terms.push(j); s ^= x[j]; }
      var shown = terms.length > 8 ? terms.slice(0, 8) : terms;
      return '<div class="tip-k">Output for ' + F0.esc(subsetLong(i)) + '</div><div class="tip-t">XOR of ' + terms.length + ' input' + (terms.length > 1 ? 's' : '') + ' = ' + s + '</div>' +
        '<div class="tip-note">' + shown.map(function (j) { return F0.esc(subsetName(j)) + ':' + x[j]; }).join(' + ') + (terms.length > 8 ? ' + …' : '') + '</div>';
    }
    function rowText(i) {
      var terms = [], s = 0;
      for (var j = 0; j < N; j++) if ((j & i) === j) { terms.push(subsetName(j) + ' = ' + x[j]); s ^= x[j]; }
      var more = terms.length > 12 ? ', and ' + (terms.length - 12) + ' more' : '';
      return 'Output for ' + subsetLong(i) + ' adds ' + terms.length + ' input' + (terms.length > 1 ? 's' : '') + ' (' + terms.slice(0, 12).join(', ') + more + '): result ' + s + '.';
    }
    mat.addEventListener('pointermove', function (ev) {
      var p = matPick(ev);
      if (p && p.row != null) { rowHov = p.row; F0.tip.show(rowHTML(p.row), ev.clientX, ev.clientY); mat.style.cursor = 'crosshair'; }
      else if (p && p.input != null) { rowHov = -1; F0.tip.show('<div class="tip-k">Input bit</div><div class="tip-t">' + F0.esc(subsetLong(p.input)) + ' = ' + x[p.input] + '</div><div class="tip-foot">Click to flip</div>', ev.clientX, ev.clientY); mat.style.cursor = 'pointer'; }
      else { rowHov = -1; F0.tip.hide(); mat.style.cursor = 'default'; }
      drawMat(); hiRow();
    });
    mat.addEventListener('pointerleave', function () { rowHov = -1; F0.tip.hide(); drawMat(); hiRow(); });
    mat.addEventListener('click', function (ev) { var p = matPick(ev); if (p && p.input != null) flip(p.input); });
    mat.addEventListener('focus', function () { if (rowCur < 0) rowCur = N - 1; drawMat(); hiRow(); cap.textContent = rowText(rowCur); });
    mat.addEventListener('blur', function () { rowCur = -1; drawMat(); hiRow(); });
    mat.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') rowCur = Math.min(N - 1, rowCur + 1); else if (e.key === 'ArrowUp') rowCur = Math.max(0, rowCur - 1);
      else if (e.key === 'Home') rowCur = 0; else if (e.key === 'End') rowCur = N - 1; else return;
      e.preventDefault(); drawMat(); hiRow(); cap.textContent = rowText(rowCur);
    });
    /* ---- butterfly (SVG) ---- */
    var BF = { W: 600, H: 600 }, nodes = [];
    function bgeom() {
      var labW = N <= 16 ? 66 : 34, x0 = labW + 16, x1 = BF.W - 24, y0 = 60, y1 = BF.H - 50;
      var dx = (x1 - x0) / Math.max(1, k), dy = N > 1 ? (y1 - y0) / (N - 1) : 0;
      var r = Math.max(2.4, Math.min(11, dy * 0.34));
      return { x0: x0, dx: dx, y0: y0, dy: dy, r: r, labW: labW };
    }
    function drawBf() {
      var cw = Math.round(bf.parentNode.getBoundingClientRect().width) || 600;
      BF.W = BF.H = Math.max(400, Math.min(600, cw));
      bf.setAttribute('viewBox', '0 0 ' + BF.W + ' ' + BF.H);
      while (bf.lastChild && bf.lastChild.nodeName !== 'desc') bf.removeChild(bf.lastChild);
      var g = bgeom(), gE = el('g', {}, bf), gN = el('g', {}, bf), gT = el('g', {}, bf);
      function X(t) { return g.x0 + t * g.dx; } function Y(i) { return g.y0 + i * g.dy; }
      /* current pass band */
      if (pass > 0) el('rect', { x: X(pass - 1) + 4, y: g.y0 - 54, width: g.dx - 8, height: (N - 1) * g.dy + 66, style: 'fill:color-mix(in srgb, var(--mk) 8%, transparent)' }, gE);
      for (var t = 1; t <= k; t++) {
        var bit = 1 << (t - 1), done = t <= pass;
        el('text', { x: (X(t - 1) + X(t)) / 2, y: g.y0 - 36, 'text-anchor': 'middle', 'class': 'bf-t' + (done ? ' strong' : '') }, gT, '+' + LET[t - 1]);
        el('text', { x: (X(t - 1) + X(t)) / 2, y: g.y0 - 18, 'text-anchor': 'middle', 'class': 'bf-t' }, gT, (N / 2) + ' XOR');
        for (var i = 0; i < N; i++) {
          el('line', { x1: X(t - 1), y1: Y(i), x2: X(t), y2: Y(i), stroke: done ? 'var(--line-ui)' : 'var(--grid)', 'stroke-width': 1 }, gE);
          if (i & bit) el('line', { x1: X(t - 1), y1: Y(i ^ bit), x2: X(t), y2: Y(i), stroke: done ? 'var(--mk)' : 'var(--grid)', 'stroke-width': done ? (N > 16 ? 1 : 1.6) : 1, 'stroke-linecap': 'round' }, gE);
        }
      }
      nodes = [];
      for (var c = 0; c <= k; c++) {
        for (var ii = 0; ii < N; ii++) {
          var known = c <= pass, v = L[c][ii], recv = c > 0 && (ii & (1 << (c - 1)));
          var attrs = { cx: X(c), cy: Y(ii), r: g.r, 'stroke-width': recv && known ? 2 : 1.2 };
          if (!known) { attrs.fill = 'var(--bg-1)'; attrs.stroke = 'var(--grid)'; }
          else { attrs.fill = v ? 'var(--ink)' : 'var(--bg-2)'; attrs.stroke = recv ? 'var(--mk)' : (v ? 'var(--ink)' : 'var(--ink-3)'); }
          if (c === 0) {
            var gg = el('g', { 'class': 'bf-in', 'data-i': ii, 'aria-hidden': 'true' }, gN);
            el('circle', { cx: X(0), cy: Y(ii), r: Math.max(g.r + 4, Math.min(14, g.dy / 2)), fill: 'transparent' }, gg);
            var cc = el('circle', attrs, gg); cc.setAttribute('class', 'ring');
          } else el('circle', attrs, gN);
        }
      }
      if (N <= 16) {
        for (var j = 0; j < N; j++) el('text', { x: g.labW, y: Y(j) + 5, 'text-anchor': 'end', 'class': 'bf-t ink' }, gT, subsetName(j));
      } else {
        el('text', { x: g.labW, y: Y(0) + 5, 'text-anchor': 'end', 'class': 'bf-t' }, gT, '∅');
        el('text', { x: g.labW, y: Y(N - 1) + 5, 'text-anchor': 'end', 'class': 'bf-t' }, gT, 'all');
      }
      $('#fa-bf-desc').textContent = "Yates' butterfly for k = " + k + ': ' + k + (k === 1 ? ' pass of 1 XOR gate. ' : ' passes of ' + (N / 2) + ' XOR gates each. ') + pass + ' of ' + k + ' passes done.' + (pass === k ? ' Outputs: ' + L[k].join(' ') + '.' : '');
    }
    bf.addEventListener('click', function (e) { var g = e.target.closest('.bf-in'); if (g) flip(+g.getAttribute('data-i')); });
    function hiRow() { /* outline the hovered output row in the butterfly */
      var old = $('.bf-hi', bf); if (old) old.remove();
      var hr = rowHov >= 0 ? rowHov : rowCur; if (hr < 0) return;
      var g = bgeom();
      el('rect', { 'class': 'bf-hi', x: g.x0 - g.r - 4, y: g.y0 + hr * g.dy - g.r - 3, width: k * g.dx + 2 * g.r + 8, height: 2 * g.r + 6, fill: 'none', stroke: 'var(--ink-2)', 'stroke-width': 1, rx: 3 }, bf);
    }
    /* ---- shared update ---- */
    function renderBits() {
      bitsRow.hidden = N > 16;
      bits.textContent = '';
      if (N > 16) return;
      for (var i = 0; i < N; i++) {
        var b = D.createElement('button'); b.type = 'button'; b.setAttribute('data-i', i); b.setAttribute('aria-pressed', x[i] ? 'true' : 'false');
        b.setAttribute('aria-label', 'Input ' + subsetLong(i) + ': ' + x[i]);
        var s1 = D.createElement('span'); s1.textContent = x[i]; var s2 = D.createElement('span'); s2.className = 'nm'; s2.textContent = subsetName(i);
        b.appendChild(s1); b.appendChild(s2); bits.appendChild(b);
      }
    }
    bits.addEventListener('click', function (e) { var b = e.target.closest('button'); if (b) { flip(+b.getAttribute('data-i')); var nb = bits.querySelector('[data-i="' + b.getAttribute('data-i') + '"]'); if (nb) nb.focus(); } });
    function flip(i) { x[i] ^= 1; compute(); render(); }
    function renderCount() {
      var yates = k * N / 2, naive = Math.pow(3, k) - N, used = pass * N / 2;
      count.innerHTML = '<div class="fa-bar"><span class="fa-bk">Yates&rsquo; butterfly</span><span class="fa-track"><i class="fa-fill y" style="width:' + (100 * yates / naive).toFixed(1) + '%"></i></span><span class="fa-bv">' + fmt(yates) + (yates === 1 ? ' XOR' : ' XORs') + '</span></div>' +
        '<div class="fa-bar"><span class="fa-bk">Every sub-choice separately</span><span class="fa-track"><i class="fa-fill n" style="width:100%"></i></span><span class="fa-bv">' + fmt(naive) + (naive === 1 ? ' XOR' : ' XORs') + '</span></div>';
      var ok = true; for (var i = 0; i < N; i++) if (L[k][i] !== yDirect(i)) ok = false;
      cap.textContent = 'k = ' + k + ', N = ' + N + ': ' + (pass === k ? (k === 1 ? 'the 1 pass is done, 1 XOR gate. ' : 'all ' + k + ' passes done, ' + fmt(yates) + ' XOR gates. ') + (ok ? 'The outputs match the grid.' : 'MISMATCH') : pass + ' of ' + k + ' passes done, ' + fmt(used) + ' of ' + fmt(yates) + ' XOR gates used.');
      passOut.textContent = 'pass ' + pass + ' of ' + k;
      back.disabled = pass === 0; fwd.disabled = pass === k;
    }
    function render() { drawMat(); drawBf(); hiRow(); renderBits(); renderCount(); matLab.textContent = 'Grid · N = ' + N; }
    function setK(nk) { k = nk; N = 1 << k; pass = k; rowCur = -1; newInputs(rng(1937 + k)); compute(); stopPlay(); setPressed(kSeg, 'data-k', k); render(); }
    kSeg.addEventListener('click', function (e) { var b = e.target.closest('button'); if (b) setK(+b.getAttribute('data-k')); });
    $('#fa-rand').addEventListener('click', function () { newInputs(rand); compute(); render(); });
    back.addEventListener('click', function () { stopPlay(); if (pass > 0) { pass--; render(); } });
    fwd.addEventListener('click', function () { stopPlay(); if (pass < k) { pass++; render(); } });
    var loop = F0.loop(function (now) {
      if (!lastT) lastT = now; acc += now - lastT; lastT = now;
      if (acc >= 750) { acc = 0; if (pass < k) { pass++; render(); } if (pass >= k) stopPlay(); }
    });
    function stopPlay() { playing = false; loop.stop(); playBtn.setAttribute('aria-pressed', 'false'); }
    playBtn.addEventListener('click', function () {
      if (!F0.motion()) { pass = pass >= k ? 0 : pass + 1; render(); return; } /* motion off: one pass per press */
      if (playing) { stopPlay(); return; }
      if (pass >= k) { pass = 0; render(); }
      playing = true; acc = 0; lastT = 0; playBtn.setAttribute('aria-pressed', 'true'); loop.start();
    });
    F0.whenVisible(bf, null, function () { if (playing) stopPlay(); });
    F0.onMotion(function (on) { if (!on && playing) stopPlay(); });
    C.resize(drawMat); F0.onTheme(drawMat);
    var lastBW = 0;
    if ('ResizeObserver' in window) new ResizeObserver(function () { var w = Math.round(bf.parentNode.getBoundingClientRect().width); if (w && w !== lastBW) { lastBW = w; drawBf(); hiRow(); } }).observe(bf.parentNode);
    newInputs(rng(1937 + k)); compute(); render();
  })();

  /* =========================================================================
     FIGURE B1: the eight-row gadget on bits
     ========================================================================= */
  (function figB1() {
    var svg = $('#fb-svg'); if (!svg) return;
    var WIRES = ['x', 'A', 'c', 'y'], WY = { x: 78, A: 158, c: 238, y: 318 }, G = { w: 640, h: 360, left: 64, col: 66, r: 10 };
    var START = { x: ['x'], A: ['a₀'], c: ['c₀'], y: ['y₀'] };
    /* [target, source, coefficient, route] in schedule order (x1_e1_rep.c rows 0-7) */
    var ROWS = [['y', 'A', 'J', 'side'], ['y', 'c', 'R', 'centre'], ['A', 'x', 'V', 'side'], ['c', 'x', 'G', 'centre'],
                ['y', 'c', 'R', 'centre'], ['y', 'A', 'J', 'side'], ['c', 'x', 'G', 'centre'], ['A', 'x', 'V', 'side']];
    var on = { centre: true, side: false }, step = 8, playing = false, acc = 0, lastT = 0;
    var terms = $('#fb-terms'), verdict = $('#fb-verdict'), log = $('#fb-log'), playBtn = $('#fb-play');
    var CX = function (r) { return G.left + (r + 0.5) * G.col; };
    function state(upto) {
      /* each wire: ordered list of {t, live, gone} */
      var w = {}; WIRES.forEach(function (n) { w[n] = START[n].map(function (t) { return { t: t, live: true, gone: -1 }; }); });
      var lines = [];
      for (var r = 0; r < upto; r++) {
        var R = ROWS[r], tgt = R[0], src = R[1], active = on[R[3]];
        if (active) {
          w[src].filter(function (e) { return e.live; }).forEach(function (s) {
            var hit = w[tgt].filter(function (e) { return e.t === s.t; })[0];
            if (hit && hit.live) { hit.live = false; hit.gone = r; }
            else if (hit) { hit.live = true; hit.gone = -1; }
            else w[tgt].push({ t: s.t, live: true, gone: -1 });
          });
        }
        lines.push(r);
      }
      return w;
    }
    function sumText(list) { var l = list.filter(function (e) { return e.live; }).map(function (e) { return e.t; }); return l.length ? l.join(' + ') : '0'; }
    function draw() {
      while (svg.lastChild && svg.lastChild.nodeName !== 'desc') svg.removeChild(svg.lastChild);
      for (var r = 0; r < 8; r++) {
        el('rect', { 'class': 'fb-col-bg' + (r === step - 1 ? ' cur' : (r < step - 1 ? ' done' : '')), x: CX(r) - G.col / 2 + 3, y: 36, width: G.col - 6, height: G.h - 44 }, svg);
        el('text', { 'class': 'fb-rowno', x: CX(r), y: 26 }, svg, G.col < 56 ? String(r) : 'row ' + r);
      }
      WIRES.forEach(function (n) {
        el('line', { 'class': 'fb-wire', x1: G.left - 6, y1: WY[n], x2: G.w - 6, y2: WY[n] }, svg);
        el('text', { 'class': 'fb-wl', x: G.left < 50 ? 10 : 22, y: WY[n] + 5 }, svg, n);
      });
      ROWS.forEach(function (R, r) {
        var active = on[R[3]], g = el('g', { 'class': 'fb-gate ' + (active ? 'on' : 'off') + (r < step ? '' : ' later') }, svg);
        if (r >= step) g.setAttribute('opacity', active ? '.55' : '.25');
        var ys = WY[R[1]], yt = WY[R[0]], x = CX(r), dir = yt > ys ? 1 : -1;
        el('line', { x1: x, y1: ys, x2: x, y2: yt - dir * 10 }, g);
        el('circle', { 'class': 'src', cx: x, cy: ys, r: 4.5 }, g);
        var rr = G.r, pr = rr * 0.6;
        el('circle', { 'class': 'xo', cx: x, cy: yt, r: rr }, g);
        el('path', { 'class': 'xp', d: 'M' + (x - pr) + ' ' + yt + 'h' + 2 * pr + 'M' + x + ' ' + (yt - pr) + 'v' + 2 * pr, fill: 'none' }, g);
        el('text', { 'class': 'fb-coef', x: x + (G.col < 56 ? 9 : 15), y: (ys + yt) / 2 + 4 }, g, R[2] + (active || G.col < 56 ? '' : '=0'));
      });
      $('#fb-svg-d').textContent = 'Gadget after ' + step + ' of 8 rows. Centre route ' + (on.centre ? 'on' : 'off') + ', side route ' + (on.side ? 'on' : 'off') + '.';
    }
    function render() {
      draw();
      var w = state(step);
      terms.innerHTML = WIRES.map(function (n) {
        return '<div><p class="w">' + n + '<span>' + (n === 'x' ? 'value to deliver' : n === 'y' ? 'answer' : 'helper') + '</span></p><div class="fb-chips">' + w[n].map(function (e) {
          var sig = e.t === 'x' && n !== 'x';
          return '<span class="fb-chip' + (sig ? ' sig' : '') + (e.live ? '' : ' gone') + '" title="' + (e.live ? 'present' : 'cancelled at row ' + e.gone) + '">' + F0.esc(e.t) + '</span>';
        }).join('') + '</div></div>';
      }).join('');
      var parity = (on.centre ? 1 : 0) ^ (on.side ? 1 : 0);
      var lis = $$('li', log);
      ROWS.forEach(function (R, r) {
        var ws = state(r + 1), act = on[R[3]];
        lis[r].textContent = 'Row ' + r + ': ' + R[0] + ' += ' + R[2] + '·' + R[1] + (act ? '' : ' (switched off)') + ' → ' + R[0] + ' = ' + sumText(ws[R[0]][0] ? ws[R[0]] : []);
        lis[r].className = r === step - 1 ? 'cur' : '';
      });
      verdict.classList.toggle('bad', step === 8 && !parity);
      if (step < 8) {
        verdict.innerHTML = (step === 0 ? 'Before row 0' : 'After row ' + (step - 1)) + ': y = <b>' + F0.esc(sumText(w.y)) + '</b>. ' + (step === 0 ? 'Press play or step through the rows.' : step <= 2 ? 'Rows 0 and 1 pour the helpers&rsquo; junk into y, wherever a switch is on.' : step <= 4 ? 'The helpers now carry x as well.' : step <= 6 ? 'The junk arrives a second time and cancels.' : 'Taking x back out of the helpers.');
      } else if (parity) {
        verdict.innerHTML = '<b>RG + JV = 1 (odd).</b> y ends as ' + F0.esc(sumText(w.y)) + '; both helpers are restored.';
      } else {
        verdict.innerHTML = '<b>RG + JV = 0 (even).</b> x ' + (on.centre ? 'arrived twice and cancelled' : 'never arrived') + ': y ends as ' + F0.esc(sumText(w.y)) + '. Nothing was delivered: the gadget fails.';
      }
      $('#fb-back').disabled = step === 0; $('#fb-fwd').disabled = step === 8;
    }
    function sw(btn, key) { btn.addEventListener('click', function () { on[key] = !on[key]; btn.setAttribute('aria-pressed', String(on[key])); render(); }); }
    sw($('#fb-rg'), 'centre'); sw($('#fb-jv'), 'side');
    fitSvg(svg, function (w, h) {
      G.w = w; G.h = h; G.left = w < 480 ? 34 : 64; G.col = (w - G.left - 8) / 8; G.r = Math.max(7, Math.min(10, G.col * 0.24));
      var top = 52, bot = h - 22, gap = (bot - top) / 3;
      WY = { x: top, A: top + gap, c: top + 2 * gap, y: bot };
      if (svg.childNodes.length) draw();
    });
    $('#fb-back').addEventListener('click', function () { stop(); if (step > 0) { step--; render(); } });
    $('#fb-fwd').addEventListener('click', function () { stop(); if (step < 8) { step++; render(); } });
    var loop = F0.loop(function (now) {
      if (!lastT) lastT = now; acc += now - lastT; lastT = now;
      if (acc >= 850) { acc = 0; if (step < 8) { step++; render(); } if (step >= 8) stop(); }
    });
    function stop() { playing = false; loop.stop(); playBtn.setAttribute('aria-pressed', 'false'); }
    playBtn.addEventListener('click', function () {
      if (!F0.motion()) { step = step >= 8 ? 0 : step + 1; render(); return; }
      if (playing) { stop(); return; }
      if (step >= 8) { step = 0; render(); }
      playing = true; acc = 0; lastT = 0; playBtn.setAttribute('aria-pressed', 'true'); loop.start();
    });
    F0.whenVisible(svg, null, function () { if (playing) stop(); });
    F0.onMotion(function (m) { if (!m && playing) stop(); });
    render();
  })();

  /* =========================================================================
     FIGURE B2: two labels on a ring of 12 points
     ========================================================================= */
  (function figB2() {
    var svg = $('#fr-svg'); if (!svg) return;
    var H = 12, S = [0, 1, 2, 3, 4, 5, 6], T = [4, 5, 6, 7, 8, 9, 10], centre = 3, msg = '';
    var read = $('#fr-read'), seg = $('#fr-centre');
    function ang(i) { return -Math.PI / 2 + i * 2 * Math.PI / H; }
    function pt(i, R) { return { x: Math.cos(ang(i)) * R, y: Math.sin(ang(i)) * R }; }
    function has(a, i) { return a.indexOf(i) >= 0; }
    function poly(a) { return a.slice().sort(function (p, q) { return p - q; }).map(function (i) { var p = pt(i, 86); return p.x.toFixed(1) + ',' + p.y.toFixed(1); }).join(' '); }
    function draw() {
      svg.textContent = '';
      el('circle', { cx: 0, cy: 0, r: 86, fill: 'none', stroke: 'var(--grid)', 'stroke-width': 1 }, svg);
      if (T.length > 2) el('polygon', { points: poly(T), fill: 'color-mix(in srgb, var(--mk) 10%, transparent)', stroke: 'var(--mk)', 'stroke-width': 1 }, svg);
      el('polygon', { 'class': 'fr-hull s', points: poly(S) }, svg);
      for (var i = 0; i < H; i++) {
        var p = pt(i, 86), q = pt(i, 108), inS = has(S, i), inT = has(T, i);
        var g = el('g', { 'class': 'fr-pt', tabindex: 0, role: 'button', 'aria-pressed': String(inT), 'data-i': i,
          'aria-label': 'Point ' + (i + 1) + (inS ? ', in S' : '') + (inT ? ', in T' : ', not in T') + '. Press to ' + (inT ? 'remove it from' : 'add it to') + ' T.' }, svg);
        el('circle', { 'class': 'hit', cx: p.x, cy: p.y, r: 15 }, g);
        if (!inS && !inT) el('circle', { 'class': 'e', cx: p.x, cy: p.y, r: 4 }, g);
        if (inT) el('circle', { 'class': 't', cx: p.x, cy: p.y, r: 6.5 }, g);
        if (inS) el('circle', { 'class': 's', cx: p.x, cy: p.y, r: 10.5 }, g);
        el('text', { x: q.x, y: q.y + 3 }, g, String(i + 1));
      }
    }
    function readout() {
      if (T.length !== 7) {
        read.innerHTML = '<p class="k">Label T</p><p>T has ' + T.length + ' of its 7 points. ' + (T.length < 7 ? 'Press an empty point to add one.' : 'Press a filled point to remove one.') + '</p>' + (msg ? '<p>' + F0.esc(msg) + '</p>' : '');
        return;
      }
      var inter = S.filter(function (i) { return has(T, i); }), n = inter.length, cnt = binom(n, centre), odd = cnt % 2 === 1;
      var kind = n === 7 ? 'same' : (n % 3 === 0 ? 'nb' : 'un');
      var kindTxt = kind === 'same' ? 'same label (S = T)' : kind === 'nb' ? 'neighbours (overlap a multiple of 3)' : 'unrelated labels';
      var v, cls;
      if (kind === 'same') { v = odd ? '<b>Signal survives.</b> The label reaches itself an odd number of times.' : '<b>Signal lost.</b> An even count would cancel the label&rsquo;s own data.'; cls = odd ? '' : 'bad'; }
      else if (kind === 'un') { v = odd ? '<b>Leak: the gadget fails.</b> Unrelated labels share an odd number of centre wires, so junk survives.' : '<b>Junk cancels.</b> Unrelated labels share an even number of centre wires.'; cls = odd ? 'bad' : ''; }
      else { v = odd ? '<b>Allowed, with a side wire.</b> Neighbours may share an odd count; one side wire patches it.' : '<b>Fine.</b> Even, so no side wire is needed.'; cls = odd ? 'warn' : ''; }
      var sets = [];
      if (cnt <= 20) {
        var c = inter.slice().sort(function (a, b) { return a - b; });
        (function rec(start, acc2) { if (acc2.length === centre) { sets.push('{' + acc2.map(function (i) { return i + 1; }).join(',') + '}'); return; } for (var i = start; i < c.length; i++) rec(i + 1, acc2.concat(c[i])); })(0, []);
      }
      read.innerHTML = '<p class="k">Shared points n</p><p class="big">' + n + '</p>' +
        '<p class="k">Shared centre wires</p><p><span class="big">' + cnt + '</span> = C(' + n + ', ' + centre + ') <span class="par">' + (odd ? 'ODD' : 'EVEN') + '</span></p>' +
        (sets.length ? '<div class="fr-trip" aria-label="The shared ' + centre + '-point sets">' + sets.map(function (s) { return '<span>' + s + '</span>'; }).join('') + '</div>' : (cnt ? '<p>' + cnt + ' shared ' + centre + '-point sets</p>' : '')) +
        '<p class="k">Pair</p><p>' + kindTxt + '</p><p class="verdict ' + cls + '">' + v + '</p>' + (msg ? '<p>' + F0.esc(msg) + '</p>' : '');
    }
    function render() { draw(); readout(); }
    function toggle(i) {
      msg = '';
      if (has(T, i)) T = T.filter(function (j) { return j !== i; });
      else if (T.length >= 7) msg = 'T already has 7 points: remove one first.';
      else T.push(i);
      render();
      var f = svg.querySelector('[data-i="' + i + '"]'); if (f) f.focus();
    }
    svg.addEventListener('click', function (e) { var g = e.target.closest('.fr-pt'); if (g) toggle(+g.getAttribute('data-i')); });
    svg.addEventListener('keydown', function (e) {
      var g = e.target.closest('.fr-pt'); if (!g) return;
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(+g.getAttribute('data-i')); }
    });
    function turn(d) { msg = ''; T = T.map(function (i) { return (i + d + H) % H; }); render(); }
    $('#fr-cw').addEventListener('click', function () { turn(1); });
    $('#fr-ccw').addEventListener('click', function () { turn(-1); });
    seg.addEventListener('click', function (e) { var b = e.target.closest('button'); if (!b) return; centre = +b.getAttribute('data-c'); setPressed(seg, 'data-c', centre); render(); });
    render();
  })();

  /* =========================================================================
     Exponent model (x1_theorems.py, re-computed with exact whole numbers)
     ========================================================================= */
  var FAM = {
    thm1: { name: 'Theorem 1', fam: '4', mu: 1, h0: 70, h1: 110 },
    thm1p: { name: 'Theorem 1′', fam: '4', mu: 2, h0: 36, h1: 70 },
    thm2: { name: 'Theorem 2 (E1)', fam: '7', mu: 2, h0: 14, h1: 40 }
  };
  function params(f, h) {
    var H = BigInt(h), v, c, d;
    if (f.fam === '4') { v = binomBig(h, 4); c = 1n + H + binomBig(h, 2); d = binomBig(h - 4, 4) + 4n * BigInt(h - 4); }
    else { v = binomBig(h, 7); c = binomBig(h, 3); d = 35n * binomBig(h - 7, 4); }
    var m = H * H * H, N0 = v * v * v, W = 2n * N0 + 3n * v * v * (v * d + c), delta = BigInt(f.mu) * N0 - 6n * v * v * c * H;
    var w = 0, p = 1n; while (p < W) { p *= 3n; w++; }
    var eps = Number(delta) / (Number(p) * Number(m));
    var omt = delta > 0n ? -Math.log1p(-eps) / Math.log(Number(m)) : null;
    return { h: h, v: v, c: c, d: d, m: Number(m), w: w, delta: delta, eps: eps, omt: omt };
  }
  var cache = {};
  function curve(key) {
    if (cache[key]) return cache[key];
    var f = FAM[key], pts = [], best = null, thr = null;
    for (var h = f.h0; h <= f.h1; h++) { var p = params(f, h); pts.push(p); if (p.omt != null && (!best || p.omt > best.omt)) best = p; if (p.omt != null && thr == null) thr = h; }
    return (cache[key] = { pts: pts, best: best, thr: thr });
  }
  var sel = { thm: 'thm2', c0: 84 };
  var subs = [];

  /* =========================================================================
     FIGURE C: how far away is eventually?
     ========================================================================= */
  (function figC() {
    var svg = $('#fc-svg'); if (!svg) return;
    var range = $('#fc-range'), read = $('#fc-read'), dims = { w: 800, h: 400 };
    function model() {
      var b = curve(sel.thm).best, lm = Math.log10(b.m);
      var Lc = lm * Math.log(sel.c0) / b.eps; /* log10 k at the crossover, PROOF.md §8 */
      return { b: b, lm: lm, Lc: Lc, Xc: Math.log10(Lc), r: function (X) { var L = Math.pow(10, X); return Math.log10(sel.c0) - b.eps * L / (lm * Math.LN10); } };
    }
    var YMIN = -2, YMAX = 6.6, XMAX = 16;
    function draw(w, h) {
      dims = { w: w, h: h };
      svg.textContent = ''; el('desc', { id: 'fc-desc' }, svg, '');
      var M = model(), ml = w < 520 ? 44 : 58, mr = 16, mt = 30, mb = 42;
      var pw = w - ml - mr, ph = h - mt - mb;
      var X = function (v) { return ml + v / XMAX * pw; }, Y = function (v) { return mt + (YMAX - v) / (YMAX - YMIN) * ph; };
      var root = el('g', { 'class': 'mx-chart' }, svg);
      /* regions */
      el('rect', { 'class': 'area-win', x: ml, y: Y(0), width: pw, height: Y(YMIN) - Y(0) }, root);
      el('rect', { 'class': 'feas', x: ml, y: mt, width: X(Math.log10(2)) - ml, height: ph }, root);
      /* grid */
      for (var e = -2; e <= 6; e++) {
        el('line', { 'class': e === 0 ? 'even' : 'grid', x1: ml, x2: ml + pw, y1: Y(e), y2: Y(e) }, root);
        if (w >= 420 || e % 2 === 0) el('text', { 'class': 'mx-svg-t', x: ml - 8, y: Y(e) + 4, 'text-anchor': 'end' }, root, (e === 0 ? '1×' : pow10txt(e) + '×'));
      }
      var step = w < 520 ? 4 : 2;
      for (var xv = 0; xv <= XMAX; xv += step) {
        el('line', { 'class': 'grid', x1: X(xv), x2: X(xv), y1: mt, y2: mt + ph }, root);
        el('text', { 'class': 'mx-svg-t', x: X(xv), y: mt + ph + 16, 'text-anchor': 'middle' }, root, pow10txt(xv));
      }
      el('text', { 'class': 'mx-svg-t ink', x: ml + pw, y: mt + ph + 34, 'text-anchor': 'end' }, root, 'digits in k →');
      var narrow = w < 560;
      if (!narrow) el('text', { 'class': 'mx-svg-t ink', x: X(2.4), y: Y(0) - 7 }, root, 'break-even: same cost');
      el('text', { 'class': 'mx-svg-t', x: narrow ? ml + 8 : ml + pw - 6, y: Y(YMIN) - 8, 'text-anchor': narrow ? 'start' : 'end' }, root, 'new circuit cheaper');
      el('text', { 'class': 'mx-svg-t', x: ml + pw - 6, y: mt + 14, 'text-anchor': 'end' }, root, 'Yates cheaper');
      el('text', { 'class': 'mx-svg-t ink', x: X(Math.log10(2)) + 6, y: mt + 14 }, root, w < 520 ? 'k ≤ 64' : 'k ≤ 64: every computer ever');
      el('line', { 'class': 'mark', x1: X(Math.log10(2)), x2: X(Math.log10(2)), y1: mt, y2: mt + ph }, root);
      /* the curve */
      var d = '', last = null;
      for (var xx = 0; xx <= XMAX + 1e-9; xx += 0.02) {
        var yy = M.r(xx); if (yy < YMIN) { var xe = Math.log10((Math.log10(sel.c0) - YMIN) * M.lm * Math.LN10 / M.b.eps); d += 'L' + X(Math.min(XMAX, xe)).toFixed(1) + ',' + Y(YMIN).toFixed(1); break; }
        d += (last == null ? 'M' : 'L') + X(xx).toFixed(1) + ',' + Y(yy).toFixed(1); last = yy;
      }
      el('path', { 'class': 'line', d: d }, root);
      /* crossover */
      if (M.Xc <= XMAX) {
        el('line', { 'class': 'mark', x1: X(M.Xc), x2: X(M.Xc), y1: Y(0), y2: mt + ph }, root);
        el('circle', { 'class': 'dot', cx: X(M.Xc), cy: Y(0), r: 5 }, root);
        var lab = 'crossover: ' + digitsText(M.Lc, false) + ' digits';
        if (narrow) {
          var tl = el('text', { 'class': 'mx-svg-t strong', x: X(M.Xc) - 8, y: Y(0) + 16, 'text-anchor': 'end' }, root, 'crossover:');
          el('tspan', { x: X(M.Xc) - 8, dy: 14 }, tl, digitsText(M.Lc, false) + ' digits');
        } else el('text', { 'class': 'mx-svg-t strong', x: X(M.Xc) - 8, y: Y(0) + 18, 'text-anchor': 'end' }, root, lab);
      }
      /* cursor */
      var cx = +range.value, cy = Math.max(YMIN, M.r(cx));
      el('line', { 'class': 'cursor', x1: X(cx), x2: X(cx), y1: mt, y2: mt + ph }, root);
      el('circle', { 'class': 'dot', cx: X(cx), cy: Y(cy), r: 5.5 }, root);
      el('text', { 'class': 'mx-svg-t strong', x: 4, y: mt - 14 }, root, 'new circuit’s cost ÷ Yates’');
      $('#fc-desc', svg).textContent = 'For ' + FAM[sel.thm].name + ' with c0 = ' + fmt(sel.c0) + ', the new circuit costs about ' + fmt(sel.c0) + ' times Yates until k has billions of digits; it breaks even when k has ' + digitsText(M.Lc, false) + ' digits.';
      readout(M);
    }
    function digitsText(L, html) { return L < 1e12 ? fmt(Math.floor(L) + 1) : sci(L, 2, html); }
    function readout(M) {
      var X = +range.value, L = Math.pow(10, X), lr = M.r(X), ratio = Math.pow(10, lr);
      var kTxt = L < 1e6 ? 'k has ' + fmt(Math.round(L)) + ' digit' + (Math.round(L) === 1 ? '' : 's') : 'k has ' + sci(L, 1, true) + ' digits';
      var rTxt = ratio >= 1.05 ? '≈ ' + (ratio >= 100 ? fmt(Math.round(ratio)) : ratio.toFixed(ratio >= 10 ? 0 : 1)) + '× Yates' : ratio > 0.95 ? '≈ the same as Yates' : (ratio >= 0.1 ? '≈ ' + ratio.toFixed(2) + '× Yates' : ratio > 1e-3 ? '≈ ' + ratio.toPrecision(2) + '× Yates' : '< 0.001× Yates');
      var win = ratio < 1;
      read.innerHTML = '<div><p class="k">Problem size</p><p class="v">' + kTxt + '</p><p class="s">' + (X < Math.log10(2) + 1e-9 ? 'Real computers live here: no machine can hold N = 2<sup>64</sup> bits.' : 'N = 2<sup>k</sup> inputs. Merely writing down how many digits N has would take about ' + (L < 1e6 ? fmt(Math.round(L)) : sci(L, 1, true)) + ' digits.') + '</p></div>' +
        '<div><p class="k">New circuit&rsquo;s cost</p><p class="v">' + rTxt + '</p><p class="s">' + (ratio > 0.95 && ratio < 1.05 ? 'Within 5% of Yates: this is the crossover.' : win ? 'Cheaper by ' + Math.min(99.9, (1 - ratio) * 100).toFixed(1) + '%: the new circuit wins.' : 'More expensive by a factor of ' + (ratio >= 10 ? fmt(Math.round(ratio)) : ratio.toFixed(1)) + ': Yates wins.') + '</p></div>' +
        '<div><p class="k">Crossover</p><p class="v">' + digitsText(M.Lc, true) + ' digits</p><p class="s">' + FAM[sel.thm].name + ', c<sub>0</sub> = ' + (sel.c0 === 1000000 ? '10<sup>6</sup>' : sel.c0) + '; 1 &minus; &theta;&prime; = ' + sci(M.b.omt, 4, true) + '.</p></div>';
      range.setAttribute('aria-valuetext', (L < 1e6 ? fmt(Math.round(L)) : sci(L, 1, false)) + ' digits in k; new circuit costs ' + rTxt.replace('≈ ', 'about ') + (win ? '' : '; Yates wins'));
    }
    var redraw = fitSvg(svg, draw);
    range.addEventListener('input', function () { draw(dims.w, dims.h); });
    $('#fc-thm').addEventListener('click', function (e) { var b = e.target.closest('button'); if (!b) return; sel.thm = b.getAttribute('data-t'); setPressed($('#fc-thm'), 'data-t', sel.thm); draw(dims.w, dims.h); subs.forEach(function (f) { f(); }); });
    $('#fc-c0').addEventListener('click', function (e) { var b = e.target.closest('button'); if (!b) return; sel.c0 = +b.getAttribute('data-c'); setPressed($('#fc-c0'), 'data-c', sel.c0); draw(dims.w, dims.h); });
    void redraw;
  })();

  /* =========================================================================
     FIGURE H: the best gadget size
     ========================================================================= */
  (function figH() {
    var svg = $('#fh-svg'); if (!svg) return;
    var dims = { w: 800, h: 300 }, out = $('#fh-out'), capEl = $('#fh-cap'), table = $('#fh-table');
    function draw(w, h) {
      dims = { w: w, h: h };
      svg.textContent = ''; el('desc', { id: 'fh-desc' }, svg, '');
      var cv = curve(sel.thm), pts = cv.pts, best = cv.best;
      var ml = 34, mr = 10, mt = 30, mb = 34, pw = w - ml - mr, ph = h - mt - mb;
      var e = Math.floor(Math.log10(best.omt)), unit = Math.pow(10, e), top = Math.ceil(best.omt / unit * 1.15);
      var Y = function (v) { return mt + ph - v / (top * unit) * ph; };
      var slot = pw / pts.length, bw = Math.min(24, slot * 0.7);
      var root = el('g', { 'class': 'mx-chart' }, svg);
      var tstep = top <= 5 ? 1 : 2;
      for (var t = 0; t <= top; t += tstep) {
        el('line', { 'class': 'grid', x1: ml, x2: ml + pw, y1: Y(t * unit), y2: Y(t * unit) }, root);
        el('text', { 'class': 'mx-svg-t', x: ml - 8, y: Y(t * unit) + 4, 'text-anchor': 'end' }, root, String(t));
      }
      el('text', { 'class': 'mx-svg-t strong', x: 4, y: mt - 12 }, root, '1 − θ′, in units of 10' + supU(e));
      pts.forEach(function (p, i) {
        var cx = ml + slot * (i + 0.5), g = el('g', { 'class': 'colh', tabindex: 0, role: 'img' }, root);
        var lab = 'h = ' + p.h + ': ' + (p.omt != null ? '1 − θ′ = ' + sci(p.omt, 3, false) : 'no saving (the gadget costs more than it saves)') + ', padded roles 3^' + p.w;
        g.setAttribute('aria-label', lab);
        el('rect', { 'class': 'hit', x: cx - slot / 2, y: mt, width: slot, height: ph + 18 }, g);
        if (p.omt != null) {
          var y0 = Y(p.omt), hh = Math.max(1, mt + ph - y0);
          el('path', { 'class': 'bar' + (p === best ? ' best' : ''), d: 'M' + (cx - bw / 2) + ',' + (mt + ph) + 'v' + (-hh + 3) + 'q0,-3 3,-3h' + (bw - 6) + 'q3,0 3,3v' + (hh - 3) + 'z' }, g);
        } else {
          var s = Math.min(4, bw / 3);
          el('path', { 'class': 'no', d: 'M' + (cx - s) + ',' + (mt + ph - 4 - s) + 'l' + 2 * s + ',' + 2 * s + 'M' + (cx + s) + ',' + (mt + ph - 4 - s) + 'l' + (-2 * s) + ',' + 2 * s }, g);
        }
        if (p.h % 5 === 0 || p === best) el('text', { 'class': 'mx-svg-t' + (p === best ? ' strong' : ''), x: cx, y: mt + ph + 16, 'text-anchor': 'middle' }, root, String(p.h));
        g.addEventListener('pointerenter', function (ev) { F0.tip.show(tip(p), ev.clientX, ev.clientY); });
        g.addEventListener('pointermove', function (ev) { F0.tip.show(tip(p), ev.clientX, ev.clientY); });
        g.addEventListener('pointerleave', function () { F0.tip.hide(); });
        g.addEventListener('focus', function () { tipAt(tip(p), g); out.textContent = 'h ' + p.h; });
        g.addEventListener('blur', function () { F0.tip.hide(); out.textContent = ''; });
      });
      el('line', { 'class': 'axis', x1: ml, x2: ml + pw, y1: mt + ph, y2: mt + ph }, root);
      el('text', { 'class': 'mx-svg-t ink', x: ml + pw, y: mt + ph + 30, 'text-anchor': 'end' }, root, 'label size h →');
      var bi = pts.indexOf(best), bx = ml + slot * (bi + 0.5);
      el('text', { 'class': 'mx-svg-t strong', x: bx + (bi > pts.length * 0.7 ? -8 : 8), y: Y(best.omt) - 6, 'text-anchor': bi > pts.length * 0.7 ? 'end' : 'start' }, root, sci(best.omt, 3, false) + ' at h = ' + best.h);
      $('#fh-desc', svg).textContent = FAM[sel.thm].name + ': no saving below h = ' + cv.thr + '; the best label size is h = ' + best.h + ' with 1 − θ′ = ' + sci(best.omt, 4, false) + '.';
    }
    function tip(p) {
      return '<div class="tip-k">' + F0.esc(FAM[sel.thm].name) + ' · h = ' + p.h + '</div><div class="tip-t">' + (p.omt != null ? '1 − θ′ = ' + sci(p.omt, 4, false) : 'No saving') + '</div>' +
        '<div class="tip-rows"><div class="tip-row">labels v = ' + fmt(p.v) + '</div><div class="tip-row">centre wires c = ' + fmt(p.c) + '</div><div class="tip-row">roles padded to 3' + supU(p.w) + '</div><div class="tip-row">saving per level Δ ' + (p.delta > 0n ? '> 0' : '< 0') + '</div></div>';
    }
    function tableRender() {
      var cv = curve(sel.thm), f = FAM[sel.thm];
      var rows = cv.pts.map(function (p) {
        return '<tr' + (p === cv.best ? ' class="best"' : '') + '><td class="n">' + p.h + '</td><td class="n">' + fmt(p.v) + '</td><td class="n">' + fmt(p.c) + '</td><td class="n">' + fmt(p.d) + '</td><td class="n">3<sup>' + p.w + '</sup></td><td class="n">' + (p.delta > 0n ? '+' : '−') + '</td><td class="n">' + (p.omt != null ? sci(p.eps, 4, true) : '') + '</td><td class="n">' + (p.omt != null ? sci(p.omt, 4, true) : 'no saving') + '</td></tr>';
      }).join('');
      table.innerHTML = '<table class="tbl"><caption>' + F0.esc(f.name) + ': exponent saving by label size (computed here)</caption><thead><tr><th scope="col" class="n">h</th><th scope="col" class="n">labels v</th><th scope="col" class="n">centre wires c</th><th scope="col" class="n">side wires per entry</th><th scope="col" class="n">roles padded to</th><th scope="col" class="n">saving Δ</th><th scope="col" class="n">ε</th><th scope="col" class="n">1 − θ′</th></tr></thead><tbody>' + rows + '</tbody></table>';
      var cvv = cv;
      capEl.textContent = f.name + ': no saving below h = ' + cvv.thr + '; the best is h = ' + cvv.best.h + ' (1 − θ′ = ' + sci(cvv.best.omt, 4, false) + ').' + (sel.thm === 'thm2' ? ' At h = 24 the count of roles must be padded up to the next power of 3, and the saving drops by two thirds.' : ' The jagged steps come from padding the count of roles up to a power of 3.');
    }
    fitSvg(svg, draw);
    subs.push(function () { draw(dims.w, dims.h); tableRender(); });
    tableRender();
  })();

  /* =========================================================================
     FIGURE O: overlap histogram at h = 11 (Aska's log, line 1)
     ========================================================================= */
  (function figO() {
    var svg = $('#fo-svg'); if (!svg) return;
    var DATA = [[3, 11550], [4, 46200], [5, 41580], [6, 9240]], TOT = 108570;
    function draw(w, h) {
      svg.textContent = ''; el('desc', { id: 'fo-desc' }, svg, 'Overlap 3: 11,550 pairs (needs a side wire); overlap 4: 46,200; overlap 5: 41,580; overlap 6: 9,240.');
      var ml = 46, mr = 10, mt = 24, mb = 40, pw = w - ml - mr, ph = h - mt - mb, max = 50000;
      var Y = function (v) { return mt + ph - v / max * ph; }, root = el('g', { 'class': 'mx-chart' }, svg);
      [0, 10000, 20000, 30000, 40000, 50000].forEach(function (t) {
        el('line', { 'class': 'grid', x1: ml, x2: ml + pw, y1: Y(t), y2: Y(t) }, root);
        el('text', { 'class': 'mx-svg-t', x: ml - 8, y: Y(t) + 4, 'text-anchor': 'end' }, root, t ? (t / 1000) + 'K' : '0');
      });
      var slot = pw / DATA.length, bw = Math.min(24, slot * 0.5);
      DATA.forEach(function (d, i) {
        var cx = ml + slot * (i + 0.5), y0 = Y(d[1]), hh = mt + ph - y0, g = el('g', { 'class': 'colh', tabindex: 0, role: 'img', 'aria-label': d[0] + ' points shared: ' + fmt(d[1]) + ' ordered pairs (' + (100 * d[1] / TOT).toFixed(1) + '%)' + (d[0] === 3 ? ', needs a side wire' : '') }, root);
        el('rect', { 'class': 'hit', x: cx - slot / 2, y: mt, width: slot, height: ph }, g);
        el('path', { 'class': 'bar' + (d[0] === 3 ? ' best' : ''), d: 'M' + (cx - bw / 2) + ',' + (mt + ph) + 'v' + (-hh + 4) + 'q0,-4 4,-4h' + (bw - 8) + 'q4,0 4,4v' + (hh - 4) + 'z' }, g);
        el('text', { 'class': 'mx-svg-t ink', x: cx, y: y0 - 7, 'text-anchor': 'middle' }, g, fmt(d[1]));
        el('text', { 'class': 'mx-svg-t' + (d[0] === 3 ? ' strong' : ''), x: cx, y: mt + ph + 16, 'text-anchor': 'middle' }, root, String(d[0]));
        var html = '<div class="tip-k">' + d[0] + ' points shared</div><div class="tip-t">' + fmt(d[1]) + ' ordered pairs</div><div class="tip-note">' + (100 * d[1] / TOT).toFixed(1) + '% of all pairs · ' + (d[0] === 3 ? 'needs a side wire' : 'no side wire needed') + '</div>';
        g.addEventListener('pointermove', function (ev) { F0.tip.show(html, ev.clientX, ev.clientY); });
        g.addEventListener('pointerleave', function () { F0.tip.hide(); });
        g.addEventListener('focus', function () { tipAt(html, g); });
        g.addEventListener('blur', function () { F0.tip.hide(); });
      });
      el('line', { 'class': 'axis', x1: ml, x2: ml + pw, y1: mt + ph, y2: mt + ph }, root);
      el('text', { 'class': 'mx-svg-t ink', x: ml + pw, y: mt + ph + 32, 'text-anchor': 'end' }, root, 'points shared →');
      el('text', { 'class': 'mx-svg-t strong', x: ml - 8, y: mt - 10, 'text-anchor': 'end' }, root, 'pairs');
    }
    fitSvg(svg, draw);
  })();
})();
