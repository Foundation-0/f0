/* gf2m-circuits page (research/gf2m-circuits): five figures that run Swapnil Jain's circuits in the browser.
   Hero: all 65,536 AES-field products from the 112-gate circuit. 01: GF(2^4) playground (30-gate circuit vs a
   schoolbook circuit built here). 02: gates-vs-depth staircase. 03: the live S-box (106 / 121 / inverse 109).
   04: baseline-vs-circuit dumbbells and an exhaustive in-browser check of Aska's three contributed circuits.
   Circuits come from circuits.js (Apache-2.0, (c) 2026 Swapnil Jain); this file is new code. */
(function () {
  'use strict';
  var F0 = window.F0, CIR = window.GF2M_CIRCUITS, D = document, NS = 'http://www.w3.org/2000/svg';
  if (!F0 || !CIR) return;
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
  function hex2(v) { return (v < 16 ? '0' : '') + v.toString(16).toUpperCase(); }
  function bin(v, w) { var s = v.toString(2); while (s.length < w) s = '0' + s; return s; }
  function setPressed(group, attr, val) { $$('button', group).forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute(attr) === String(val))); }); }
  function tipAt(html, node) { var r = node.getBoundingClientRect(); F0.tip.show(html, r.left + r.width / 2, r.top + r.height / 2); }
  function now() { return (window.performance && performance.now) ? performance.now() : Date.now(); }
  function fitSvg(svg, draw) {
    var st = svg.parentNode, last = '';
    function go() {
      var r = st.getBoundingClientRect(), w = Math.max(200, Math.round(r.width)), h = Math.max(120, Math.round(r.height));
      var key = w + 'x' + h; if (key === last) return; last = key;
      svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h); draw(w, h);
    }
    if ('ResizeObserver' in window) new ResizeObserver(go).observe(st); else window.addEventListener('resize', go);
    go();
  }
  function rgb(hex) {
    var h = String(hex || '').trim();
    if (/^#[0-9a-f]{3}$/i.test(h)) h = '#' + h[1] + h[1] + h[2] + h[2] + h[3] + h[3];
    var m = /^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i.exec(h);
    return m ? [parseInt(m[1], 16), parseInt(m[2], 16), parseInt(m[3], 16)] : [128, 128, 128];
  }

  /* ---- circuits: decode, depth, evaluate ---- */
  function decode(c, nIn) {
    var op = [], x = [], y = [];
    c.g.split(';').forEach(function (t) { var ch = t.charAt(0), p = t.slice(1).split(','); op.push(ch === '&' ? 1 : ch === '~' ? 2 : 0); x.push(+p[0]); y.push(+p[1]); });
    var dep = new Array(nIn + op.length).fill(0);
    for (var i = 0; i < op.length; i++) dep[nIn + i] = 1 + Math.max(dep[x[i]], dep[y[i]]);
    var maxd = 0; c.o.forEach(function (s) { maxd = Math.max(maxd, dep[s]); });
    var ands = op.filter(function (v) { return v === 1; }).length;
    return { op: op, x: x, y: y, n: op.length, nIn: nIn, o: c.o, dep: dep, depth: maxd, ands: ands, m: c.m, poly: c.poly };
  }
  function evalScalar(C, inputs) {
    var s = new Uint8Array(C.nIn + C.n);
    for (var i = 0; i < C.nIn; i++) s[i] = inputs[i];
    for (var g = 0; g < C.n; g++) {
      var a = s[C.x[g]], b = s[C.y[g]];
      s[C.nIn + g] = C.op[g] === 1 ? (a & b) : C.op[g] === 2 ? (1 ^ a ^ b) : (a ^ b);
    }
    return s;
  }
  function gmul(a, b, poly, m) { var r = 0; while (b) { if (b & 1) r ^= a; a <<= 1; if ((a >> m) & 1) a ^= poly; b >>= 1; } return r; }

  /* exhaustive multiplier check, bitsliced over b; reference built from the linear map b -> a*b.
     Calls back per a-row so the caller can keep products; runs in chunks so the page stays responsive. */
  function checkMult(C, opts) {
    var m = C.m, n = 1 << m, W = Math.max(1, n >> 5), mask = n < 32 ? ((1 << n) >>> 0) - 1 : 0xffffffff;
    var slots = 2 * m + C.n, mem = [], i, w;
    for (i = 0; i < slots; i++) mem.push(new Uint32Array(W));
    var bsig = [];
    for (i = 0; i < m; i++) { var v = new Uint32Array(W); for (var b = 0; b < n; b++) if ((b >> i) & 1) v[b >> 5] |= (1 << (b & 31)) >>> 0; bsig.push(v); }
    var a = 0, bad = 0, t0 = now(), ref = new Uint32Array(W), col = new Array(m);
    function row(aa) {
      for (i = 0; i < m; i++) { mem[i].fill(((aa >> i) & 1) ? 0xffffffff : 0); mem[m + i].set(bsig[i]); }
      for (var g = 0; g < C.n; g++) {
        var Dd = mem[2 * m + g], X = mem[C.x[g]], Y = mem[C.y[g]];
        if (C.op[g] === 1) for (w = 0; w < W; w++) Dd[w] = X[w] & Y[w]; else for (w = 0; w < W; w++) Dd[w] = X[w] ^ Y[w];
      }
      for (i = 0; i < m; i++) col[i] = gmul(aa, 1 << i, C.poly, m);
      for (var j = 0; j < m; j++) {
        ref.fill(0);
        for (i = 0; i < m; i++) if ((col[i] >> j) & 1) { var B = bsig[i]; for (w = 0; w < W; w++) ref[w] ^= B[w]; }
        var O = mem[C.o[j]];
        for (w = 0; w < W; w++) { var diff = ((O[w] ^ ref[w]) & mask) >>> 0; while (diff) { bad++; diff &= diff - 1; } }
      }
      if (opts.onRow) opts.onRow(aa, mem, W);
    }
    (function chunk() {
      var stop = Math.min(n, a + (opts.chunk || n));
      for (; a < stop; a++) row(a);
      if (opts.progress) opts.progress(a, n);
      if (a < n) setTimeout(chunk, 0); else opts.done(bad, n * n, now() - t0);
    })();
  }

  /* =========================================================================
     HERO: every product in the AES field
     ========================================================================= */
  (function hero() {
    var cv = $('#ht-cv'); if (!cv) return;
    var C = decode(CIR.aes112, 16), Cv = F0.canvas(cv), ctx = Cv.ctx;
    var prod = new Uint8Array(65536), ready = false, mode = '0', cur = null, hov = null;
    var off = D.createElement('canvas'); off.width = 256; off.height = 256;
    var octx = off.getContext('2d'), check = $('#ht-check'), cap = $('#ht-cap'), seg = $('#ht-bit');
    var inv = new Uint8Array(256);
    checkMult(C, {
      chunk: 64,
      onRow: function (a, mem) {
        for (var j = 0; j < 8; j++) { var O = mem[C.o[j]]; for (var b = 0; b < 256; b++) if ((O[b >> 5] >>> (b & 31)) & 1) prod[a * 256 + b] |= 1 << j; }
      },
      done: function (bad, total, ms) {
        ready = true;
        for (var a = 1; a < 256; a++) for (var b = 1; b < 256; b++) if (prod[a * 256 + b] === 1) { inv[a] = b; break; }
        check.innerHTML = '<b>' + fmt(total - bad) + ' / ' + fmt(total) + '</b> products from the 112-gate circuit match long multiplication, checked in your browser just now (' + ms.toFixed(0) + ' ms).';
        if (bad) check.style.borderLeftColor = 'var(--st-contested)';
        paintOff(); draw();
      }
    });
    function paintOff() {
      var on = rgb(F0.css('--mk')), offc = rgb(F0.css('--bg-1')), img = octx.createImageData(256, 256), d = img.data;
      var bit = mode === 'inv' ? -1 : +mode;
      for (var i = 0; i < 65536; i++) {
        var lit = bit >= 0 ? (prod[i] >> bit) & 1 : 0, c = lit ? on : offc, k = i * 4;
        d[k] = c[0]; d[k + 1] = c[1]; d[k + 2] = c[2]; d[k + 3] = 255;
      }
      octx.putImageData(img, 0, 0);
    }
    function geom() { var s = Math.min(Cv.w, Cv.h); return { s: s, ox: (Cv.w - s) / 2, oy: (Cv.h - s) / 2, cell: s / 256 }; }
    function draw() {
      var g = geom();
      ctx.clearRect(0, 0, Cv.w, Cv.h);
      if (!ready) return;
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(off, g.ox, g.oy, g.s, g.s);
      if (mode === 'inv') {
        ctx.fillStyle = F0.css('--mk');
        var r = Math.max(1.6, g.cell * 0.9);
        for (var a = 1; a < 256; a++) { ctx.beginPath(); ctx.arc(g.ox + (inv[a] + 0.5) * g.cell, g.oy + (a + 0.5) * g.cell, r, 0, 6.2832); ctx.fill(); }
      }
      var m = hov || cur;
      if (m) {
        ctx.strokeStyle = F0.css('--ink'); ctx.lineWidth = 1; ctx.globalAlpha = 0.55;
        ctx.beginPath(); ctx.moveTo(g.ox, g.oy + (m.a + 0.5) * g.cell); ctx.lineTo(g.ox + g.s, g.oy + (m.a + 0.5) * g.cell);
        ctx.moveTo(g.ox + (m.b + 0.5) * g.cell, g.oy); ctx.lineTo(g.ox + (m.b + 0.5) * g.cell, g.oy + g.s); ctx.stroke();
        ctx.globalAlpha = 1; ctx.lineWidth = 2;
        var q = Math.max(6, g.cell * 3);
        ctx.strokeRect(g.ox + (m.b + 0.5) * g.cell - q / 2, g.oy + (m.a + 0.5) * g.cell - q / 2, q, q);
      }
    }
    function tipHTML(m) {
      var p = prod[m.a * 256 + m.b];
      return '<div class="tip-k">a = ' + hex2(m.a) + ' · b = ' + hex2(m.b) + '</div><div class="tip-t">a × b = ' + hex2(p) + '</div>' +
        '<div class="tip-rows"><div class="tip-row">a ' + bin(m.a, 8) + '</div><div class="tip-row">b ' + bin(m.b, 8) + '</div><div class="tip-row">= ' + bin(p, 8) + '</div></div>' +
        '<div class="tip-note">' + (mode === 'inv' ? (p === 1 ? 'b is a’s inverse.' : 'Not an inverse pair.') : 'Output bit ' + mode + ' is ' + ((p >> +mode) & 1) + '.') + '</div>';
    }
    function txt(m) { var p = prod[m.a * 256 + m.b]; return 'a = ' + hex2(m.a) + ' (' + bin(m.a, 8) + '), b = ' + hex2(m.b) + ' (' + bin(m.b, 8) + '): a × b = ' + hex2(p) + ' (' + bin(p, 8) + ').'; }
    function pick(ev) { var r = cv.getBoundingClientRect(), g = geom(); var b = Math.floor((ev.clientX - r.left - g.ox) / g.cell), a = Math.floor((ev.clientY - r.top - g.oy) / g.cell); return (a >= 0 && a < 256 && b >= 0 && b < 256) ? { a: a, b: b } : null; }
    cv.addEventListener('pointermove', function (ev) { if (!ready) return; hov = pick(ev); draw(); if (hov) F0.tip.show(tipHTML(hov), ev.clientX, ev.clientY); else F0.tip.hide(); });
    cv.addEventListener('pointerleave', function () { hov = null; F0.tip.hide(); draw(); });
    function showCur() { draw(); cap.textContent = txt(cur); var g = geom(), r = cv.getBoundingClientRect(); F0.tip.show(tipHTML(cur), r.left + g.ox + (cur.b + 0.5) * g.cell, r.top + g.oy + (cur.a + 0.5) * g.cell); }
    cv.addEventListener('focus', function () { if (!ready) return; if (!cur) cur = { a: 0x53, b: 0xCA }; showCur(); });
    cv.addEventListener('blur', function () { cur = null; F0.tip.hide(); draw(); });
    cv.addEventListener('keydown', function (e) {
      if (!cur) return; var a = cur.a, b = cur.b, st = e.shiftKey ? 16 : 1;
      if (e.key === 'ArrowUp') a -= st; else if (e.key === 'ArrowDown') a += st; else if (e.key === 'ArrowLeft') b -= st; else if (e.key === 'ArrowRight') b += st;
      else if (e.key === 'PageUp') a -= 16; else if (e.key === 'PageDown') a += 16; else return;
      e.preventDefault(); cur = { a: (a + 256) % 256, b: (b + 256) % 256 }; showCur();
    });
    seg.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return; mode = b.getAttribute('data-b'); setPressed(seg, 'data-b', mode);
      cap.textContent = mode === 'inv' ? 'The 255 pairs whose product is 1: every number except 0 has exactly one partner, its inverse, and the pattern is symmetric. The S-box starts from exactly this.'
        : 'Output bit ' + mode + ' of every product. The nested blocks at powers of 2 are long multiplication showing through; the fold scrambles the rest.';
      if (ready) { paintOff(); draw(); }
    });
    Cv.resize(draw); F0.onTheme(function () { if (ready) { paintOff(); draw(); } });
  })();

  /* =========================================================================
     01: GF(2^4) playground
     ========================================================================= */
  (function f4() {
    var svg = $('#f4-svg'); if (!svg) return;
    var J = decode(CIR.f4, 8);
    /* schoolbook: 16 ANDs, column sums (9 XORs), fold x^4 = x + 1 (6 XORs) */
    var S = (function () {
      var op = [], x = [], y = [], idx = {};
      function gate(o, a, b) { op.push(o); x.push(a); y.push(b); return 8 + op.length - 1; }
      for (var i = 0; i < 4; i++) for (var j = 0; j < 4; j++) idx[i + ',' + j] = gate(1, i, 4 + j);
      function P(i, j) { return idx[i + ',' + j]; }
      var p0 = P(0, 0), p1 = gate(0, P(0, 1), P(1, 0));
      var p2 = gate(0, gate(0, P(0, 2), P(1, 1)), P(2, 0));
      var p3 = gate(0, gate(0, P(0, 3), P(1, 2)), gate(0, P(2, 1), P(3, 0)));
      var p4 = gate(0, gate(0, P(1, 3), P(2, 2)), P(3, 1));
      var p5 = gate(0, P(2, 3), P(3, 2)), p6 = P(3, 3);
      var c0 = gate(0, p0, p4), c1 = gate(0, gate(0, p1, p5), p4), c2 = gate(0, gate(0, p5, p6), p2), c3 = gate(0, p3, p6);
      return decode({ g: op.map(function (o, k) { return (o ? '&' : '^') + x[k] + ',' + y[k]; }).join(';'), o: [c0, c1, c2, c3], m: 4, poly: 0x13 }, 8);
    })();
    var which = 'jain', A = 11, B = 6, reveal = 99, playing = false, acc = 0, lastT = 0, dims = { w: 600, h: 500 };
    var work = $('#f4-work'), tally = $('#f4-tally'), tab = $('#f4-tab'), allres = $('#f4-allres');
    function cir() { return which === 'jain' ? J : S; }
    /* bit buttons */
    function bits(host, get, set, name) {
      host.textContent = '';
      for (var i = 3; i >= 0; i--) (function (i) {
        var b = D.createElement('button'); b.type = 'button'; b.setAttribute('data-i', i);
        b.innerHTML = '<span class="bv"></span><span class="w">' + (i === 0 ? '1' : i === 1 ? 'x' : 'x' + (i === 2 ? '²' : '³')) + '</span>';
        b.addEventListener('click', function () { set(get() ^ (1 << i)); update(true); });
        host.appendChild(b);
      })(i);
      host._name = name;
    }
    function syncBits(host, v) { $$('button', host).forEach(function (b) { var i = +b.getAttribute('data-i'), on = (v >> i) & 1; b.setAttribute('aria-pressed', on ? 'true' : 'false'); b.querySelector('.bv').textContent = on; b.setAttribute('aria-label', host._name + ' bit for ' + (i === 0 ? '1' : i === 1 ? 'x' : 'x to the ' + i) + ': ' + on); }); }
    bits($('#f4-a'), function () { return A; }, function (v) { A = v; }, 'a');
    bits($('#f4-b'), function () { return B; }, function (v) { B = v; }, 'b');
    function poly(v) { var t = []; for (var i = 3; i >= 0; i--) if ((v >> i) & 1) t.push(i === 0 ? '1' : i === 1 ? 'x' : 'x' + (i === 2 ? '²' : '³')); return t.length ? t.join('+') : '0'; }
    /* table */
    (function () {
      var h = '<thead><tr><th scope="col"><span class="sr-only">a \\ b</span></th>';
      for (var b = 0; b < 16; b++) h += '<th scope="col">' + b.toString(16) + '</th>';
      h += '</tr></thead><tbody>';
      for (var a = 0; a < 16; a++) { h += '<tr><th scope="row">' + a.toString(16) + '</th>'; for (var b2 = 0; b2 < 16; b2++) h += '<td data-a="' + a + '" data-b="' + b2 + '">' + gmul(a, b2, 0x13, 4).toString(16) + '</td>'; h += '</tr>'; }
      tab.innerHTML = h + '</tbody>';
    })();
    tab.addEventListener('click', function (e) { var td = e.target.closest('td'); if (!td) return; A = +td.getAttribute('data-a'); B = +td.getAttribute('data-b'); update(true); });
    function workText() {
      var lines = [], full = 0, pad = function (s, n) { while (s.length < n) s = ' ' + s; return s; };
      lines.push(pad(bin(A, 4), 9) + '   a = ' + A + ' = ' + poly(A));
      lines.push('  × ' + pad(bin(B, 4), 5) + '   b = ' + B + ' = ' + poly(B));
      lines.push('  -------');
      for (var j = 0; j < 4; j++) {
        var on = (B >> j) & 1, row = on ? A : 0; full ^= row << j;
        var s = bin(row, 4) + new Array(j + 1).join(' ');
        lines.push(pad(s, 9) + '   <i>b' + j + '=' + on + (on ? (j ? ': a, shifted ' + j : ': a') : ': 0') + '</i>');
      }
      lines.push('  -------   <i>XOR each column</i>');
      lines.push(pad(bin(full, 7), 9) + '   = ' + full);
      var r = full;
      for (var k = 6; k >= 4; k--) if ((r >> k) & 1) {
        var sh = 0x13 << (k - 4);
        lines.push(pad('+' + bin(sh, k + 1), 9) + '   <i>fold x' + (k === 4 ? '⁴ = x+1' : k === 5 ? '⁵ = x²+x' : '⁶ = x³+x²') + '</i>');
        r ^= sh;
        lines.push(pad(bin(r, 7), 9));
      }
      lines.push(pad('<b>' + bin(r, 4) + '</b>', 16) + '   <b>a × b = ' + r + '</b>');
      return { html: lines.join('\n'), r: r };
    }
    /* circuit layout: bands of rows */
    function layout(c) {
      var rows = [], kind = function (g) { return c.op[g] === 1 ? 'and' : (c.x[g] < 8 && c.y[g] < 8 ? 'top' : 'bot'); };
      var top = [], and = [], bot = [];
      for (var g = 0; g < c.n; g++) { var k = kind(g); (k === 'top' ? top : k === 'and' ? and : bot).push(8 + g); }
      rows.push({ band: 'in', ids: [0, 1, 2, 3, 4, 5, 6, 7] });
      if (top.length) rows.push({ band: 'top', ids: top });
      for (var i = 0; i < and.length; i += 10) rows.push({ band: 'and', ids: and.slice(i, i + 10), cont: i > 0 });
      var byD = {}; bot.forEach(function (s) { (byD[c.dep[s]] = byD[c.dep[s]] || []).push(s); });
      var first = true;
      Object.keys(byD).sort(function (p, q) { return p - q; }).forEach(function (d) { var l = byD[d]; for (var i = 0; i < l.length; i += 8) { rows.push({ band: 'bot', ids: l.slice(i, i + 8), cont: !first }); first = false; } });
      rows.push({ band: 'out', ids: ['o0', 'o1', 'o2', 'o3'] });
      return { rows: rows, counts: [top.length, and.length, bot.length] };
    }
    var BANDTXT = { 'in': 'inputs a, b', top: 'prepare', and: 'multiply', bot: 'clean up', out: 'output a × b' };
    function draw() {
      var w = dims.w, h = dims.h, c = cir(), L = layout(c), sig = evalScalar(c, [A & 1, A >> 1 & 1, A >> 2 & 1, A >> 3 & 1, B & 1, B >> 1 & 1, B >> 2 & 1, B >> 3 & 1]);
      svg.textContent = ''; el('desc', { id: 'f4-desc' }, svg, '');
      var side = w >= 520, LW = side ? 104 : 0, labels = [];
      var top = side ? 22 : 30, bot = h - 18, nR = L.rows.length, gapY = (bot - top) / (nR - 1), pos = {};
      var r = Math.max(7, Math.min(11, gapY * 0.27, (w - LW - 20) / 12 * 0.32));
      L.rows.forEach(function (row, ri) {
        var n = row.ids.length, sp = Math.min(54, (w - LW - 24) / Math.max(n, 1)), x0 = LW + (w - LW) / 2 - sp * (n - 1) / 2, yy = top + ri * gapY;
        row.ids.forEach(function (id, k) { pos[id] = { x: x0 + k * sp, y: yy }; });
        if (!row.cont) {
          var cnt = row.band === 'top' ? L.counts[0] + ' XOR' : row.band === 'and' ? L.counts[1] + ' AND' : row.band === 'bot' ? L.counts[2] + ' XOR' : '';
          labels.push({ t: BANDTXT[row.band], n: cnt, y: yy });
        }
      });
      var gW = el('g', {}, svg), gN = el('g', {}, svg);
      function known(s) { return s < 8 || c.dep[s] <= reveal; }
      function wire(s, t) {
        var p = pos[s], q = pos[t]; if (!p || !q) return;
        var v = known(s) ? sig[s] : 0;
        el('path', { 'class': 'f4-w v' + v, d: 'M' + p.x.toFixed(1) + ',' + (p.y + r).toFixed(1) + 'C' + p.x.toFixed(1) + ',' + ((p.y + q.y) / 2).toFixed(1) + ' ' + q.x.toFixed(1) + ',' + ((p.y + q.y) / 2).toFixed(1) + ' ' + q.x.toFixed(1) + ',' + (q.y - r).toFixed(1) }, gW);
      }
      for (var g = 0; g < c.n; g++) { wire(c.x[g], 8 + g); wire(c.y[g], 8 + g); }
      c.o.forEach(function (s, i) { wire(s, 'o' + i); });
      function node(id, kindC, v, label, tip) {
        var p = pos[id], gg = el('g', { 'class': 'f4-g ' + kindC + (v == null ? ' unk' : ' v' + v) }, gN);
        if (kindC === 'and') el('rect', { 'class': 'sh', x: p.x - r, y: p.y - r, width: 2 * r, height: 2 * r, rx: 2.5 }, gg);
        else el('circle', { 'class': 'sh', cx: p.x, cy: p.y, r: kindC === 'io' ? r * 1.1 : r }, gg);
        if (kindC === 'xor') el('path', { 'class': 'pl', d: 'M' + (p.x - r * 0.55) + ',' + p.y + 'h' + r * 1.1 + 'M' + p.x + ',' + (p.y - r * 0.55) + 'v' + r * 1.1 }, gg);
        if (label) el('text', { x: p.x, y: p.y + 3.5 }, gg, label);
        if (tip) { gg.addEventListener('pointermove', function (ev) { F0.tip.show(tip, ev.clientX, ev.clientY); }); gg.addEventListener('pointerleave', function () { F0.tip.hide(); }); }
      }
      for (var i = 0; i < 8; i++) node(i, 'io', sig[i], (i < 4 ? 'a' : 'b') + (i % 4));
      for (var g2 = 0; g2 < c.n; g2++) {
        var s = 8 + g2, kn = known(s), kindC = c.op[g2] === 1 ? 'and' : 'xor';
        node(s, kindC, kn ? sig[s] : null, '', '<div class="tip-k">Gate ' + (g2 + 1) + ' · ' + (kindC === 'and' ? 'AND' : 'XOR') + ' · depth ' + c.dep[s] + '</div><div class="tip-t">' + nm(c.x[g2]) + (kindC === 'and' ? ' AND ' : ' XOR ') + nm(c.y[g2]) + ' = ' + sig[s] + '</div>');
      }
      c.o.forEach(function (s2, k) { node('o' + k, 'io', known(s2) ? sig[s2] : null, 'c' + k); });
      var gL = el('g', { 'aria-hidden': 'true' }, svg);
      labels.forEach(function (lb) {
        if (side) {
          var t = el('text', { 'class': 'f4-band', x: 4, y: lb.n ? lb.y - 2 : lb.y + 4 }, gL, lb.t);
          if (lb.n) el('tspan', { 'class': 'n', x: 4, dy: 14 }, t, lb.n);
        } else {
          var t2 = el('text', { 'class': 'f4-band', x: 4, y: lb.y - r - 8 }, gL, lb.t + (lb.n ? ' · ' : ''));
          if (lb.n) el('tspan', { 'class': 'n' }, t2, lb.n);
        }
      });
      $('#f4-desc', svg).textContent = (which === 'jain' ? "Jain's 30-gate circuit" : 'The schoolbook 31-gate circuit') + ' computing ' + A + ' × ' + B + '. Output bits c3 c2 c1 c0 = ' + c.o.slice().reverse().map(function (s3) { return sig[s3]; }).join(' ') + '.';
      return sig;
    }
    function nm(s) { return s < 8 ? (s < 4 ? 'a' : 'b') + (s % 4) : 'gate ' + (s - 7); }
    function update(animate) {
      syncBits($('#f4-a'), A); syncBits($('#f4-b'), B);
      $('#f4-av').textContent = A + ' = ' + bin(A, 4); $('#f4-bv').textContent = B + ' = ' + bin(B, 4);
      var wt = workText(); work.innerHTML = wt.html;
      $$('td', tab).forEach(function (td) { var a = +td.getAttribute('data-a'), b = +td.getAttribute('data-b'); td.className = (a === A && b === B ? 'sel' : a === A ? 'row' : b === B ? 'col' : '') + (td.classList.contains('ok') ? ' ok' : ''); });
      if (animate && F0.motion()) { reveal = 0; acc = 0; lastT = 0; playing = true; loop.start(); } else reveal = 99;
      var sig = draw(), c = cir(), out = 0; c.o.forEach(function (s, i) { out |= sig[s] << i; });
      var L = layout(c);
      tally.innerHTML = '<div><p class="k">Gates</p><p class="v">' + (L.counts[0] ? L.counts[0] + ' + ' : '0 + ') + L.counts[1] + ' + ' + L.counts[2] + ' = ' + c.n + '</p></div>' +
        '<div><p class="k">AND gates</p><p class="v">' + c.ands + ' <small>· depth ' + c.depth + '</small></p></div>' +
        '<div><p class="k">Circuit says</p><p class="v">' + bin(out, 4) + ' = ' + out + ' <small>' + (out === wt.r ? '✓ matches' : '✗ mismatch') + '</small></p></div>';
    }
    var loop = F0.loop(function (t) {
      if (!lastT) lastT = t; acc += t - lastT; lastT = t;
      if (acc >= 170) { acc = 0; reveal++; draw(); if (reveal > 6) { playing = false; loop.stop(); reveal = 99; } }
    });
    $('#f4-which').addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return; which = b.getAttribute('data-c'); setPressed($('#f4-which'), 'data-c', which);
      $$('td', tab).forEach(function (td) { td.classList.remove('ok', 'bad'); }); allres.textContent = '';
      update(true);
    });
    $('#f4-all').addEventListener('click', function () {
      var c = cir(), ok = 0, t0 = now();
      $$('td', tab).forEach(function (td) {
        var a = +td.getAttribute('data-a'), b = +td.getAttribute('data-b');
        var s = evalScalar(c, [a & 1, a >> 1 & 1, a >> 2 & 1, a >> 3 & 1, b & 1, b >> 1 & 1, b >> 2 & 1, b >> 3 & 1]), o = 0;
        c.o.forEach(function (q, i) { o |= s[q] << i; });
        var good = o === gmul(a, b, 0x13, 4); if (good) ok++;
        td.classList.toggle('ok', good); td.classList.toggle('bad', !good);
      });
      allres.textContent = ok + ' / 256 pairs correct (' + (now() - t0).toFixed(1) + ' ms)' + (which === 'jain' ? '. Lean proved the same in about 1 s.' : '.');
    });
    fitSvg(svg, function (w, h) { dims = { w: w, h: h }; draw(); });
    F0.whenVisible(svg, null, function () { if (playing) { loop.stop(); playing = false; reveal = 99; draw(); } });
    update(false);
  })();

  /* =========================================================================
     02: the size-speed staircase
     ========================================================================= */
  (function stair() {
    var svg = $('#st-svg'); if (!svg) return;
    var PTS = [
      { g: 117, d: 6, and: 48, L: [8, 48, 61], who: 'CMT 2010 record', k: 'rec', file: 'Circuit Minimization Team, July 2010' },
      { g: 112, d: 6, and: 36, L: [20, 36, 56], who: 'Jain 2026', k: 'par', file: 'aes112_d6.slp' },
      { g: 110, d: 7, and: 36, L: [20, 36, 54], who: 'Jain 2026', k: 'par', file: 'aes110_d7.slp' },
      { g: 108, d: 12, and: 34, L: [24, 34, 50], who: 'Jain 2026', k: 'par', file: 'aes108_d12.slp' },
      { g: 107, d: 13, and: 35, L: [22, 35, 50], who: 'Jain 2026', k: 'par', file: 'aes107_d13.slp' },
      { g: 115, d: 15, and: 48, who: 'Jain 2026 (search step)', k: 'lad' }, { g: 114, d: 9, and: 43, who: 'Jain 2026 (search step)', k: 'lad' },
      { g: 113, d: 15, and: 43, who: 'Jain 2026 (search step)', k: 'lad' }, { g: 112, d: 14, and: 43, who: 'Jain 2026 (search step)', k: 'lad' },
      { g: 110, d: 20, and: 32, who: 'Jain 2026 (search step)', k: 'lad' }, { g: 109, d: 18, and: 33, who: 'Jain 2026 (search step)', k: 'lad' },
      { g: 108, d: 19, and: 34, who: 'Jain 2026 (search step)', k: 'lad' }, { g: 107, d: 19, and: 35, who: 'Jain 2026 (search step)', k: 'lad' },
      { g: 107, d: 18, and: 36, who: 'Jain 2026 (search step)', k: 'lad' }
    ];
    var range = $('#st-range'), out = $('#st-out'), layers = $('#st-layers'), dims = { w: 500, h: 400 };
    function best(D2) { var c = PTS.filter(function (p) { return p.d <= D2; }); c.sort(function (p, q) { return p.g - q.g || p.d - q.d || (p.k === 'rec') - (q.k === 'rec'); }); return c[0] || null; }
    function tip(p) { return '<div class="tip-k">' + F0.esc(p.who) + '</div><div class="tip-t">' + p.g + ' gates · depth ' + p.d + '</div><div class="tip-rows"><div class="tip-row">' + p.and + ' AND + ' + (p.g - p.and) + ' XOR</div>' + (p.L ? '<div class="tip-row">layers ' + p.L.join(' / ') + '</div>' : '') + '</div>' + (p.file ? '<div class="tip-foot">' + F0.esc(p.file) + '</div>' : ''); }
    function draw(w, h) {
      dims = { w: w, h: h }; svg.textContent = ''; el('desc', { id: 'st-desc' }, svg, '');
      var D2 = +range.value, b = best(D2), ml = 40, mr = 12, mt = 30, mb = 36, pw = w - ml - mr, ph = h - mt - mb;
      var X = function (d) { return ml + (d - 4) / 17 * pw; }, Y = function (g) { return mt + (131 - g) / 27 * ph; };
      var root = el('g', { 'class': 'gf-chart' }, svg);
      el('rect', { 'class': 'budget', x: X(D2 + 0.5), y: mt, width: Math.max(0, ml + pw - X(D2 + 0.5)), height: ph }, root);
      for (var gg = 105; gg <= 130; gg += 5) { el('line', { 'class': 'grid', x1: ml, x2: ml + pw, y1: Y(gg), y2: Y(gg) }, root); el('text', { 'class': 'gf-svg-t', x: ml - 6, y: Y(gg) + 4, 'text-anchor': 'end' }, root, String(gg)); }
      for (var dd = 5; dd <= 20; dd += 5) { el('line', { 'class': 'grid', x1: X(dd), x2: X(dd), y1: mt, y2: mt + ph }, root); el('text', { 'class': 'gf-svg-t', x: X(dd), y: mt + ph + 15, 'text-anchor': 'middle' }, root, String(dd)); }
      el('text', { 'class': 'gf-svg-t ink', x: ml + pw, y: mt + ph + 31, 'text-anchor': 'end' }, root, 'depth (gates in a row) →');
      el('text', { 'class': 'gf-svg-t strong', x: 4, y: 14 }, root, 'gates ↑');
      el('text', { 'class': 'gf-svg-t', x: ml + pw - 4, y: 14, 'text-anchor': 'end' }, root, w < 420 ? '↑ schoolbook: 141' : '↑ off the top: schoolbook + simple fold, 141');
      el('line', { 'class': 'ref', x1: ml, x2: ml + pw, y1: Y(128), y2: Y(128) }, root);
      el('text', { 'class': 'gf-svg-t', x: ml + pw - 4, y: Y(128) - 5, 'text-anchor': 'end' }, root, w < 420 ? 'product circuit + fold: 128' : 'published product circuit + simple fold: 128');
      var par = PTS.filter(function (p) { return p.k === 'par'; }), d = '';
      par.forEach(function (p, i) { d += (i ? 'H' + X(p.d).toFixed(1) + 'V' : 'M' + X(p.d).toFixed(1) + ',') + Y(p.g).toFixed(1); });
      d += 'H' + X(21).toFixed(1);
      el('path', { 'class': 'stair', d: d }, root);
      PTS.slice().sort(function (p, q) { return (p.k === 'lad' ? 0 : 1) - (q.k === 'lad' ? 0 : 1); }).forEach(function (p) {
        var g = el('g', { 'class': 'pt', tabindex: 0, role: 'img', 'aria-label': p.who + ': ' + p.g + ' gates at depth ' + p.d + ', ' + p.and + ' AND gates' }, root);
        el('circle', { 'class': 'hit', cx: X(p.d), cy: Y(p.g), r: 12 }, g);
        if (p.k === 'rec') el('circle', { cx: X(p.d), cy: Y(p.g), r: 5.5, fill: 'var(--bg-1)', stroke: 'var(--ink)', 'stroke-width': 2 }, g);
        else el('circle', { cx: X(p.d), cy: Y(p.g), r: p.k === 'par' ? 5.5 : 4, fill: p.k === 'par' ? 'var(--mk)' : 'var(--mark-mid)', stroke: 'var(--bg-1)', 'stroke-width': 2 }, g);
        g.addEventListener('pointermove', function (ev) { F0.tip.show(tip(p), ev.clientX, ev.clientY); });
        g.addEventListener('pointerleave', function () { F0.tip.hide(); });
        g.addEventListener('focus', function () { tipAt(tip(p), g); });
        g.addEventListener('blur', function () { F0.tip.hide(); });
      });
      el('text', { 'class': 'gf-svg-t strong', x: X(6) + 9, y: Y(117) + 4 }, root, '117 · 2010');
      el('text', { 'class': 'gf-svg-t strong', x: w < 480 ? X(6) + 2 : X(6) - 15, y: w < 480 ? Y(112) + 22 : Y(112) + 4, 'text-anchor': w < 480 ? 'middle' : 'end' }, root, '112');
      el('text', { 'class': 'gf-svg-t strong', x: X(13) + 9, y: Y(107) + 13 }, root, '107');
      if (b) el('circle', { 'class': 'ring', cx: X(b.d), cy: Y(b.g), r: 10 }, root);
      $('#st-desc', svg).textContent = 'Gates against depth for AES-field multipliers. With depth at most ' + D2 + ', the smallest is ' + (b ? b.g + ' gates (' + b.who + ', depth ' + b.d + ')' : 'none') + '.';
      renderLayers(b, D2);
    }
    function bar(p) {
      if (p.L) { var t = p.g; return '<span class="st-bar">' + (p.L[0] ? '<i class="x1" style="width:' + (100 * p.L[0] / t) + '%">' + p.L[0] + '</i>' : '') + '<i class="an" style="width:' + (100 * p.L[1] / t) + '%">' + p.L[1] + '</i><i class="x2" style="width:' + (100 * p.L[2] / t) + '%">' + p.L[2] + '</i></span>'; }
      return '<span class="st-bar"><i class="an" style="width:' + (100 * p.and / p.g) + '%">' + p.and + '</i><i class="x2" style="width:' + (100 * (p.g - p.and) / p.g) + '%">' + (p.g - p.and) + '</i></span>';
    }
    function renderLayers(b, D2) {
      out.textContent = D2;
      range.setAttribute('aria-valuetext', 'depth at most ' + D2 + ': ' + (b ? 'smallest is ' + b.g + ' gates' : 'no circuit found'));
      if (!b) { layers.innerHTML = '<p class="st-note"><b>Nothing fits at depth 5.</b> The 2010 record needs depth 6, and the preprint reports nothing below 117 gates at depth 5.</p>'; return; }
      var rec = PTS[0], rows = [b]; if (b !== rec) rows.push(rec);
      layers.innerHTML = rows.map(function (p) { return '<div class="st-row"><span><b>' + (p.k === 'rec' ? '2010 record' : 'Jain 2026') + '</b>, depth ' + p.d + '</span>' + bar(p) + '<span class="st-tot">' + p.g + '</span></div>'; }).join('') +
        '<p class="st-key"><span><i style="background:var(--mark-mid)"></i>XOR: prepare / clean up</span><span><i style="background:var(--mk)"></i>AND: multiply</span></p>' +
        (b.L ? '' : '<p class="st-note">For this step of the search only the AND count is published, so its XORs are shown as one block.</p>') +
        (b !== rec ? '<p class="st-note">' + (rec.g - b.g) + ' gates fewer than the 2010 record' + (b.d > rec.d ? ', at ' + (b.d / rec.d).toFixed(1).replace('.0', '') + ' times its depth.' : ', at the same depth.') + '</p>' : '');
    }
    (function table() {
      var rows = PTS.slice().sort(function (p, q) { return p.d - q.d || p.g - q.g; }).map(function (p) { return '<tr><td>' + F0.esc(p.who) + '</td><td class="n">' + p.g + '</td><td class="n">' + p.d + '</td><td class="n">' + p.and + '</td><td class="n">' + (p.L ? p.L.join(' / ') : '') + '</td></tr>'; }).join('');
      $('#st-table').innerHTML = '<table class="tbl"><caption>AES-field multipliers (x<sup>8</sup>+x<sup>4</sup>+x<sup>3</sup>+x+1)</caption><thead><tr><th scope="col">Circuit</th><th scope="col" class="n">Gates</th><th scope="col" class="n">Depth</th><th scope="col" class="n">AND</th><th scope="col" class="n">Prepare / multiply / clean up</th></tr></thead><tbody>' + rows +
        '<tr><td>Schoolbook + simple fold (reference)</td><td class="n">141</td><td class="n">11</td><td class="n">64</td><td class="n">0 / 64 / 77</td></tr><tr><td>Published product circuit + simple fold (reference)</td><td class="n">128</td><td class="n"></td><td class="n"></td><td class="n">100 + 28 fold</td></tr></tbody></table>';
    })();
    range.addEventListener('input', function () { draw(dims.w, dims.h); });
    fitSvg(svg, draw);
  })();

  /* =========================================================================
     03: the S-box, live
     ========================================================================= */
  (function sbox() {
    var svg = $('#sb-svg'); if (!svg) return;
    var CS = { s106: decode(CIR.s106, 8), s121: decode(CIR.s121, 8), i109: decode(CIR.i109, 8) };
    var SB = [], ISB = [];
    (function tables() {
      var inv = [0]; for (var x = 1; x < 256; x++) for (var y = 1; y < 256; y++) if (gmul(x, y, 0x11B, 8) === 1) { inv.push(y); break; }
      for (var i = 0; i < 256; i++) { var v = inv[i], s = 0; for (var b = 0; b < 8; b++) { var bit = ((v >> b) ^ (v >> ((b + 4) % 8)) ^ (v >> ((b + 5) % 8)) ^ (v >> ((b + 6) % 8)) ^ (v >> ((b + 7) % 8)) ^ (0x63 >> b)) & 1; s |= bit << b; } SB.push(s); }
      for (var j = 0; j < 256; j++) ISB[SB[j]] = j;
    })();
    var which = 's106', X = 0x53, reveal = 99, playing = false, acc = 0, lastT = 0, dims = { w: 900, h: 340 }, checked = false;
    var input = $('#sb-in'), res = $('#sb-res'), tab = $('#sb-tab'), allres = $('#sb-allres');
    function C() { return CS[which]; }
    function T() { return which === 'i109' ? ISB : SB; }
    function run(c, x) { var ins = []; for (var j = 0; j < 8; j++) ins.push((x >> (7 - j)) & 1); var s = evalScalar(c, ins), o = 0; c.o.forEach(function (q, j) { o |= s[q] << (7 - j); }); return { s: s, o: o }; }
    function draw() {
      var w = dims.w, h = dims.h, c = C(), r = run(c, X), cols = c.depth + 2, byD = [];
      svg.textContent = ''; el('desc', { id: 'sb-desc' }, svg, '');
      for (var g = 0; g < c.n; g++) { var d = c.dep[8 + g]; (byD[d] = byD[d] || []).push(8 + g); }
      var maxPer = 8; byD.forEach(function (l) { if (l) maxPer = Math.max(maxPer, l.length); });
      var vert = w < 560, ml = 6, mr = 6, mt = 20, mb = 8;
      svg.parentNode.classList.toggle('vert', vert);
      var colW = vert ? (h - mt - mb) / cols : (w - ml - mr) / cols, rowH = vert ? (w - ml - mr) / maxPer : (h - mt - mb) / maxPer;
      var sz = Math.max(3, Math.min(colW * 0.62, rowH * 0.72, 16));
      var P = {}, gW = el('g', { 'class': 'sb-wires', 'aria-hidden': 'true' }, svg), wIn = {}, wOut = {};
      function cell(px, py, kind, v, tipHtml, key) {
        var cx = vert ? py : px, cy = vert ? px : py, hw = vert ? rowH : colW, hh = vert ? colW : rowH;
        if (key != null) P[key] = { x: cx, y: cy };
        var g2 = el('g', {}, svg), cl = 'sb-c ' + kind + (v == null ? ' unk' : ' v' + v);
        if (kind === 'and') el('rect', { 'class': cl, x: cx - sz / 2, y: cy - sz / 2, width: sz, height: sz, rx: 1.5 }, g2);
        else el('circle', { 'class': cl, cx: cx, cy: cy, r: sz / 2 }, g2);
        if (kind === 'xnor' && sz >= 6) el('circle', { 'class': 'sb-xn', cx: cx, cy: cy, r: sz * 0.22, style: v === 1 ? 'stroke:var(--bg)' : '' }, g2);
        if (tipHtml) {
          el('rect', { 'class': 'sb-hit', x: cx - hw / 2, y: cy - hh / 2, width: hw, height: hh }, g2);
          g2.addEventListener('pointermove', function (ev) { F0.tip.show(tipHtml(), ev.clientX, ev.clientY); });
          g2.addEventListener('pointerenter', function () { hl(key, true); });
          g2.addEventListener('pointerleave', function () { F0.tip.hide(); hl(key, false); });
        }
      }
      function hl(key, on) {
        (wIn[key] || []).forEach(function (pth) { pth.classList.toggle('hi-in', on); });
        (wOut[key] || []).forEach(function (pth) { pth.classList.toggle('hi-out', on); });
      }
      function wire(from, to, v) {
        var a = P[from], b = P[to]; if (!a || !b) return;
        var d;
        if (vert) { var my = (a.y + b.y) / 2; d = 'M' + a.x.toFixed(1) + ',' + (a.y + sz / 2).toFixed(1) + 'C' + a.x.toFixed(1) + ',' + my.toFixed(1) + ' ' + b.x.toFixed(1) + ',' + my.toFixed(1) + ' ' + b.x.toFixed(1) + ',' + (b.y - sz / 2).toFixed(1); }
        else { var mx = (a.x + b.x) / 2; d = 'M' + (a.x + sz / 2).toFixed(1) + ',' + a.y.toFixed(1) + 'C' + mx.toFixed(1) + ',' + a.y.toFixed(1) + ' ' + mx.toFixed(1) + ',' + b.y.toFixed(1) + ' ' + (b.x - sz / 2).toFixed(1) + ',' + b.y.toFixed(1); }
        var pth = el('path', { 'class': 'sb-w' + (v === 1 ? ' v1' : ''), d: d }, gW);
        (wIn[to] = wIn[to] || []).push(pth); (wOut[from] = wOut[from] || []).push(pth);
      }
      var X0 = function (col) { return (vert ? mt : ml) + (col + 0.5) * colW; }, Yy = function (k, n) { return (vert ? w / 2 : mt + (h - mt - mb) / 2) + (k - (n - 1) / 2) * rowH; };
      for (var j = 0; j < 8; j++) (function (j) { cell(X0(0), Yy(j, 8), 'io', r.s[j], function () { return '<div class="tip-k">Input bit U' + j + '</div><div class="tip-t">' + r.s[j] + '</div>'; }, j); })(j);
      for (var dd = 1; dd <= c.depth; dd++) (byD[dd] || []).forEach(function (s, k, arr) {
        var gi = s - 8, kind = c.op[gi] === 1 ? 'and' : c.op[gi] === 2 ? 'xnor' : 'xor', kn = dd <= reveal;
        cell(X0(dd), Yy(k, arr.length), kind, kn ? r.s[s] : null, function () { return '<div class="tip-k">Gate ' + (gi + 1) + ' · ' + kind.toUpperCase() + ' · depth ' + c.dep[s] + '</div><div class="tip-t">output ' + r.s[s] + '</div><div class="tip-note">inputs: ' + sname(c.x[gi]) + ' and ' + sname(c.y[gi]) + '</div>'; }, s);
      });
      var done = reveal >= c.depth;
      for (var o = 0; o < 8; o++) (function (o) { var s = c.o[o]; cell(X0(cols - 1), Yy(o, 8), 'io', done ? r.s[s] : null, function () { return '<div class="tip-k">Output bit S' + o + '</div><div class="tip-t">' + r.s[s] + '</div>'; }, 'o' + o); })(o);
      for (var gw = 0; gw < c.n; gw++) { var sg = 8 + gw, kw = c.dep[sg] <= reveal; wire(c.x[gw], sg, kw ? r.s[c.x[gw]] : 0); wire(c.y[gw], sg, kw ? r.s[c.y[gw]] : 0); }
      for (var ow = 0; ow < 8; ow++) wire(c.o[ow], 'o' + ow, done ? r.s[c.o[ow]] : 0);
      if (vert) {
        el('text', { 'class': 'gf-svg-t', x: 4, y: X0(0) + 4 }, svg, 'in');
        el('text', { 'class': 'gf-svg-t', x: 4, y: X0(cols - 1) + 4 }, svg, 'out');
      } else {
        el('text', { 'class': 'gf-svg-t', x: X0(0), y: 12, 'text-anchor': 'middle' }, svg, 'in');
        el('text', { 'class': 'gf-svg-t', x: X0(cols - 1), y: 12, 'text-anchor': 'middle' }, svg, 'out');
      }
      if (!vert) el('text', { 'class': 'gf-svg-t', x: (X0(1) + X0(c.depth)) / 2, y: 12, 'text-anchor': 'middle' }, svg, 'depth 1 → ' + c.depth + ' · ' + c.n + ' gates (' + c.ands + ' AND)');
      else el('text', { 'class': 'gf-svg-t', x: w - 4, y: 12, 'text-anchor': 'end' }, svg, 'depth ↓ · ' + c.n + ' gates (' + c.ands + ' AND)');
      $('#sb-desc', svg).textContent = c.n + '-gate circuit, depth ' + c.depth + ', evaluating input ' + hex2(X) + '; output ' + hex2(r.o) + '.';
      return r;
    }
    function sname(s) { return s < 8 ? 'input U' + s : 'gate ' + (s - 7); }
    function result(r) {
      var t = T()[X], ok = r.o === t, inv = which === 'i109';
      res.classList.toggle('bad', !ok);
      res.innerHTML = '<span>' + (inv ? 'S<sup>−1</sup>' : 'S') + '(' + hex2(X) + ') =</span><span class="big">' + hex2(r.o) + '</span><span class="bits">' + bin(r.o, 8) + '</span><span>' + (ok ? '✓ matches the standard&rsquo;s ' + (inv ? 'inverse ' : '') + 'table' : '✗ table says ' + hex2(t)) + '</span>';
    }
    function buildTable() {
      var t = T(), h = '<thead><tr><th scope="col"><span class="sr-only">first digit</span></th>';
      for (var c = 0; c < 16; c++) h += '<th scope="col">' + c.toString(16).toUpperCase() + '</th>';
      h += '</tr></thead><tbody>';
      for (var r = 0; r < 16; r++) { h += '<tr><th scope="row">' + r.toString(16).toUpperCase() + '</th>'; for (var c2 = 0; c2 < 16; c2++) { var x = r * 16 + c2; h += '<td data-x="' + x + '">' + hex2(t[x]) + '</td>'; } h += '</tr>'; }
      var cap = $('#sb-cap'), keep = cap ? cap.outerHTML : '';
      tab.innerHTML = keep + h + '</tbody>';
      $('#sb-cap').textContent = which === 'i109' ? 'The inverse AES S-box, computed here as the inverse of the forward table: row = first hex digit of the input, column = second' : 'The AES S-box (FIPS-197), computed here from field inversion and the affine map: row = first hex digit of the input, column = second';
    }
    function mark() { $$('td', tab).forEach(function (td) { td.classList.toggle('sel', +td.getAttribute('data-x') === X); td.classList.toggle('chk', checked); }); }
    function update(animate) {
      input.value = hex2(X);
      if (animate && F0.motion()) { reveal = 0; acc = 0; lastT = 0; playing = true; loop.start(); } else reveal = 99;
      var r = draw(); result(r); mark();
    }
    var loop = F0.loop(function (t) {
      if (!lastT) lastT = t; acc += t - lastT; lastT = t;
      if (acc >= 45) { acc = 0; reveal++; draw(); if (reveal > C().depth) { playing = false; loop.stop(); reveal = 99; draw(); } }
    });
    input.addEventListener('input', function () { var v = input.value.trim(); if (/^[0-9a-f]{1,2}$/i.test(v)) { X = parseInt(v, 16); var r = (reveal = 99, draw()); result(r); mark(); } });
    input.addEventListener('keydown', function (e) { if (e.key === 'ArrowUp') { e.preventDefault(); X = (X + 1) % 256; update(true); } else if (e.key === 'ArrowDown') { e.preventDefault(); X = (X + 255) % 256; update(true); } });
    input.addEventListener('blur', function () { input.value = hex2(X); });
    $('#sb-inc').addEventListener('click', function () { X = (X + 1) % 256; update(true); });
    $('#sb-dec').addEventListener('click', function () { X = (X + 255) % 256; update(true); });
    tab.addEventListener('click', function (e) { var td = e.target.closest('td'); if (!td) return; X = +td.getAttribute('data-x'); update(true); });
    $('#sb-which').addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return; which = b.getAttribute('data-c'); setPressed($('#sb-which'), 'data-c', which);
      checked = false; allres.innerHTML = 'Not run yet for this circuit.'; buildTable(); update(true);
    });
    $('#sb-all').addEventListener('click', function () {
      var c = C(), t = T(), t0 = now(), W = 8, mem = [], i, w;
      for (i = 0; i < 8 + c.n; i++) mem.push(new Uint32Array(W));
      for (var j = 0; j < 8; j++) for (var x = 0; x < 256; x++) if ((x >> (7 - j)) & 1) mem[j][x >> 5] |= (1 << (x & 31)) >>> 0;
      for (var g = 0; g < c.n; g++) { var Dd = mem[8 + g], A = mem[c.x[g]], B = mem[c.y[g]], op = c.op[g]; for (w = 0; w < W; w++) Dd[w] = op === 1 ? (A[w] & B[w]) : op === 2 ? ~(A[w] ^ B[w]) : (A[w] ^ B[w]); }
      var ok = 0, bad = [];
      for (var x2 = 0; x2 < 256; x2++) { var o = 0; for (var k = 0; k < 8; k++) o |= ((mem[c.o[k]][x2 >> 5] >>> (x2 & 31)) & 1) << (7 - k); if (o === t[x2]) ok++; else bad.push(x2); }
      var ms = now() - t0; checked = true; mark();
      bad.forEach(function (x3) { var td = tab.querySelector('td[data-x="' + x3 + '"]'); if (td) td.classList.add('badc'); });
      allres.innerHTML = '<b>' + ok + ' / 256</b> inputs give exactly the standard&rsquo;s ' + (which === 'i109' ? 'inverse ' : '') + 'table (' + (ms < 1 ? ms.toFixed(2) : ms.toFixed(1)) + ' ms in your browser, all 256 at once). The repository&rsquo;s Lean proof of the same fact takes 8 to 9 seconds.';
    });
    /* comparison dot plot */
    (function cmp() {
      var s = $('#sbc-svg'); if (!s) return;
      var lastW = 0;
      function go() { var cw = Math.round(s.getBoundingClientRect().width) || 380; if (cw === lastW) return; lastW = cw; s.textContent = ''; el('desc', { id: 'sbc-d' }, s, 'Gate counts: Boyar–Peralta / Calik 113 at depth 27; NIST 2026 110 at depth 22; Jain 2026 106 at depth 24; NIST’s stated wish is 105 or fewer.'); paint(Math.max(280, cw)); }
      if ('ResizeObserver' in window) new ResizeObserver(go).observe(s.parentNode); go();
      function paint(W) {
      var H = 118, ml = W < 340 ? 128 : 150, mr = 62, X1 = function (g) { return ml + (g - 100) / 16 * (W - ml - mr); };
      s.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
      var root = el('g', { 'class': 'gf-chart' }, s);
      [100, 104, 108, 112, 116].forEach(function (g) { el('line', { 'class': 'grid', x1: X1(g), x2: X1(g), y1: 6, y2: H - 22 }, root); el('text', { 'class': 'gf-svg-t', x: X1(g), y: H - 8, 'text-anchor': 'middle' }, root, String(g)); });
      el('line', { x1: X1(105), x2: X1(105), y1: 2, y2: H - 22, stroke: 'var(--ink-2)', 'stroke-width': 1 }, root);
      el('text', { 'class': 'gf-svg-t ink', x: X1(105) - 4, y: 12, 'text-anchor': 'end' }, root, 'NIST wish ≤ 105');
      [['Boyar–Peralta/Calik', 113, 27, 0], ['NIST 2026', 110, 22, 0], ['Jain 2026', 106, 24, 1]].forEach(function (r, i) {
        var y = 32 + i * 24;
        el('text', { 'class': 'gf-svg-t' + (r[3] ? ' strong' : ' ink'), x: ml - 8, y: y + 4, 'text-anchor': 'end' }, root, r[0]);
        el('line', { 'class': 'grid', x1: ml, x2: X1(r[1]), y1: y, y2: y }, root);
        el('circle', { cx: X1(r[1]), cy: y, r: 5, fill: r[3] ? 'var(--mk)' : 'var(--mark-mid)', stroke: 'var(--bg-1)', 'stroke-width': 2 }, root);
        el('text', { 'class': 'gf-svg-t' + (r[3] ? ' strong' : ''), x: X1(r[1]) + 9, y: y + 4 }, root, r[1] + ' · d' + r[2]);
      });
      }
    })();
    fitSvg(svg, function (w, h) { dims = { w: w, h: h }; draw(); });
    F0.whenVisible(svg, null, function () { if (playing) { loop.stop(); playing = false; reveal = 99; draw(); } });
    buildTable(); update(false);
  })();

  /* =========================================================================
     04: Aska's multipliers
     ========================================================================= */
  (function aska() {
    var svg = $('#ak-svg'); if (!svg) return;
    var ROWS = [
      { f: 'GF(2⁴)', base: 31, c: 30, by: 'Jain' }, { f: 'GF(2⁵)', base: 49, c: 44, by: 'Jain' },
      { f: 'GF(2⁹)', base: 142, c: 136, by: 'Aska' }, { f: 'GF(2¹⁰)', base: 172, c: 172, by: 'Aska' }, { f: 'GF(2¹¹)', base: 206, c: 199, by: 'Aska' },
      { f: 'GF(2¹²)', base: 229, c: 210, by: 'Jain' }, { f: 'GF(2¹³)', base: 303, c: 283, by: 'Jain' }
    ];
    function draw(w, h) {
      svg.textContent = ''; el('desc', { id: 'ak-desc' }, svg, 'Gates saved against a simple baseline: ' + ROWS.map(function (r) { return r.f + ' ' + (r.base - r.c) + ' of ' + r.base + ' (' + r.by + ')'; }).join('; ') + '.');
      var narrow = w < 440, ml = narrow ? 112 : 150, mr = 70, mt = 22, mb = 30, pw = w - ml - mr, rh = (h - mt - mb) / ROWS.length, MAX = 22;
      var X = function (g) { return ml + g / MAX * pw; }, root = el('g', { 'class': 'gf-chart' }, svg);
      [0, 5, 10, 15, 20].forEach(function (g) { el('line', { 'class': 'grid', x1: X(g), x2: X(g), y1: mt, y2: h - mb }, root); el('text', { 'class': 'gf-svg-t', x: X(g), y: h - mb + 15, 'text-anchor': 'middle' }, root, String(g)); });
      el('text', { 'class': 'gf-svg-t ink', x: ml + pw + mr - 4, y: h - 2, 'text-anchor': 'end' }, root, 'gates saved →');
      el('text', { 'class': 'gf-svg-t strong', x: 4, y: 12 }, root, 'field · baseline → circuit');
      ROWS.forEach(function (r, i) {
        var y = mt + (i + 0.5) * rh, ak = r.by === 'Aska', sv = r.base - r.c, bw = Math.min(18, rh * 0.5);
        var g = el('g', { 'class': 'pt', tabindex: 0, role: 'img', 'aria-label': r.f + ', ' + r.by + ': ' + r.base + ' to ' + r.c + ' gates, ' + (sv ? sv + ' saved' : 'equal, no gain claimed') }, root);
        el('rect', { 'class': 'hit', x: 0, y: y - rh / 2, width: w, height: rh }, g);
        if (ak) el('line', { x1: 2, x2: 2, y1: y - rh * 0.38, y2: y + rh * 0.38, stroke: 'var(--hair)', 'stroke-width': 2 }, g);
        el('text', { 'class': 'gf-svg-t' + (ak ? ' strong' : ' ink'), x: 10, y: y - 2 }, g, narrow ? r.f : r.f + ' · ' + r.by);
        el('text', { 'class': 'gf-svg-t', x: 10, y: y + 11 }, g, (narrow ? r.by + ' ' : '') + r.base + '→' + r.c);
        if (sv > 0) {
          var x1 = X(sv), r4 = Math.min(4, (x1 - ml) / 2);
          el('path', { d: 'M' + ml + ',' + (y - bw / 2) + 'H' + (x1 - r4) + 'q' + r4 + ',0 ' + r4 + ',' + r4 + 'V' + (y + bw / 2 - r4) + 'q0,' + r4 + ' ' + (-r4) + ',' + r4 + 'H' + ml + 'z', fill: 'var(--mk)' }, g);
          el('text', { 'class': 'gf-svg-t strong', x: x1 + 6, y: y + 4 }, g, sv + ' (' + (100 * sv / r.base).toFixed(1) + '%)');
        } else {
          el('line', { x1: ml, x2: ml, y1: y - bw / 2, y2: y + bw / 2, stroke: 'var(--ink-3)', 'stroke-width': 2 }, g);
          el('text', { 'class': 'gf-svg-t', x: ml + 6, y: y + 4 }, g, '0 · equal');
        }
        var html = '<div class="tip-k">' + r.f + ' · ' + r.by + '</div><div class="tip-t">' + r.c + ' gates</div><div class="tip-note">baseline ' + r.base + (sv ? ' · ' + sv + ' fewer (' + (100 * sv / r.base).toFixed(1) + '%)' : ' · equal, no gain claimed') + '</div>';
        g.addEventListener('pointermove', function (ev) { F0.tip.show(html, ev.clientX, ev.clientY); });
        g.addEventListener('pointerleave', function () { F0.tip.hide(); });
        g.addEventListener('focus', function () { tipAt(html, g); });
        g.addEventListener('blur', function () { F0.tip.hide(); });
      });
    }
    fitSvg(svg, draw);
    var btn = $('#ak-run'), res = $('#ak-res');
    btn.addEventListener('click', function () {
      btn.disabled = true; res.classList.remove('done');
      var list = [['f9', 'GF(2<sup>9</sup>)'], ['f10', 'GF(2<sup>10</sup>)'], ['f11', 'GF(2<sup>11</sup>)']], outs = [], total = 0, bad = 0, ms = 0;
      (function next(i) {
        if (i >= list.length) {
          res.classList.add('done'); btn.disabled = false;
          res.innerHTML = '<b>' + fmt(total - bad) + ' / ' + fmt(total) + '</b> products correct, ' + bad + ' failures, in ' + (ms / 1000).toFixed(2) + ' s. ' + outs.join(' · ');
          return;
        }
        var c = decode(CIR[list[i][0]], 2 * CIR[list[i][0]].m);
        checkMult(c, {
          chunk: c.m >= 11 ? 64 : 256,
          progress: function (a, n) { res.innerHTML = 'Checking ' + list[i][1] + ': ' + Math.round(100 * a / n) + '%&hellip;'; },
          done: function (b, t, dt) { total += t; bad += b; ms += dt; outs.push(list[i][1] + ': ' + c.n + ' gates, ' + fmt(t) + ' pairs, ' + b + ' wrong'); next(i + 1); }
        });
      })(0);
    });
  })();
})();
