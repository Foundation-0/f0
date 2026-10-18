/* Maxwell's point charges (research/maxwell-charges): two figures.
   Hero: the certified equilibria of four configurations (equilibria.json, written from the physics0 certificates),
   drawn in 3D; drag or arrow keys turn it, the slider zooms by up to 10,000 times. "Search again here" runs a
   numerical search from scratch in the browser (Newton's method from many starting points) and compares what it
   finds with the certified list; "Hide one point" removes one point from the list so the comparison must fail.
   01: the scoreboard, most equilibria known against Maxwell's (n - 1)^2, from the table in the page.
   Nothing moves on its own. */
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
  function sig(x, d) { if (x === 0) return '0'; var s = Number(x).toPrecision(d || 4); return s.indexOf('e') >= 0 ? Number(s).toExponential(2).replace('-', '−') : String(Number(s)).replace('-', '−'); }
  function now() { return (window.performance && performance.now) ? performance.now() : Date.now(); }
  var WORD = { 3: 'Three', 4: 'Four', 5: 'Five', 6: 'Six' };

  /* =========================================================================
     HERO: the certified equilibria in 3D
     ========================================================================= */
  (function viewer() {
    var cv = $('#mv-cv'); if (!cv) return;
    var C = F0.canvas(cv), ctx = C.ctx;
    var seg = $('#mv-n'), zoom = $('#mv-zoom'), zout = $('#mv-zout'), cap = $('#mv-cap'), scaleLbl = $('#mv-scale');
    var msg = $('#mv-msg'), btnCheck = $('#mv-check'), btnBreak = $('#mv-break');
    var DATA = null, cfg = null, yaw = -0.55, pitch = 0.42, z = 0, hidden = -1, hov = null, drawn = [];

    function rot(p) {
      var cy = Math.cos(yaw), sy = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch);
      var x1 = cy * p[0] - sy * p[1], y1 = sy * p[0] + cy * p[1], z1 = p[2];
      return [x1, cp * y1 - sp * z1, sp * y1 + cp * z1]; // screen x, depth, screen up
    }
    function viewR() { return 1.2 / Math.pow(10, z); }
    function siteR(q) { return Math.max(2.5, Math.min(6, 3 + 3 * (1 + Math.log(q) / Math.LN10 / 14))); }

    function draw() {
      if (!cfg || !C.ready) return;
      var w = C.w, h = C.h, R = viewR(), s = (Math.min(w, h) / 2 - 14) / R, cx = w / 2, cy = h / 2;
      ctx.clearRect(0, 0, w, h);
      function scr(p) { var r = rot(p); return [cx + r[0] * s, cy - r[2] * s, r[1]]; }
      // context: the triangle's edges and its axis
      ctx.lineWidth = 1; ctx.strokeStyle = F0.css('--grid');
      var T = cfg.sites.slice(0, 3).map(scr);
      ctx.beginPath(); ctx.moveTo(T[0][0], T[0][1]); ctx.lineTo(T[1][0], T[1][1]); ctx.lineTo(T[2][0], T[2][1]); ctx.closePath(); ctx.stroke();
      var a0 = scr([0, 0, -1.5 * R]), a1 = scr([0, 0, 1.5 * R]);
      ctx.setLineDash([3, 4]); ctx.beginPath(); ctx.moveTo(a0[0], a0[1]); ctx.lineTo(a1[0], a1[1]); ctx.stroke(); ctx.setLineDash([]);
      var items = [];
      cfg.sites.forEach(function (p, i) { var q = scr(p); items.push({ kind: 's', i: i, x: q[0], y: q[1], d: q[2], p: p }); });
      cfg.equilibria.forEach(function (e, i) { var q = scr(e); items.push({ kind: e[3] === 1 ? 'e1' : 'e2', i: i, x: q[0], y: q[1], d: q[2], p: e, hid: i === hidden }); });
      items.sort(function (a, b) { return b.d - a.d; });
      var dig = F0.css('--mark-dig'), bio = F0.css('--mark-bio'), ink = F0.css('--ink'), bg = F0.css('--bg-1'), m = 6, shown = 0;
      drawn = [];
      items.forEach(function (it) {
        if (it.x < -m || it.x > w + m || it.y < -m || it.y > h + m) return;
        drawn.push(it);
        if (it.kind === 's') {
          var r = siteR(cfg.charges_float[it.i]);
          ctx.fillStyle = bg; ctx.beginPath(); ctx.arc(it.x, it.y, r + 1.5, 0, 7); ctx.fill();
          ctx.fillStyle = ink; ctx.beginPath(); ctx.arc(it.x, it.y, r, 0, 7); ctx.fill();
          return;
        }
        shown++;
        if (it.hid) { ctx.strokeStyle = F0.css('--hair'); ctx.lineWidth = 1.5; ctx.setLineDash([2, 2]); ctx.beginPath(); ctx.arc(it.x, it.y, 6, 0, 7); ctx.stroke(); ctx.setLineDash([]); return; }
        if (it.kind === 'e1') { ctx.fillStyle = bg; ctx.beginPath(); ctx.arc(it.x, it.y, 5.5, 0, 7); ctx.fill(); ctx.fillStyle = dig; ctx.beginPath(); ctx.arc(it.x, it.y, 4, 0, 7); ctx.fill(); }
        else { ctx.strokeStyle = bg; ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(it.x, it.y, 4.5, 0, 7); ctx.stroke(); ctx.strokeStyle = bio; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(it.x, it.y, 4.5, 0, 7); ctx.stroke(); }
      });
      if (hov) { ctx.strokeStyle = F0.css('--focus'); ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(hov.x, hov.y, 8.5, 0, 7); ctx.stroke(); }
      scaleLbl.textContent = 'view radius ' + sig(R, 2) + ' · ' + shown + ' of ' + cfg.count + ' in view';
    }

    function setCfg(id) {
      cfg = DATA.configs.filter(function (c) { return c.id === id; })[0];
      hidden = btnBreak.getAttribute('aria-pressed') === 'true' ? pickHidden() : -1;
      $$('button', seg).forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-c') === id)); });
      var extra = { n3: 'The one 1-saddle is at the centre.', n4: 'Zoom to about ×10 to see the six points around the tiny centre charge.',
        n5: 'Zoom to about ×40 to see 18 of them packed around the centre; the innermost three need about ×1,000.', n6: 'Zoom to about ×5,000 to see the six points around the tiny centre charge.' }[id];
      cap.textContent = WORD[cfg.n] + ' charges: ' + cfg.count + ' equilibria, ' + cfg.m1 + ' of them 1-saddles and ' + cfg.m2 + ' 2-saddles. Maxwell’s bound for ' + WORD[cfg.n].toLowerCase() + ' charges is ' + cfg.maxwell + '. ' + extra;
      cv.setAttribute('aria-label', WORD[cfg.n] + ' charges and their ' + cfg.count + ' certified equilibria (' + cfg.m1 + ' 1-saddles, ' + cfg.m2 + ' 2-saddles), drawn in three dimensions. Arrow keys turn the picture; plus and minus zoom.');
      msg.className = 'mv-check'; msg.textContent = 'Press “Search again here” to look for equilibria from scratch in your browser and compare with the certified list.';
      draw();
    }
    function setZoom(v) {
      z = Math.max(0, Math.min(4, v)); zoom.value = z;
      var f = Math.pow(10, z); zout.textContent = '×' + fmt(f < 10 ? Math.round(f * 10) / 10 : Math.round(Number(f.toPrecision(2))));
      draw();
    }
    function pickHidden() { // a point from the inner cluster, where a search is most likely to miss something
      var best = -1, br = Infinity;
      cfg.equilibria.forEach(function (e, i) { var r = Math.hypot(e[0], e[1], e[2]); if (r > 0 && r < br) { br = r; best = i; } });
      return best;
    }

    /* ---- numerical search in the browser (not a proof) ---- */
    function rng(seed) { return function () { seed |= 0; seed = seed + 0x6D2B79F5 | 0; var t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
    function gradHess(x, A, Q) {
      var g = [0, 0, 0], H = [0, 0, 0, 0, 0, 0, 0, 0, 0], fs = 0, rmin = Infinity;
      for (var i = 0; i < A.length; i++) {
        var d0 = x[0] - A[i][0], d1 = x[1] - A[i][1], d2 = x[2] - A[i][2], r2 = d0 * d0 + d1 * d1 + d2 * d2, r = Math.sqrt(r2);
        var i3 = Q[i] / (r2 * r), i5 = Q[i] / (r2 * r2 * r), d = [d0, d1, d2];
        rmin = Math.min(rmin, r); fs += Q[i] / r2;
        for (var k = 0; k < 3; k++) { g[k] -= i3 * d[k]; for (var l = 0; l < 3; l++) H[3 * k + l] += 3 * i5 * d[k] * d[l] - (k === l ? i3 : 0); }
      }
      return { g: g, H: H, fs: fs, rmin: rmin };
    }
    function solve3(H, g) {
      var a = H[0], b = H[1], c = H[2], d = H[3], e = H[4], f = H[5], gg = H[6], h = H[7], k = H[8];
      var det = a * (e * k - f * h) - b * (d * k - f * gg) + c * (d * h - e * gg);
      if (!isFinite(det) || Math.abs(det) < 1e-300) return null;
      return [((e * k - f * h) * g[0] + (c * h - b * k) * g[1] + (b * f - c * e) * g[2]) / det,
              ((f * gg - d * k) * g[0] + (a * k - c * gg) * g[1] + (c * d - a * f) * g[2]) / det,
              ((d * h - e * gg) * g[0] + (b * gg - a * h) * g[1] + (a * e - b * d) * g[2]) / det];
    }
    function search(c) {
      var A = c.sites, Q = c.charges_float, n = A.length, R = rng(20261018), seeds = [], i, j;
      function dirichlet() { var w = [], s = 0; for (var k = 0; k < n; k++) { var u = -Math.log(Math.max(1e-12, R())); w.push(u * u); s += u * u; } return w.map(function (v) { return v / s; }); }
      for (i = 0; i < 500; i++) { var w = dirichlet(), p = [0, 0, 0]; for (j = 0; j < n; j++) for (var k = 0; k < 3; k++) p[k] += w[j] * A[j][k]; seeds.push(p); }
      for (i = 0; i < n; i++) {
        var dm = Infinity; for (j = 0; j < n; j++) if (j !== i) dm = Math.min(dm, Math.hypot(A[i][0] - A[j][0], A[i][1] - A[j][1], A[i][2] - A[j][2]));
        for (k = 0; k < 120; k++) {
          var u = [R() - .5, R() - .5, R() - .5], un = Math.hypot(u[0], u[1], u[2]) || 1, rr = dm * Math.pow(10, -5 + 4.95 * R());
          seeds.push([A[i][0] + u[0] / un * rr, A[i][1] + u[1] / un * rr, A[i][2] + u[2] / un * rr]);
        }
        for (j = i + 1; j < n; j++) {
          var t0 = Math.sqrt(Q[i]) / (Math.sqrt(Q[i]) + Math.sqrt(Q[j]));
          for (k = 0; k < 12; k++) { var t = Math.min(1 - 1e-9, Math.max(1e-9, k < 6 ? t0 * Math.pow(10, -R()) : 1 - (1 - t0) * Math.pow(10, -R()))); seeds.push([A[i][0] + t * (A[j][0] - A[i][0]), A[i][1] + t * (A[j][1] - A[i][1]), A[i][2] + t * (A[j][2] - A[i][2])]); }
        }
      }
      // centroids of the whole set and of every three sites, at distances spread over five decades
      var cents = [], ii, jj, kk;
      function cen(ids) { var p = [0, 0, 0]; ids.forEach(function (t) { for (var q = 0; q < 3; q++) p[q] += A[t][q] / ids.length; }); return p; }
      cents.push(cen(A.map(function (a_, t) { return t; })));
      for (ii = 0; ii < n; ii++) for (jj = ii + 1; jj < n; jj++) for (kk = jj + 1; kk < n; kk++) cents.push(cen([ii, jj, kk]));
      var span = 0; for (ii = 0; ii < n; ii++) for (jj = 0; jj < n; jj++) span = Math.max(span, Math.hypot(A[ii][0] - A[jj][0], A[ii][1] - A[jj][1], A[ii][2] - A[jj][2]));
      cents.forEach(function (c0) { for (var q = 0; q < 60; q++) { var v = [R() - .5, R() - .5, R() - .5], vn = Math.hypot(v[0], v[1], v[2]) || 1, rr = span * Math.pow(10, -5 + 4.5 * R()); seeds.push([c0[0] + v[0] / vn * rr, c0[1] + v[1] / vn * rr, c0[2] + v[2] / vn * rr]); } });
      var found = [];
      function polish(x) {
        for (var it = 0; it < 70; it++) {
          var G = gradHess(x, A, Q), st = solve3(G.H, G.g); if (!st) return;
          var sn = Math.hypot(st[0], st[1], st[2]), f = Math.min(1, 0.5 * G.rmin / (sn || 1e-300));
          x = [x[0] - f * st[0], x[1] - f * st[1], x[2] - f * st[2]];
          if (!isFinite(x[0])) return;
        }
        var G2 = gradHess(x, A, Q);
        if (Math.hypot(G2.g[0], G2.g[1], G2.g[2]) > 1e-9 * G2.fs || G2.rmin < 1e-9) return;
        for (var m = 0; m < found.length; m++) if (Math.hypot(x[0] - found[m].x[0], x[1] - found[m].x[1], x[2] - found[m].x[2]) < 1e-6 * Math.min(G2.rmin, found[m].rmin)) return;
        found.push({ x: x, rmin: G2.rmin });
      }
      seeds.forEach(polish);
      // second round: start again close to every point found, at three scales, to catch near neighbours
      var first = found.slice(), extra = 0;
      first.forEach(function (f) { [0.3, 0.03, 0.003].forEach(function (sc) { for (var q = 0; q < 8; q++) { var v = [R() - .5, R() - .5, R() - .5], vn = Math.hypot(v[0], v[1], v[2]) || 1; polish([f.x[0] + v[0] / vn * sc * f.rmin, f.x[1] + v[1] / vn * sc * f.rmin, f.x[2] + v[2] / vn * sc * f.rmin]); extra++; } }); });
      return { found: found, seeds: seeds.length + extra };
    }
    function runCheck() {
      if (!cfg) return;
      btnCheck.disabled = true; msg.className = 'mv-check'; msg.textContent = 'Searching…';
      setTimeout(function () {
        var t0 = now(), res = search(cfg), ms = now() - t0;
        var list = cfg.equilibria.filter(function (e, i) { return i !== hidden; });
        var used = list.map(function () { return false; }), extra = [];
        res.found.forEach(function (f) {
          var hit = -1;
          list.forEach(function (e, i) { if (Math.hypot(f.x[0] - e[0], f.x[1] - e[1], f.x[2] - e[2]) < 1e-6 * f.rmin + 1e-12) hit = i; });
          if (hit >= 0) used[hit] = true; else extra.push(f);
        });
        var nUsed = used.filter(Boolean).length;
        if (extra.length) {
          var e = extra[0].x;
          msg.className = 'mv-check bad';
          msg.innerHTML = '<b>Mismatch.</b> The search found ' + res.found.length + ' equilibria, and ' + extra.length + ' of them ' + (extra.length === 1 ? 'is' : 'are') + ' not on the list: one at (' + sig(e[0], 3) + ', ' + sig(e[1], 3) + ', ' + sig(e[2], 3) + '). A list with a point missing fails; the real check, verify_arb.py, rejects it the same way.';
        } else if (nUsed === list.length) {
          msg.className = 'mv-check ok';
          msg.innerHTML = '<b>' + nUsed + ' of ' + list.length + '</b> certified equilibria found again from scratch in your browser, and none that is not on the list (' + fmt(res.seeds) + ' starting points, ' + Math.round(ms) + ' ms). This search is numerical; the certificate is the proof.';
        } else {
          msg.className = 'mv-check';
          msg.innerHTML = 'Found <b>' + nUsed + ' of ' + list.length + '</b> certified equilibria and nothing off the list (' + fmt(res.seeds) + ' starting points). A numerical search can miss points; the certificate cannot.';
        }
        btnCheck.disabled = false;
      }, 30);
    }

    /* ---- interaction ---- */
    function nearest(px, py) {
      var best = null, bd = 100;
      drawn.forEach(function (it) { var d = (it.x - px) * (it.x - px) + (it.y - py) * (it.y - py); if (d < bd) { bd = d; best = it; } });
      return best;
    }
    function tipFor(it) {
      var p = it.p, r = Math.hypot(p[0], p[1], p[2]);
      if (it.kind === 's') return '<div class="tip-k">Charge</div><div class="tip-t">strength ' + F0.esc(cfg.charges[it.i]) + '</div><div class="tip-rows"><div class="tip-row"><span>position</span><span class="tip-v">(' + sig(p[0], 3) + ', ' + sig(p[1], 3) + ', ' + sig(p[2], 3) + ')</span></div></div>';
      return '<div class="tip-k">' + (it.hid ? 'Hidden from the list' : 'Certified equilibrium') + '</div><div class="tip-t">' + (it.kind === 'e1' ? '1-saddle: escapes along one line' : '2-saddle: escapes across a plane') + '</div>' +
        '<div class="tip-rows"><div class="tip-row"><span>distance from centre</span><span class="tip-v">' + sig(r, 4) + '</span></div><div class="tip-row"><span>position</span><span class="tip-v">(' + sig(p[0], 3) + ', ' + sig(p[1], 3) + ', ' + sig(p[2], 3) + ')</span></div></div>';
    }
    var dragging = null;
    cv.addEventListener('pointerdown', function (e) { dragging = { x: e.clientX, y: e.clientY, yaw: yaw, pitch: pitch }; cv.setPointerCapture(e.pointerId); cv.classList.add('drag'); F0.tip.hide(true); });
    cv.addEventListener('pointermove', function (e) {
      var b = cv.getBoundingClientRect();
      if (dragging) {
        yaw = dragging.yaw + (e.clientX - dragging.x) * 0.01;
        pitch = Math.max(-1.5, Math.min(1.5, dragging.pitch + (e.clientY - dragging.y) * 0.01));
        hov = null; draw(); return;
      }
      var it = nearest(e.clientX - b.left, e.clientY - b.top);
      if (it !== hov) { hov = it; draw(); }
      if (it) F0.tip.show(tipFor(it), e.clientX, e.clientY); else F0.tip.hide();
    });
    function endDrag(e) { if (dragging) { dragging = null; cv.classList.remove('drag'); try { cv.releasePointerCapture(e.pointerId); } catch (x) { /* already released */ } } }
    cv.addEventListener('pointerup', endDrag);
    cv.addEventListener('pointercancel', endDrag);
    cv.addEventListener('pointerleave', function () { if (!dragging) { hov = null; F0.tip.hide(); draw(); } });
    cv.addEventListener('wheel', function (e) { if (!e.ctrlKey && !e.metaKey) return; e.preventDefault(); setZoom(z - Math.sign(e.deltaY) * 0.1); }, { passive: false });
    cv.addEventListener('keydown', function (e) {
      var k = e.key, used = true;
      if (k === 'ArrowLeft') yaw -= 0.12; else if (k === 'ArrowRight') yaw += 0.12;
      else if (k === 'ArrowUp') pitch = Math.max(-1.5, pitch - 0.12); else if (k === 'ArrowDown') pitch = Math.min(1.5, pitch + 0.12);
      else if (k === '+' || k === '=') { setZoom(z + 0.25); return e.preventDefault(); }
      else if (k === '-' || k === '_') { setZoom(z - 0.25); return e.preventDefault(); }
      else if (k === 'Home') { yaw = -0.55; pitch = 0.42; setZoom(0); }
      else used = false;
      if (used) { e.preventDefault(); draw(); }
    });
    cv.addEventListener('blur', function () { F0.tip.hide(true); });
    seg.addEventListener('click', function (e) { var b = e.target.closest('button[data-c]'); if (b) setCfg(b.getAttribute('data-c')); });
    zoom.addEventListener('input', function () { setZoom(+zoom.value); });
    btnCheck.addEventListener('click', runCheck);
    btnBreak.addEventListener('click', function () {
      var on = btnBreak.getAttribute('aria-pressed') !== 'true';
      btnBreak.setAttribute('aria-pressed', String(on));
      hidden = on ? pickHidden() : -1;
      msg.className = 'mv-check';
      msg.textContent = on ? 'One point (dashed red) is now left off the list. Press “Search again here”: the comparison should fail.' : 'The list is complete again.';
      draw();
    });
    C.resize(draw);
    F0.onTheme(draw);
    F0.json('equilibria.json').then(function (d) { DATA = d; setCfg('n5'); setZoom(0); }).catch(function (e) { console.warn('equilibria.json:', e); });
  })();

  /* =========================================================================
     01: the scoreboard
     ========================================================================= */
  (function scoreboard() {
    var svg = $('#sb-svg'); if (!svg) return;
    var cap = $('#sb-cap'), rows = $$('#sb-rows tr');
    // n, Maxwell's bound, most known, this study?, upper end of the open range, status from the table
    var DATA = rows.map(function (tr) {
      var td = tr.querySelectorAll('td'), n = +tr.querySelector('th').textContent;
      // a red ring marks a new count from this study (at five charges the count 24 is Arathoon, Ball and Kvalheim's)
      return { n: n, bound: +td[0].textContent, known: +td[1].textContent, note: td[2].textContent, ours: /this study/.test(td[2].textContent) && !/Arathoon/.test(td[2].textContent), hi: n === 3 ? 6 : null };
    });
    var cur = -1, pts = [];
    function fit(draw) {
      var st = svg.parentNode, last = '';
      function go() {
        var r = st.getBoundingClientRect(), w = Math.max(240, Math.round(r.width)), h = Math.max(140, Math.round(r.height));
        var key = w + 'x' + h; if (key === last) return; last = key;
        svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h); draw(w, h);
      }
      if ('ResizeObserver' in window) new ResizeObserver(go).observe(st); else window.addEventListener('resize', go);
      go();
    }
    function render(w, h) {
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      var g = el('g', { 'class': 'sb' }, svg), L = 44, Rm = 18, T = 26, B = 34, iw = w - L - Rm, ih = h - T - B;
      var ymax = 70, X = function (n) { return L + (n - 2 + 0.5) / DATA.length * iw; }, Y = function (v) { return T + ih - v / ymax * ih; };
      [0, 20, 40, 60].forEach(function (v) { el('line', { 'class': 'grid', x1: L, x2: L + iw, y1: Y(v), y2: Y(v) }, g); el('text', { 'class': 'sb-t', x: L - 8, y: Y(v) + 4, 'text-anchor': 'end' }, g, String(v)); });
      el('line', { 'class': 'axis', x1: L, x2: L + iw, y1: Y(0), y2: Y(0) }, g);
      DATA.forEach(function (d) { el('text', { 'class': 'sb-t ink', x: X(d.n), y: Y(0) + 18, 'text-anchor': 'middle' }, g, String(d.n)); });
      el('text', { 'class': 'sb-t', x: L + iw, y: Y(0) + 30, 'text-anchor': 'end' }, g, 'charges →');
      el('text', { 'class': 'sb-t', x: L, y: T - 8, 'text-anchor': 'start' }, g, 'equilibria ↑');
      DATA.forEach(function (d) { if (d.known > d.bound) el('rect', { 'class': 'above', x: X(d.n) - 7, y: Y(d.known), width: 14, height: Y(d.bound) - Y(d.known) }, g); });
      el('polyline', { 'class': 'bound', points: DATA.map(function (d) { return X(d.n) + ',' + Y(d.bound); }).join(' ') }, g);
      var lastD = DATA[DATA.length - 1];
      el('text', { 'class': 'sb-t', x: X(lastD.n) - 10, y: Y(lastD.bound) - 10, 'text-anchor': 'end' }, g, 'Maxwell (n − 1)²');
      pts = [];
      DATA.forEach(function (d, i) {
        var p = el('g', { 'class': 'pt' + (i === cur ? ' cur' : '') }, g), x = X(d.n);
        el('rect', { 'class': 'bsq', x: x - 3.5, y: Y(d.bound) - 3.5, width: 7, height: 7 }, p);
        if (d.hi) { el('line', { 'class': 'range', x1: x, x2: x, y1: Y(d.known), y2: Y(d.hi) }, p); el('line', { 'class': 'range', x1: x - 5, x2: x + 5, y1: Y(d.hi), y2: Y(d.hi) }, p); el('text', { 'class': 'sb-t', x: x, y: Y(d.hi) - 9, 'text-anchor': 'middle' }, p, 'at most 6'); }
        el('circle', { 'class': 'known', cx: x, cy: Y(d.known), r: 4 }, p);
        if (d.ours) el('circle', { 'class': 'ours', cx: x, cy: Y(d.known), r: 7.5 }, p);
        if (d.known !== d.bound || d.ours) el('text', { 'class': 'sb-t strong', x: x + 11, y: Y(d.known) + 4 }, p, String(d.known));
        el('circle', { 'class': 'hit', cx: x, cy: Y(Math.max(d.known, d.bound)), r: 14 }, p);
        p.addEventListener('pointerenter', function (e) { show(i, e.clientX, e.clientY); });
        p.addEventListener('pointermove', function (e) { show(i, e.clientX, e.clientY); });
        p.addEventListener('pointerleave', function () { F0.tip.hide(); });
        pts.push(p);
      });
    }
    function tip(d) {
      return '<div class="tip-k">' + d.n + ' charges</div><div class="tip-t">most known: ' + d.known + (d.hi ? ' (true maximum between 4 and 6)' : '') + '</div>' +
        '<div class="tip-rows"><div class="tip-row"><span>Maxwell’s bound</span><span class="tip-v">' + d.bound + '</span></div></div><div class="tip-note">' + F0.esc(d.note) + '</div>';
    }
    function show(i, x, y) { F0.tip.show(tip(DATA[i]), x, y); }
    function focusPt(i) {
      cur = Math.max(0, Math.min(DATA.length - 1, i));
      pts.forEach(function (p, j) { p.setAttribute('class', 'pt' + (j === cur ? ' cur' : '')); });
      var b = pts[cur].getBoundingClientRect(); show(cur, b.left + b.width / 2, b.top + b.height / 2);
      var d = DATA[cur]; cap.textContent = d.n + ' charges: Maxwell’s bound ' + d.bound + ', most known ' + d.known + '. ' + d.note;
    }
    svg.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight' || e.key === 'ArrowUp') { focusPt(cur + 1); e.preventDefault(); }
      else if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') { focusPt(cur < 0 ? 0 : cur - 1); e.preventDefault(); }
      else if (e.key === 'Home') { focusPt(0); e.preventDefault(); } else if (e.key === 'End') { focusPt(DATA.length - 1); e.preventDefault(); }
    });
    svg.addEventListener('focus', function () { if (cur < 0) focusPt(3); });
    svg.addEventListener('blur', function () { F0.tip.hide(true); });
    fit(render);
  })();
})();
